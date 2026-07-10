"""
Módulo: panel_emergencias.py
Sprint 5 — Panel del área de urgencias.

Define la clase PanelEmergencias, que muestra las tarjetas de los pacientes
en el área de urgencias, ordenadas por prioridad. Incluye una sección de
notificaciones y un botón "Atender Siguiente" para simular el llamado del
siguiente paciente en la cola de espera.

Dependencias previas necesarias:
    - config.py                  (constantes)
    - interfaz/componentes.py    (TarjetaPaciente, BadgeEstado)
    - interfaz/panel_salas.py    (BarraResumen — reutilizada)

Librería externa requerida:
    - customtkinter  (pip install customtkinter)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from datetime import datetime

from config import (
    ESTADOS_EMERGENCIA,
    COLORES_ESTADO,
    COLORES_TEXTO_ESTADO,
    PRIORIDAD_ESTADO,
    ESTADO_CRITICO,
    ESTADO_NO_CRITICO,
    COLOR_CRITICO,
    COLOR_ESTABLE,
)

from interfaz.componentes import TarjetaPaciente, BadgeEstado
from interfaz.panel_salas import BarraResumen


class PanelNotificaciones(ctk.CTkFrame):
    """
    Panel lateral que muestra un registro de notificaciones del área
    de emergencias: cambios de estado, pacientes atendidos, médicos
    disponibles, etc.

    Funciona como un log visual con scroll. Las notificaciones más
    recientes aparecen al principio.
    """

    MAX_NOTIFICACIONES = 50  # Límite para no sobrecargar la interfaz

    def __init__(self, parent, **kwargs):
        """Constructor del panel de notificaciones."""
        super().__init__(
            parent,
            fg_color="#1A1A1A",
            corner_radius=10,
            **kwargs,
        )

        # Lista interna de mensajes (tuplas: (timestamp, mensaje, tipo))
        self._mensajes: list[tuple[datetime, str, str]] = []

        # Construir la interfaz
        self._crear_widgets()

    def _crear_widgets(self) -> None:
        """Construye los elementos visuales del panel de notificaciones."""
        # Título del panel
        titulo = ctk.CTkLabel(
            self,
            text="Notificaciones",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#FFFFFF",
        )
        titulo.pack(padx=15, pady=(10, 5), anchor="w")

        # Separador
        sep = ctk.CTkFrame(self, height=1, fg_color="#444444")
        sep.pack(fill="x", padx=10, pady=(0, 5))

        # Área de texto con scroll para las notificaciones
        self._texto_notificaciones = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#CCCCCC",
            fg_color="#111111",
            corner_radius=8,
            wrap="word",
        )
        self._texto_notificaciones.pack(
            fill="both", expand=True, padx=10, pady=(0, 10)
        )

        # Deshabilitar edición (solo lectura)
        self._texto_notificaciones.configure(state="disabled")

    def agregar_notificacion(self, mensaje: str, tipo: str = "INFO") -> None:
        """
        Agrega una notificación al panel.

        Args:
            mensaje: Texto de la notificación.
            tipo:    "INFO", "ALERTA" o "ATENCION". Afecta el prefijo.
        """
        ahora = datetime.now()

        # Prefijo según tipo
        prefijos = {
            "INFO":     "[i]",
            "ALERTA":   "[!]",
            "ATENCION": "[>>]",
        }
        prefijo = prefijos.get(tipo, "[i]")

        texto = f"{ahora.strftime('%H:%M:%S')} {prefijo} {mensaje}\n"

        self._mensajes.append((ahora, mensaje, tipo))

        # Limitar la cantidad de mensajes en memoria
        if len(self._mensajes) > self.MAX_NOTIFICACIONES:
            self._mensajes = self._mensajes[-self.MAX_NOTIFICACIONES:]

        # Actualizar el widget de texto
        self._actualizar_texto()

    def _actualizar_texto(self) -> None:
        """Reconstruye el contenido del área de texto con los mensajes acumulados."""
        self._texto_notificaciones.configure(state="normal")
        self._texto_notificaciones.delete("1.0", "end")

        # Mostrar los últimos mensajes (más recientes al final)
        for _, mensaje, tipo in self._mensajes:
            prefijos = {"INFO": "[i]", "ALERTA": "[!]", "ATENCION": "[>>]"}
            prefijo = prefijos.get(tipo, "[i]")
            self._texto_notificaciones.insert("end", f"{prefijo} {mensaje}\n")

        self._texto_notificaciones.configure(state="disabled")
        # Auto-scroll al final
        self._texto_notificaciones.see("end")

    def limpiar(self) -> None:
        """Limpia todas las notificaciones del panel."""
        self._mensajes.clear()
        self._texto_notificaciones.configure(state="normal")
        self._texto_notificaciones.delete("1.0", "end")
        self._texto_notificaciones.configure(state="disabled")


class PanelEmergencias(ctk.CTkFrame):
    """
    Panel principal del área de urgencias / emergencias.

    Muestra:
      - Barra de resumen con conteos por estado.
      - Panel de notificaciones (lateral derecho).
      - Cuadrícula de tarjetas de pacientes ordenadas por prioridad.
      - Botón "Atender Siguiente" para simular la cola de atención.
      - Botones de control (Actualizar, Volver).

    Se integra con el MonitorSignos y el Notificador para recibir
    alertas en tiempo real durante la simulación.
    """

    def __init__(
        self,
        parent,
        on_ver_detalle_callback=None,
        on_atender_siguiente_callback=None,
        on_volver_callback=None,
        on_marcar_fuga_callback=None,
        on_ver_mas_callback=None,
        **kwargs,
    ):
        """
        Constructor del PanelEmergencias.

        Args:
            parent:                     Widget padre (ventana principal).
            on_ver_detalle_callback:    Callback al hacer click en tarjeta.
            on_atender_siguiente_callback: Callback al presionar "Atender Siguiente".
            on_volver_callback:         Callback al presionar "Volver".
            on_marcar_fuga_callback:    Callback al presionar "Marcar Fuga".
            on_ver_mas_callback:        Callback al presionar "Ver más".
        """
        super().__init__(parent, **kwargs)

        self._on_ver_detalle         = on_ver_detalle_callback
        self._on_atender_siguiente   = on_atender_siguiente_callback
        self._on_volver              = on_volver_callback
        self._on_marcar_fuga         = on_marcar_fuga_callback
        self._on_ver_mas             = on_ver_mas_callback

        # Lista de pacientes en espera
        self._pacientes: list = []

        # Referencias a tarjetas
        self._tarjetas: dict[str, TarjetaPaciente] = {}

        # Configurar layout principal: dos columnas (tarjetas | notificaciones)
        self.grid_columnconfigure(0, weight=3)  # Área de tarjetas
        self.grid_columnconfigure(1, weight=1)  # Panel de notificaciones
        self.grid_rowconfigure(0, weight=0)     # Barra superior
        self.grid_rowconfigure(1, weight=1)     # Contenido principal

        # Construir la interfaz
        self._crear_barra_superior()
        self._crear_area_principal()

    # ==================================================================
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ==================================================================
    def _crear_barra_superior(self) -> None:
        """Construye la barra superior con título y botones de control."""
        barra = ctk.CTkFrame(self, fg_color="#1A1A1A", height=55)
        barra.grid(row=0, column=0, columnspan=2, sticky="ew")
        barra.pack_propagate(False)

        # Título
        titulo = ctk.CTkLabel(
            barra,
            text="Panel de Emergencias",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#FFFFFF",
        )
        titulo.pack(side="left", padx=20, pady=10)

        # Subtítulo
        subtitulo = ctk.CTkLabel(
            barra,
            text="Atención de urgencias por prioridad",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#888888",
        )
        subtitulo.pack(side="left", padx=(5, 20), pady=10)

        # Botón "Volver"
        if self._on_volver:
            btn_volver = ctk.CTkButton(
                barra,
                text="Volver",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                width=90,
                height=32,
                corner_radius=8,
                fg_color="#444444",
                hover_color="#555555",
                command=self._on_volver,
            )
            btn_volver.pack(side="right", padx=20, pady=10)

        # Botón "Atender Siguiente"
        self._btn_atender = ctk.CTkButton(
            barra,
            text="Atender Siguiente",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            width=160,
            height=32,
            corner_radius=8,
            fg_color=COLOR_CRITICO,
            hover_color="#B71C1C",
            command=self._on_click_atender,
        )
        self._btn_atender.pack(side="right", padx=5, pady=10)


        # Botón "Marcar Fuga"
        if self._on_marcar_fuga:
            self._btn_marcar_fuga = ctk.CTkButton(
                barra,
                text="Marcar Fuga",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                width=130,
                height=32,
                corner_radius=8,
                fg_color="#FF9800",
                hover_color="#E65100",
                command=self._on_click_marcar_fuga,
            )
            self._btn_marcar_fuga.pack(side="right", padx=5, pady=10)

    def _crear_area_principal(self) -> None:
        """Construye el área principal con tarjetas y notificaciones."""
        # --- Columna izquierda: resumen + tarjetas ---
        contenedor_izq = ctk.CTkFrame(self, fg_color="transparent")
        contenedor_izq.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=5)
        contenedor_izq.grid_rowconfigure(0, weight=0)   # Barra de resumen
        contenedor_izq.grid_rowconfigure(1, weight=1)   # Área de tarjetas
        contenedor_izq.grid_columnconfigure(0, weight=1)

        # Área de scroll para las tarjetas
        self._frame_scroll = ctk.CTkScrollableFrame(
            contenedor_izq,
            fg_color="transparent",
        )
        self._frame_scroll.grid(row=1, column=0, sticky="nsew")

        # Configurar columnas del grid (3 columnas para tarjetas)
        for col in range(3):
            self._frame_scroll.grid_columnconfigure(col, weight=1)

        # --- Columna derecha: panel de notificaciones ---
        self._panel_notificaciones = PanelNotificaciones(
            self,
            width=300,
        )
        self._panel_notificaciones.grid(
            row=1, column=1, sticky="nsew", padx=(2, 5), pady=5
        )

    # ==================================================================
    # CARGA Y ORDENAMIENTO DE PACIENTES
    # ==================================================================
    def cargar_pacientes(self, pacientes: list) -> None:
        """
        Carga una lista de pacientes de emergencias en el panel.
        Los pacientes se ordenan por prioridad (mayor primero) y,
        dentro de la misma prioridad, por tiempo de espera (mayor primero).

        Args:
            pacientes: Lista de instancias de PacienteEmergencia.
        """
        self._pacientes = list(pacientes)

        # Ordenar: CRITICO siempre primero, luego por prioridad administrativa
        # (mayor primero), y finalmente por tiempo de espera (mayor primero).
        self._pacientes.sort(
            key=lambda p: (
                1 if p.estado == ESTADO_CRITICO else 0,
                p.prioridad_administrativa,
                p.minutos_espera,
            ),
            reverse=True,
        )

        self._reconstruir_tarjetas()
        self._panel_notificaciones.agregar_notificacion(
            f"Panel cargado: {len(self._pacientes)} pacientes en espera.",
            tipo="INFO",
        )

    def refrescar_tarjetas(self) -> None:
        """
        Refresca visualmente todas las tarjetas con los valores actuales,
        sin destruir ni recrear widgets. Solo actualiza colores, badges
        e indicadores. No reordena (eso solo ocurre al cargar explícitamente).
        """
        if not self._pacientes:
            return

        # Actualizar cada tarjeta existente sin recrearla
        for id_pac, tarjeta in self._tarjetas.items():
            tarjeta.actualizar()

        # Actualizar barra de resumen si existe
        if hasattr(self, '_barra_resumen') and self._barra_resumen.winfo_exists():
            self._barra_resumen.actualizar(self._pacientes, ESTADOS_EMERGENCIA)

    def _reconstruir_tarjetas(self) -> None:
        """
        Limpia el área de tarjetas y las reconstruye con los pacientes
        ordenados por prioridad.
        """
        # Limpiar
        for widget in self._frame_scroll.winfo_children():
            widget.destroy()
        self._tarjetas.clear()

        if not self._pacientes:
            ctk.CTkLabel(
                self._frame_scroll,
                text="No hay pacientes en espera en emergencias.",
                font=ctk.CTkFont(family="Segoe UI", size=16),
                text_color="#666666",
            ).grid(row=0, column=0, columnspan=3, pady=100)
            return

        # Barra de resumen
        self._barra_resumen = BarraResumen(self._frame_scroll)
        self._barra_resumen.grid(
            row=0, column=0, columnspan=3, sticky="ew",
            padx=10, pady=(5, 10),
        )
        self._barra_resumen.actualizar(self._pacientes)

        # Crear tarjetas en grid (3 columnas para dejar espacio a notificaciones)
        columnas = 3
        for indice, paciente in enumerate(self._pacientes):
            fila    = (indice // columnas) + 1
            columna = indice % columnas

            tarjeta = TarjetaPaciente(
                self._frame_scroll,
                paciente,
                on_click_callback=self._on_tarjeta_click,
                on_ver_mas_callback=self._on_ver_mas,
            )
            tarjeta.grid(row=fila, column=columna, padx=5, pady=5, sticky="nsew")
            self._tarjetas[paciente.id_paciente] = tarjeta

    # ==================================================================
    # MANEJO DE EVENTOS
    # ==================================================================
    def _on_tarjeta_click(self, paciente) -> None:
        """Click en tarjeta de paciente."""
        self._panel_notificaciones.agregar_notificacion(
            f"Ver detalle: {paciente.nombre} ({paciente.estado})",
            tipo="INFO",
        )
        if self._on_ver_detalle:
            self._on_ver_detalle(paciente)

    def _on_click_atender(self) -> None:
        """
        Acción del botón "Atender Siguiente".
        Notifica que un médico está libre y se puede atender al siguiente
        paciente (el de mayor prioridad en la cola).
        """
        if not self._pacientes:
            self._panel_notificaciones.agregar_notificacion(
                "No hay pacientes en espera.",
                tipo="INFO",
            )
            return

        # Seleccionar siempre primero un paciente CRITICO si existe
        siguiente = None
        for p in self._pacientes:
            if p.estado == ESTADO_CRITICO:
                siguiente = p
                break
        if siguiente is None:
            siguiente = self._pacientes[0]
        self._panel_notificaciones.agregar_notificacion(
            f"Medico disponible -> Atendiendo a: {siguiente.nombre} "
            f"({siguiente.estado}, prioridad {siguiente.prioridad})",
            tipo="ATENCION",
        )

        if self._on_atender_siguiente:
            self._on_atender_siguiente(siguiente)

    def _on_click_marcar_fuga(self) -> None:
        """
        Acción del botón "Marcar Fuga".
        Notifica que se quiere marcar como fugado al paciente de mayor prioridad
        en la cola de emergencias.
        """
        if not self._pacientes:
            self._panel_notificaciones.agregar_notificacion(
                "No hay pacientes en espera para marcar fuga.",
                tipo="INFO",
            )
            return

        # Seleccionar el primer paciente en la cola
        siguiente = None
        for p in self._pacientes:
            if p.estado == ESTADO_CRITICO:
                siguiente = p
                break
        if siguiente is None:
            siguiente = self._pacientes[0]

        self._panel_notificaciones.agregar_notificacion(
            f"FUGA: {siguiente.nombre} marcado como fugado.",
            tipo="ALERTA",
        )

        if self._on_marcar_fuga:
            self._on_marcar_fuga(siguiente)

    # ==================================================================
    # MÉTODOS DE INTEGRACIÓN CON MONITOR Y NOTIFICADOR
    # ==================================================================
    def recibir_alerta(self, alerta) -> None:
        """
        Recibe una alerta desde el Notificador y la muestra en el
        panel de notificaciones.

        Pensado para ser usado como callback del Notificador:
            notificador.configurar_callback_visual(panel.recibir_alerta)

        Args:
            alerta: Instancia de Alerta desde alertas/notificador.py.
        """
        tipo = "ALERTA" if alerta.es_critica else "INFO"

        # Actualizar la tarjeta del paciente afectado
        if alerta.paciente:
            id_pac = alerta.paciente.id_paciente
            if id_pac in self._tarjetas:
                self._tarjetas[id_pac].actualizar()

        self._panel_notificaciones.agregar_notificacion(
            alerta.mensaje,
            tipo=tipo,
        )

    def notificar_medico_disponible(self, medico=None) -> None:
        """
        Muestra una notificación indicando que un médico está disponible
        para atender al siguiente paciente.

        Args:
            medico: Instancia de Doctor (opcional) para personalizar el mensaje.
        """
        nombre_medico = medico.nombre if medico else "un médico"
        self._panel_notificaciones.agregar_notificacion(
            f"{nombre_medico} está disponible para atender.",
            tipo="ATENCION",
        )

    # ==================================================================
    # MÉTODOS DE CONSULTA
    # ==================================================================
    @property
    def pacientes(self) -> list:
        """Lista de pacientes actualmente en el panel."""
        return list(self._pacientes)

    @property
    def siguiente_paciente(self):
        """
        El paciente con mayor prioridad en la cola de espera
        (None si no hay pacientes). Siempre prioriza CRITICO
        sobre NO_CRITICO.
        """
        if not self._pacientes:
            return None
        for p in self._pacientes:
            if p.estado == ESTADO_CRITICO:
                return p
        return self._pacientes[0]

    def tarjeta_por_id(self, id_paciente: str) -> TarjetaPaciente | None:
        """Obtiene la tarjeta de un paciente por ID."""
        return self._tarjetas.get(id_paciente)

    @property
    def panel_notificaciones(self) -> PanelNotificaciones:
        """Acceso al panel de notificaciones para uso externo."""
        return self._panel_notificaciones


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba visual del PanelEmergencias.
    Abre una ventana con pacientes de emergencias generados aleatoriamente,
    ordenados por prioridad, con panel de notificaciones y botón de atender.
    """
    from datos.generador import GeneradorDatos
    from datos.repositorio import RepositorioPacientes

    print("=" * 60)
    print("  PRUEBA VISUAL: PanelEmergencias")
    print("=" * 60)
    print("  Se abrirá una ventana con el panel de emergencias.")
    print("  Pacientes ordenados por prioridad (CRITICO primero).")
    print("  Panel de notificaciones a la derecha.")
    print("  Botón 'Atender Siguiente' para simular atención.")
    print("  Cierra la ventana para terminar la prueba.")
    print("=" * 60)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    ventana = ctk.CTk()
    ventana.title("GH — Panel de Emergencias (Prueba)")
    ventana.geometry("1280x750")
    ventana.minsize(1000, 500)

    # Generar pacientes de emergencia
    generador = GeneradorDatos(semilla=123)
    repo = RepositorioPacientes()
    repo.agregar_pacientes(generador.generar_pacientes_emergencia(cantidad=9))

    # Callbacks
    def ver_detalle(paciente):
        print(f"\n>>> Ver detalle: {paciente.nombre} | {paciente.estado}")

    def atender_siguiente(paciente):
        print(f"\n>>> Atendiendo: {paciente.nombre} (Prioridad: {paciente.prioridad})")

    def volver():
        print("\n>>> Volver al menú principal")
        ventana.destroy()

    # Crear panel
    panel = PanelEmergencias(
        ventana,
        on_ver_detalle_callback=ver_detalle,
        on_atender_siguiente_callback=atender_siguiente,
        on_volver_callback=volver,
    )
    panel.cargar_pacientes(repo.obtener_emergencia())

    # Simular algunas notificaciones de ejemplo
    panel.panel_notificaciones.agregar_notificacion(
        "Sistema de emergencias iniciado.", tipo="INFO"
    )
    panel.panel_notificaciones.agregar_notificacion(
        "ATENCIÓN: Paciente crítico detectado en la cola.", tipo="ALERTA"
    )

    ventana.mainloop()
