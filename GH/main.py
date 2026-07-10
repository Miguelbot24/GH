"""
Módulo: main.py
Sprint 7 — Punto de entrada de la aplicación Gestión Hospitalaria (GH).

Orquesta todos los módulos del sistema: inicializa el modelo de datos
(generador, repositorio, monitor, notificador, simulador), construye la
interfaz gráfica (pantalla de inicio, panel de salas, panel de emergencias,
detalle de paciente) y conecta los observadores entre capas.

Ejecutar este archivo lanza la aplicación completa:
    python main.py

Dependencias previas necesarias:
    - Todos los módulos de los Sprints 0 al 6.

Librerías externas requeridas:
    - customtkinter  (pip install customtkinter)
    - pillow         (pip install pillow)
"""

import sys
import os

# Aseguramos que el directorio GH/ esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
import random
from datetime import datetime, timedelta
from tkinter import filedialog

from config import (
    TEMA_APARIENCIA,
    TEMA_COLOR,
    ANCHO_VENTANA,
    ALTO_VENTANA,
    COLOR_CRITICO,
    COLOR_ESTABLE,
    SALAS_HOSPITAL,
    PACIENTES_POR_SALA,
    INTERVALO_MONITOREO_MS,
    TIPO_EGRESO_ALTA,
    TIPO_EGRESO_FUGA,
    ESTADO_ATENCION,
)

# --- Capa de modelos ---
from modelos.signos_vitales import SignosVitales
from modelos.paciente_sala import PacienteSala
from modelos.paciente_emergencia import PacienteEmergencia

# --- Capa de datos ---
from datos.generador import GeneradorDatos
from datos.repositorio import RepositorioPacientes

# --- Capa de alertas ---
from alertas.monitor import MonitorSignos, CambioEstado
from alertas.notificador import Notificador, Alerta
from alertas.simulador import SimuladorEmergencia, ESCENARIOS_EMERGENCIA

# --- Capa de interfaz ---
from interfaz.pantalla_inicio import PantallaInicio
from interfaz.panel_salas import PanelSalas
from interfaz.panel_emergencias import PanelEmergencias
from interfaz.panel_egresos import PanelEgresos
from interfaz.detalle_paciente import DetallePaciente

# --- Capa de utilidades ---
from utilidades.exportador_pdf import ExportadorPDF


class AplicacionGH:
    """
    Clase principal que orquesta toda la aplicación Gestión Hospitalaria.

    Responsabilidades:
      - Crear la ventana principal y configurar el tema visual.
      - Instanciar los componentes del modelo (generador, repositorio,
        monitor, notificador, simulador).
      - Instanciar los paneles de la interfaz gráfica.
      - Conectar las capas mediante el patrón Observer.
      - Gestionar la navegación entre pantallas.
      - Proveer el botón "Simular Emergencia" integrado.
      - Iniciar el bucle de simulación periódica (ticks del monitor).
    """

    def __init__(self):
        """Constructor: inicializa CustomTkinter y construye toda la app."""
        # ── Configurar apariencia de CustomTkinter ──
        ctk.set_appearance_mode(TEMA_APARIENCIA)
        ctk.set_default_color_theme(TEMA_COLOR)

        # ── Crear ventana principal ──
        self._ventana = ctk.CTk()
        self._ventana.title("Gestión Hospitalaria — GH")
        self._ventana.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}")
        self._ventana.minsize(1000, 650)

        # Al cerrar la ventana, detenemos la simulación y salimos
        self._ventana.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)

        # ── Estado interno ──
        self._simulacion_activa = False    # Controla el bucle de ticks
        self._pantalla_actual   = None     # Referencia al panel visible
        self._panel_anterior    = "salas"  # Para volver del detalle

        # ── Contenedor único para todas las pantallas ──
        self._contenedor = ctk.CTkFrame(self._ventana, fg_color="transparent")
        self._contenedor.pack(fill="both", expand=True)
        self._contenedor.grid_rowconfigure(0, weight=1)
        self._contenedor.grid_columnconfigure(0, weight=1)

        # ── Barra de navegación (se muestra/oculta según la pantalla) ──
        self._crear_barra_navegacion()

        # ── Construir capas en orden ──
        self._inicializar_modelo()
        self._inicializar_interfaz()
        self._conectar_observadores()

        # ── Comenzar con la pantalla de inicio ──
        self._mostrar("inicio")

    # ==================================================================
    # INICIALIZACIÓN DE CAPAS
    # ==================================================================
    def _inicializar_modelo(self) -> None:
        """
        Crea los componentes de la capa de negocio:
        generador de datos, repositorio, monitor, notificador y simulador.
        """
        # Generador de pacientes ficticios
        self._generador = GeneradorDatos()

        # Repositorio central de pacientes (en memoria)
        self._repositorio = RepositorioPacientes()

        # Monitor de signos vitales
        self._monitor = MonitorSignos()

        # Notificador de alertas (sonido desactivado por defecto)
        self._notificador = Notificador(sonido_activado=True)

        # Simulador de emergencias
        self._simulador = SimuladorEmergencia(
            monitor=self._monitor,
            notificador=self._notificador,
        )

        # Exportador de PDF
        self._exportador_pdf = ExportadorPDF()

    def _crear_barra_navegacion(self) -> None:
        """
        Crea la barra de navegación (SALAS / EMERGENCIAS / SIMULAR).
        Se empaqueta directamente en la ventana por encima del contenedor.
        Por defecto permanece oculta.
        """
        self._barra_navegacion = ctk.CTkFrame(
            self._ventana, fg_color="#0D0D0D", height=42
        )
        self._barra_navegacion.pack_propagate(False)

        self._btn_tab_salas = ctk.CTkButton(
            self._barra_navegacion,             text="HOSPITALIZACIÓN",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            width=130, height=32, corner_radius=6,
            fg_color=COLOR_ESTABLE, hover_color="#2E7D32",
            command=lambda: self._mostrar("salas"),
        )
        self._btn_tab_salas.pack(side="left", padx=(20, 5), pady=5)

        self._btn_tab_emergencias = ctk.CTkButton(
            self._barra_navegacion, text="EMERGENCIAS",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            width=150, height=32, corner_radius=6,
            fg_color="#444444", hover_color="#555555",
            command=lambda: self._mostrar("emergencias"),
        )
        self._btn_tab_emergencias.pack(side="left", padx=5, pady=5)

        self._btn_tab_egresos = ctk.CTkButton(
            self._barra_navegacion, text="EGRESOS",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            width=120, height=32, corner_radius=6,
            fg_color="#444444", hover_color="#555555",
            command=lambda: self._mostrar("egresos"),
        )
        self._btn_tab_egresos.pack(side="left", padx=5, pady=5)

        self._btn_simular = ctk.CTkButton(
            self._barra_navegacion, text="SIMULAR EMERGENCIA",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            width=180, height=32, corner_radius=6,
            fg_color="#D32F2F", hover_color="#B71C1C",
            command=self._on_click_simular,
        )
        self._btn_simular.pack(side="right", padx=20, pady=5)
        self._barra_navegacion.pack_forget()  # Oculta al inicio

    def _inicializar_interfaz(self) -> None:
        """
        Crea todas las pantallas como hijas del contenedor.
        Ninguna se auto-posiciona; todas se colocan en la misma celda
        del grid del contenedor para alternar con tkraise().
        """
        # ── Pantalla de inicio ──
        self._pantalla_inicio = PantallaInicio(
            self._contenedor,
            on_iniciar_callback=self._on_iniciar_sistema,
        )
        self._pantalla_inicio.grid(row=0, column=0, sticky="nsew")

        # ── Pantalla de selección ──
        self._pantalla_seleccion = ctk.CTkFrame(
            self._contenedor, fg_color="transparent"
        )
        self._pantalla_seleccion.grid(row=0, column=0, sticky="nsew")
        self._pantalla_seleccion.grid_rowconfigure(0, weight=1)
        self._pantalla_seleccion.grid_rowconfigure(1, weight=0)
        self._pantalla_seleccion.grid_rowconfigure(2, weight=1)
        self._pantalla_seleccion.grid_columnconfigure(0, weight=1)
        self._pantalla_seleccion.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self._pantalla_seleccion,
            text="SELECCIONE UN ÁREA",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#FFFFFF",
        ).grid(row=0, column=0, columnspan=2, pady=(80, 0))

        frame_botones = ctk.CTkFrame(
            self._pantalla_seleccion, fg_color="transparent"
        )
        frame_botones.grid(row=1, column=0, columnspan=2)

        ctk.CTkButton(
            frame_botones,
            text="ÁREA DE HOSPITALIZACIÓN\n\n4 Salas · 24 Pacientes\nInternación y Monitoreo",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            width=350, height=180, corner_radius=16,
            fg_color=COLOR_ESTABLE, hover_color="#2E7D32",
            text_color="#FFFFFF",
            command=lambda: self._iniciar_area("salas"),
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            frame_botones,
            text="ÁREA DE EMERGENCIAS\n\nCola de Atención\nPrioridad y Triaje",
            font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"),
            width=350, height=180, corner_radius=16,
            fg_color="#D32F2F", hover_color="#B71C1C",
            text_color="#FFFFFF",
            command=lambda: self._iniciar_area("emergencias"),
        ).pack(side="left", padx=20)

        # ── Panel de salas ──
        self._panel_salas = PanelSalas(
            self._contenedor,
            on_ver_detalle_callback=self._on_ver_detalle,
            on_volver_callback=lambda: self._mostrar("inicio"),
            on_ver_mas_callback=self._exportar_pdf,
        )
        self._panel_salas.grid(row=0, column=0, sticky="nsew")

        # ── Panel de emergencias ──
        self._panel_emergencias = PanelEmergencias(
            self._contenedor,
            on_ver_detalle_callback=self._on_ver_detalle,
            on_atender_siguiente_callback=self._on_atender_siguiente,
            on_volver_callback=lambda: self._mostrar("inicio"),
            on_marcar_fuga_callback=self._marcar_fuga,
            on_ver_mas_callback=self._exportar_pdf,
        )
        self._panel_emergencias.grid(row=0, column=0, sticky="nsew")

        # ── Panel de egresos ──
        self._panel_egresos = PanelEgresos(
            self._contenedor,
            on_volver_callback=lambda: self._mostrar("inicio"),
            on_ver_mas_callback=self._exportar_pdf,
        )
        self._panel_egresos.grid(row=0, column=0, sticky="nsew")

        # ── Detalle de paciente ──
        self._detalle_paciente = DetallePaciente(
            self._contenedor,
            on_volver_callback=self._on_volver_detalle,
            on_dar_alta_callback=self._dar_de_alta,
            on_atender_sala_callback=self._atender_paciente_sala,
        )
        self._detalle_paciente.grid(row=0, column=0, sticky="nsew")

    def _conectar_observadores(self) -> None:
        """
        Conecta los componentes mediante el patrón Observer:
          - Monitor → Notificador (cambios de estado generan alertas).
          - Notificador → GUI (alertas críticas actualizan interfaz).
          - Simulador → GUI (resultados de simulación activan parpadeo).
        """
        # El notificador escucha los cambios de estado del monitor
        self._monitor.registrar_observador(self._notificador.recibir_cambio)

        # Las alertas críticas actualizan la GUI
        self._notificador.configurar_callback_visual(self._on_alerta_gui)

        # Las simulaciones de emergencia notifican a la GUI
        self._simulador.configurar_callback_gui(self._on_simulacion_gui)

    # ==================================================================
    # NAVEGACIÓN CENTRALIZADA (tkraise)
    # ==================================================================
    def _mostrar(self, pantalla: str) -> None:
        """
        Única función de navegación. Trae al frente la pantalla indicada
        usando tkraise() sobre el contenedor común.

        Args:
            pantalla: "inicio", "seleccion", "salas", "emergencias", "detalle"
        """
        # ── Ocultar barra de navegación por defecto ──
        self._barra_navegacion.pack_forget()

        if pantalla == "inicio":
            self._pantalla_inicio.tkraise()
            self._pantalla_actual = self._pantalla_inicio
            self._detener_simulacion()

        elif pantalla == "seleccion":
            self._pantalla_seleccion.tkraise()
            self._pantalla_actual = self._pantalla_seleccion

        elif pantalla == "salas":
            self._barra_navegacion.pack(side="top", fill="x",
                                         before=self._contenedor)
            self._btn_tab_salas.configure(fg_color=COLOR_ESTABLE)
            self._btn_tab_emergencias.configure(fg_color="#444444")
            self._btn_tab_egresos.configure(fg_color="#444444")
            self._panel_anterior = "salas"
            self._panel_salas.tkraise()
            self._pantalla_actual = self._panel_salas
            self._panel_salas.refrescar_tarjetas()

        elif pantalla == "emergencias":
            self._barra_navegacion.pack(side="top", fill="x",
                                         before=self._contenedor)
            self._btn_tab_emergencias.configure(fg_color="#D32F2F")
            self._btn_tab_salas.configure(fg_color="#444444")
            self._btn_tab_egresos.configure(fg_color="#444444")
            self._panel_anterior = "emergencias"
            self._panel_emergencias.tkraise()
            self._pantalla_actual = self._panel_emergencias
            self._panel_emergencias.refrescar_tarjetas()

        elif pantalla == "egresos":
            self._barra_navegacion.pack(side="top", fill="x",
                                         before=self._contenedor)
            self._btn_tab_salas.configure(fg_color="#444444")
            self._btn_tab_emergencias.configure(fg_color="#444444")
            self._btn_tab_egresos.configure(fg_color="#FF9800")
            self._panel_anterior = "egresos"
            self._panel_egresos.tkraise()
            self._pantalla_actual = self._panel_egresos
            self._panel_egresos.cargar_pacientes(
                self._repositorio.obtener_egresos()
            )

        elif pantalla == "detalle":
            self._detalle_paciente.tkraise()
            self._pantalla_actual = self._detalle_paciente

    def _on_iniciar_sistema(self, pantalla) -> None:
        """
        Callback del botón "Iniciar Sistema".
        Genera pacientes y muestra la pantalla de selección de área.
        """
        self._repositorio.limpiar()
        pacientes_sala = self._generador.generar_pacientes_sala()
        pacientes_emerg = self._generador.generar_pacientes_emergencia()

        self._repositorio.agregar_pacientes(pacientes_sala)
        self._repositorio.agregar_pacientes(pacientes_emerg)

        self._monitor = MonitorSignos()
        self._monitor.registrar_observador(self._notificador.recibir_cambio)
        self._monitor.agregar_pacientes(self._repositorio.obtener_todos())
        self._monitor.evaluar_todos()

        self._simulador = SimuladorEmergencia(
            monitor=self._monitor, notificador=self._notificador,
        )
        self._simulador.configurar_callback_gui(self._on_simulacion_gui)

        self._panel_salas.cargar_pacientes(self._repositorio.obtener_sala())
        self._panel_emergencias.cargar_pacientes(
            self._repositorio.obtener_emergencia()
        )

        self._mostrar("seleccion")
        self._iniciar_simulacion()

        print(f"\n[GH] {self._repositorio.total_pacientes()} pacientes generados "
              f"({self._repositorio.total_sala()} sala, "
              f"{self._repositorio.total_emergencia()} emergencia)")

    def _iniciar_area(self, tipo: str) -> None:
        """Callback desde la pantalla de selección: muestra el panel elegido."""
        self._mostrar(tipo)

    def _on_ver_detalle(self, paciente) -> None:
        """Click en tarjeta: muestra detalle del paciente."""
        self._detalle_paciente.cargar_paciente(paciente)
        self._mostrar("detalle")

    def _on_volver_detalle(self) -> None:
        """Vuelve del detalle al panel anterior."""
        self._mostrar(self._panel_anterior)

    # ==================================================================
    # SIMULACIÓN DE EMERGENCIAS (SPRINT 6)
    # ==================================================================
    def _on_click_simular(self) -> None:
        """
        Acción del botón "SIMULAR EMERGENCIA" en la barra de navegación.
        Selecciona un paciente aleatorio del repositorio y aplica un
        escenario de emergencia aleatorio.
        """
        todos = self._repositorio.obtener_sala()
        if not todos:
            print("[SIMULACION] No hay pacientes en sala para simular.")
            return
        self._simulador.simular_emergencia_aleatoria(todos)

    def _on_simulacion_gui(self, resultado: dict) -> None:
        """
        Callback invocado tras cada simulación de emergencia.
        Refresca los paneles suavemente (sin reconstruir tarjetas).
        """
        self._panel_salas.refrescar_tarjetas()
        self._panel_emergencias.refrescar_tarjetas()

        paciente = resultado["paciente"]
        print(f"[SIMULACION] {resultado['escenario']} aplicado a "
              f"{paciente.nombre}: {resultado['estado_anterior']} -> "
              f"{resultado['estado_nuevo']}")

    def _on_atender_siguiente(self, paciente) -> None:
        """
        Callback del botón "Atender Siguiente" en emergencias.
        Flujo completo:
          1. Registra un examen de "Atención completada" en el historial.
          2. Restaura signos vitales a valores normales.
          3. Transfiere al paciente de emergencias a una sala de recuperación.
          4. Notifica que el médico quedó disponible para el siguiente.
        """
        from modelos.paciente_sala import PacienteSala
        from modelos.historial import Examen

        # 1. Registrar atención en el historial del paciente
        if paciente.historial:
            paciente.historial.agregar_examen(Examen(
                tipo="Atención de Emergencia",
                resultado="Completada — Paciente estabilizado",
                notas="Transferido a sala de recuperación para observación.",
            ))

        # 2. Restaurar signos vitales a valores normales
        paciente._signos_vitales = SignosVitales(
            frecuencia_cardiaca=72.0,
            frecuencia_respiratoria=16.0,
            saturacion_oxigeno=98.0,
            presion_sistolica=118.0,
            presion_diastolica=74.0,
            temperatura=36.6,
        )

        # 3. Transferir de emergencias a una sala de recuperación
        # Buscar la sala con menos pacientes actualmente
        conteo_salas = {}
        for p in self._repositorio.obtener_sala():
            sala = p.planta if hasattr(p, 'planta') else "Sala A"
            conteo_salas[sala] = conteo_salas.get(sala, 0) + 1

        # Elegir la sala con menos ocupación
        sala_destino = SALAS_HOSPITAL[0]
        for sala in SALAS_HOSPITAL:
            ocupadas = conteo_salas.get(sala["nombre"], 0)
            if ocupadas < PACIENTES_POR_SALA:
                sala_destino = sala
                break

        # Crear paciente de sala copiando los datos del de emergencia
        paciente_sala = PacienteSala(
            nombre=paciente.nombre,
            edad=paciente.edad,
            genero=paciente.genero,
            numero_cama=sala_destino["camas_inicio"] + conteo_salas.get(sala_destino["nombre"], 0),
            planta=sala_destino["nombre"],
            tipo_avatar=paciente.tipo_avatar,
        )
        # Transferir signos e historial
        paciente_sala._signos_vitales = paciente.signos_vitales.copiar()
        paciente_sala.historial = paciente.historial
        paciente_sala.historial.id_paciente = paciente_sala.id_paciente

        # Retrasar fecha de ingreso 2h: el paciente ya recorrió admisión,
        # espera y atención en emergencias. No está en observación inicial.
        paciente_sala._fecha_ingreso = datetime.now() - timedelta(hours=2)

        # Eliminar de emergencias y agregar a sala
        self._repositorio._pacientes_emergencia = [
            p for p in self._repositorio._pacientes_emergencia
            if p.id_paciente != paciente.id_paciente
        ]
        self._repositorio._pacientes_sala.append(paciente_sala)

        # Remover del monitor el paciente viejo, agregar el nuevo
        try:
            self._monitor.remover_paciente(paciente.id_paciente)
        except KeyError:
            pass
        self._monitor.agregar_paciente(paciente_sala)
        self._monitor.evaluar_todos()

        # 4. Notificar en el panel
        self._panel_emergencias.panel_notificaciones.agregar_notificacion(
            f"TRANSFERENCIA: {paciente.nombre} -> {sala_destino['nombre']} "
            f"(cama {paciente_sala.numero_cama}).\n"
            f"El paciente ya cuenta con resultados en su examen de laboratorio.",
            tipo="ATENCION",
        )

        # Refrescar ambos paneles
        self._panel_emergencias.cargar_pacientes(
            self._repositorio.obtener_emergencia()
        )
        self._panel_salas.cargar_pacientes(self._repositorio.obtener_sala())

    # ==================================================================
    # GESTIÓN DE EGRESOS (SPRINT 7)
    # ==================================================================
    def _dar_de_alta(self, paciente) -> None:
        """
        Marca a un paciente como DADO_DE_ALTA y lo mueve al área de egresos.
        Esperado para pacientes que están en sala (hospitalización).

        Args:
            paciente: Instancia de PacienteSala a dar de alta.
        """
        try:
            self._monitor.remover_paciente(paciente.id_paciente)
        except KeyError:
            pass

        egresado = self._repositorio.marcar_egreso(
            paciente.id_paciente, TIPO_EGRESO_ALTA
        )

        # Actualizar panel de salas (ya no tiene al paciente)
        self._panel_salas.cargar_pacientes(self._repositorio.obtener_sala())

        print(f"[EGRESO] {egresado.nombre} dado de alta ({egresado.tipo_egreso})")

        # Volver al panel de salas después del alta
        self._mostrar("salas")

    def _marcar_fuga(self, paciente) -> None:
        """
        Marca a un paciente de emergencias como FUGADO y lo mueve a egresos.
        Esperado para pacientes que abandonan el área de emergencias
        sin completar su atención.

        Args:
            paciente: Instancia de PacienteEmergencia a marcar como fugado.
        """
        try:
            self._monitor.remover_paciente(paciente.id_paciente)
        except KeyError:
            pass

        egresado = self._repositorio.marcar_egreso(
            paciente.id_paciente, TIPO_EGRESO_FUGA
        )

        # Actualizar panel de emergencias (ya no tiene al paciente)
        self._panel_emergencias.cargar_pacientes(
            self._repositorio.obtener_emergencia()
        )

        print(f"[EGRESO] {egresado.nombre} marcado como fugado ({egresado.tipo_egreso})")

        # Volver al panel de emergencias
        self._mostrar("emergencias")

    def _atender_paciente_sala(self, paciente) -> None:
        """
        Estabiliza a un paciente de sala restaurando sus signos vitales
        a valores normales aleatorizados dentro del rango ESTABLE.

        Solo aplica a PacienteSala. Registra la atención en el historial
        y fuerza la reevaluación del estado en el monitor.

        Args:
            paciente: Instancia de PacienteSala a atender.
        """
        from modelos.historial import Examen

        # Restaurar signos vitales a valores normales aleatorios
        paciente._signos_vitales = SignosVitales(
            frecuencia_cardiaca=random.randint(65, 95),
            frecuencia_respiratoria=random.randint(14, 18),
            saturacion_oxigeno=random.randint(96, 99),
            presion_sistolica=random.randint(105, 135),
            presion_diastolica=random.randint(65, 78),
            temperatura=round(random.uniform(36.5, 37.4), 1),
        )

        # Registrar atención en el historial
        if paciente.historial:
            paciente.historial.agregar_examen(Examen(
                tipo="Atención en sala de hospitalización",
                resultado="Paciente estabilizado — signos vitales restaurados a rangos normales",
                notas="Atención médica en sala. Monitorización continua.",
            ))

        # Forzar reevaluación del estado
        self._monitor.evaluar_paciente(paciente)

        # Detener alarma sonora y parpadeo
        self._notificador.detener_alarma_sala(paciente.id_paciente)
        tarjeta = self._panel_salas.tarjeta_por_id(paciente.id_paciente)
        if tarjeta:
            tarjeta.desactivar_parpadeo()

        # Refrescar panel de salas
        self._panel_salas.refrescar_tarjetas()

        print(f"[ATENCION SALA] {paciente.nombre} estabilizado -> {paciente.estado}")

        # Volver al panel de salas
        self._mostrar("salas")

    # ==================================================================
    # EXPORTACIÓN A PDF (SPRINT 7)
    # ==================================================================
    def _exportar_pdf(self, paciente) -> None:
        """
        Abre un diálogo de guardado y exporta la ficha del paciente a PDF.

        Args:
            paciente: Instancia de Paciente (o subclase) a exportar.
        """
        nombre_archivo = f"{paciente.nombre.replace(' ', '_')}_{paciente.id_paciente}.pdf"

        ruta = filedialog.asksaveasfilename(
            title="Exportar ficha del paciente",
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialfile=nombre_archivo,
        )

        if not ruta:
            return

        try:
            self._exportador_pdf.exportar_paciente(paciente, ruta)
            print(f"[PDF] Reporte exportado: {ruta}")
        except Exception as e:
            print(f"[PDF ERROR] {e}")

    # ==================================================================
    # BUCLE DE SIMULACIÓN PERIÓDICA
    # ==================================================================
    def _iniciar_simulacion(self) -> None:
        """
        Inicia el bucle de simulación periódica que aplica ticks del
        monitor cada INTERVALO_MONITOREO_MS milisegundos.
        Cada tick:
          1. Varía aleatoriamente los signos vitales de los pacientes.
          2. Evalúa cambios de estado.
          3. Notifica a los observadores (alertas, GUI).
          4. Refresca los paneles de la interfaz.
        """
        if self._simulacion_activa:
            return  # Ya está corriendo

        self._simulacion_activa = True
        self._ejecutar_tick()

    def _ejecutar_tick(self) -> None:
        """
        Ejecuta un solo tick de simulación y programa el siguiente.
        Envuelto en try/except para que un error no detenga la simulación.
        """
        if not self._simulacion_activa:
            return

        try:
            # Ejecutar tick del monitor (variar signos + evaluar)
            cambios = self._monitor.simular_tick()

            # Refrescar tarjetas visibles (actualización suave de valores)
            if isinstance(self._pantalla_actual, PanelSalas):
                self._panel_salas.refrescar_tarjetas()
            if isinstance(self._pantalla_actual, PanelEmergencias):
                self._panel_emergencias.refrescar_tarjetas()
        except Exception as e:
            print(f"[TICK ERROR] {e}")

        # Programar el siguiente tick
        self._ventana.after(INTERVALO_MONITOREO_MS, self._ejecutar_tick)

    def _detener_simulacion(self) -> None:
        """Detiene el bucle de simulación periódica."""
        self._simulacion_activa = False

    # ==================================================================
    # CALLBACKS DE INTEGRACIÓN
    # ==================================================================
    def _on_alerta_gui(self, alerta: Alerta) -> None:
        """
        Callback invocado por el Notificador cuando se genera una alerta
        crítica. Refresca las tarjetas del paciente afectado y activa
        el parpadeo visual si el paciente está en ATENCIÓN.
        """
        if alerta.paciente:
            id_pac = alerta.paciente.id_paciente
            tarjeta_sala = self._panel_salas.tarjeta_por_id(id_pac)
            tarjeta_emerg = self._panel_emergencias.tarjeta_por_id(id_pac)
            if tarjeta_sala:
                tarjeta_sala.actualizar()
                if alerta.paciente.estado == ESTADO_ATENCION:
                    tarjeta_sala.activar_parpadeo()
            if tarjeta_emerg:
                tarjeta_emerg.actualizar()

    def _cerrar_aplicacion(self) -> None:
        """
        Cierra la aplicación de forma ordenada:
        detiene la simulación y destruye la ventana.
        """
        self._detener_simulacion()
        self._ventana.destroy()

    # ==================================================================
    # PUNTO DE ENTRADA
    # ==================================================================
    def ejecutar(self) -> None:
        """
        Inicia el bucle principal de la interfaz gráfica.
       Bloquea la ejecución hasta que se cierre la ventana.
        """
        print("[GH] Iniciando aplicación...")
        self._ventana.mainloop()
        print("[GH] Aplicación cerrada.")


# ============================================================================
# ARRANQUE DEL PROGRAMA
# ============================================================================
if __name__ == "__main__":
    """
    Punto de entrada principal de Gestión Hospitalaria (GH).

    Crea la instancia de AplicacionGH y lanza la interfaz gráfica.
    Todo el sistema se inicializa dentro del constructor de la app:
      - Generación de pacientes ficticios.
      - Monitoreo de signos vitales.
      - Sistema de alertas y notificaciones.
      - Interfaz con paneles de sala, emergencias y detalle.
      - Simulador de emergencias.
      - Bucle de simulación periódica.
    """
    app = AplicacionGH()
    app.ejecutar()
