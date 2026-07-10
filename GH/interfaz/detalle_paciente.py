"""
Módulo: detalle_paciente.py
Sprint 5 — Vista de detalle del paciente.

Define la clase DetallePaciente, que muestra la ficha completa de un
paciente: datos demográficos, signos vitales actuales con indicadores
de estado, historial médico (exámenes, diagnósticos, tratamientos) y
botones de acción.

Dependencias previas necesarias:
    - config.py                       (estados, colores, nombres de signos)
    - interfaz/componentes.py         (BadgeEstado)
    - modelos/paciente.py             (Paciente)
    - modelos/signos_vitales.py       (SignosVitales)
    - modelos/historial.py            (HistorialMedico, Examen)

Librería externa requerida:
    - customtkinter  (pip install customtkinter)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk

from config import (
    COLORES_ESTADO,
    COLORES_TEXTO_ESTADO,
    NOMBRES_SIGNOS,
    UNIDADES_SIGNOS,
    RANGOS_NORMALES,
    ESTADO_CRITICO,
    ESTADO_ATENCION,
    ESTADO_PRUDENTE,
    ESTADO_ESTABLE,
    ESTADO_FALLECIDO,
    ESTADO_SIN_DATOS,
)

from interfaz.componentes import BadgeEstado
from modelos.paciente_sala import PacienteSala


class FilaSignoVital(ctk.CTkFrame):
    """
    Fila individual que muestra un signo vital con:
      - Nombre del signo.
      - Valor actual con unidad.
      - Barra de rango (mínimo - máximo normal).
      - Indicador de si está dentro o fuera de rango.
    """

    def __init__(self, parent, nombre_signo: str, valor: float, **kwargs):
        """
        Constructor de la fila de signo vital.

        Args:
            parent:       Widget padre.
            nombre_signo: Clave del signo (ej. "frecuencia_cardiaca").
            valor:        Valor actual del signo.
        """
        super().__init__(
            parent,
            fg_color="#252525",
            corner_radius=6,
            height=50,
            **kwargs,
        )
        self.pack_propagate(False)
        self._nombre_signo = nombre_signo

        # --- Nombre del signo (izquierda) ---
        nombre_legible = NOMBRES_SIGNOS.get(nombre_signo, nombre_signo)
        label_nombre = ctk.CTkLabel(
            self,
            text=nombre_legible,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#CCCCCC",
            width=200,
            anchor="w",
        )
        label_nombre.pack(side="left", padx=(12, 0))

        # --- Valor actual (centro) ---
        unidad = UNIDADES_SIGNOS.get(nombre_signo, "")
        texto_valor = self._formatear_valor(valor, unidad)
        self._label_valor = ctk.CTkLabel(
            self,
            text=texto_valor,
            font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
            text_color="#FFFFFF",
            width=100,
            anchor="center",
        )
        self._label_valor.pack(side="left", padx=10)

        # --- Indicador de rango (derecha) ---
        self._frame_rango = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_rango.pack(side="right", padx=12)

        # Etiqueta de estado (NORMAL / ALTERADO)
        en_rango = self._verificar_rango(nombre_signo, valor)
        self._label_estado = ctk.CTkLabel(
            self._frame_rango,
            text="NORMAL" if en_rango else "ALTERADO",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#4CAF50" if en_rango else "#F44336",
        )
        self._label_estado.pack(side="right")

        # Rango normal en texto pequeño
        vmin, vmax = RANGOS_NORMALES.get(nombre_signo, (0, 0))
        label_rango = ctk.CTkLabel(
            self._frame_rango,
            text=f"  ({vmin}-{vmax} {unidad})",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#777777",
        )
        label_rango.pack(side="right")

    def _formatear_valor(self, valor: float, unidad: str) -> str:
        """Formatea el valor: entero salvo temperatura, con su unidad."""
        if isinstance(valor, (int, float)):
            if valor == 0.0:
                return f"-- {unidad}"
            if self._nombre_signo == "temperatura":
                return f"{valor:.1f} {unidad}"
            return f"{int(round(valor))} {unidad}"
        return f"{valor} {unidad}"

    def _verificar_rango(self, nombre_signo: str, valor: float) -> bool:
        """Verifica si el valor está dentro del rango normal."""
        if valor == 0.0:
            return False
        vmin, vmax = RANGOS_NORMALES.get(nombre_signo, (0, 0))
        return vmin <= valor <= vmax

    def actualizar_valor(self, nuevo_valor: float) -> None:
        """
        Actualiza el valor mostrado y el indicador de rango.

        Args:
            nuevo_valor: Nuevo valor del signo vital.
        """
        unidad = UNIDADES_SIGNOS.get(self._nombre_signo, "")
        texto_valor = self._formatear_valor(nuevo_valor, unidad)
        self._label_valor.configure(text=texto_valor)

        en_rango = self._verificar_rango(self._nombre_signo, nuevo_valor)
        self._label_estado.configure(
            text="NORMAL" if en_rango else "ALTERADO",
            text_color="#4CAF50" if en_rango else "#F44336",
        )


class SeccionHistorial(ctk.CTkFrame):
    """
    Sección colapsable que muestra una categoría del historial médico
    (exámenes, diagnósticos o tratamientos) en formato de lista.
    """

    def __init__(self, parent, titulo: str, **kwargs):
        """
        Constructor de la sección de historial.

        Args:
            parent: Widget padre.
            titulo: Título de la sección (ej. "Exámenes").
        """
        super().__init__(
            parent,
            fg_color="#1E1E1E",
            corner_radius=8,
            **kwargs,
        )

        # Título de la sección
        label_titulo = ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#FFFFFF",
        )
        label_titulo.pack(padx=15, pady=(10, 5), anchor="w")

        # Separador
        sep = ctk.CTkFrame(self, height=1, fg_color="#444444")
        sep.pack(fill="x", padx=10, pady=(0, 5))

        # Área de contenido (scroll para listas largas)
        self._texto_contenido = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#CCCCCC",
            fg_color="#151515",
            corner_radius=6,
            wrap="word",
            height=120,
        )
        self._texto_contenido.pack(
            fill="both", expand=True, padx=10, pady=(0, 10)
        )
        self._texto_contenido.configure(state="disabled")

    def cargar_items(self, items: list) -> None:
        """
        Carga items en la sección. Cada item puede ser un string, un
        dict con 'descripcion'/'fecha'/'autor', o un objeto Examen.

        Args:
            items: Lista de items a mostrar.
        """
        self._texto_contenido.configure(state="normal")
        self._texto_contenido.delete("1.0", "end")

        if not items:
            self._texto_contenido.insert(
                "end", "(sin registros)\n"
            )
        else:
            for item in items:
                if isinstance(item, str):
                    self._texto_contenido.insert("end", f"• {item}\n")
                elif hasattr(item, 'tipo') and hasattr(item, 'resultado'):
                    # Es un Examen
                    fecha_str = item.fecha.strftime("%d/%m/%Y")
                    self._texto_contenido.insert(
                        "end",
                        f"• [{fecha_str}] {item.tipo}: {item.resultado}\n"
                    )
                elif isinstance(item, dict):
                    fecha_str = ""
                    if item.get("fecha"):
                        fecha_str = item["fecha"].strftime("%d/%m/%Y")
                    autor_str = f" ({item['autor']})" if item.get("autor") else ""
                    self._texto_contenido.insert(
                        "end",
                        f"• [{fecha_str}] {item['descripcion']}{autor_str}\n"
                    )

        self._texto_contenido.configure(state="disabled")


class DetallePaciente(ctk.CTkFrame):
    """
    Vista completa del perfil de un paciente.

    Secciones:
      - Cabecera: avatar, nombre, ID, badge de estado, prioridad.
      - Signos vitales: tabla con los 6 parámetros y estado de cada uno.
      - Historial médico: exámenes, diagnósticos y tratamientos.
      - Botones de acción: Volver, etc.
    """

    def __init__(
        self,
        parent,
        on_volver_callback=None,
        on_dar_alta_callback=None,
        on_atender_sala_callback=None,
        **kwargs,
    ):
        """
        Constructor de DetallePaciente.

        Args:
            parent:            Widget padre.
            on_volver_callback: Función llamada al presionar "Volver".
            on_dar_alta_callback: Función llamada al presionar "Dar de Alta".
            on_atender_sala_callback: Función llamada al presionar "Atender en Sala".
        """
        super().__init__(parent, **kwargs)

        self._on_volver          = on_volver_callback
        self._on_dar_alta        = on_dar_alta_callback
        self._on_atender_sala    = on_atender_sala_callback
        self._paciente           = None

        # Referencias a widgets dinámicos (para actualizar)
        self._filas_signos: dict[str, FilaSignoVital] = {}
        self._badge_estado: BadgeEstado = None
        self._label_nombre: ctk.CTkLabel = None
        self._label_info: ctk.CTkLabel = None

        # Configurar grid
        self.grid_rowconfigure(0, weight=0)      # Barra superior
        self.grid_rowconfigure(1, weight=1)      # Contenido principal
        self.grid_columnconfigure(0, weight=1)

        # Construir
        self._crear_barra_superior()
        self._contenedor_principal = None  # Se crea al cargar un paciente

    # ==================================================================
    # BARRA SUPERIOR
    # ==================================================================
    def _crear_barra_superior(self) -> None:
        """Barra con título y botón volver."""
        barra = ctk.CTkFrame(self, fg_color="#1A1A1A", height=55)
        barra.grid(row=0, column=0, sticky="ew")
        barra.pack_propagate(False)

        titulo = ctk.CTkLabel(
            barra,
            text="Detalle del Paciente",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#FFFFFF",
        )
        titulo.pack(side="left", padx=20, pady=10)

        if self._on_volver:
            btn_volver = ctk.CTkButton(
                barra,
                text="Volver al Panel",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                width=130,
                height=32,
                corner_radius=8,
                fg_color="#444444",
                hover_color="#555555",
                command=self._on_volver,
            )
            btn_volver.pack(side="right", padx=20, pady=10)


        # Botón "Dar de Alta" (solo visible si hay callback)
        if self._on_dar_alta:
            self._btn_dar_alta = ctk.CTkButton(
                barra,
                text="Dar de Alta",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                width=120,
                height=32,
                corner_radius=8,
                fg_color="#4CAF50",
                hover_color="#388E3C",
                command=self._on_click_dar_alta,
            )
            self._btn_dar_alta.pack(side="right", padx=5, pady=10)

        # Botón "Atender en Sala" (solo visible si hay callback)
        if self._on_atender_sala:
            self._btn_atender_sala = ctk.CTkButton(
                barra,
                text="Atender en Sala",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                width=140,
                height=32,
                corner_radius=8,
                fg_color="#1976D2",
                hover_color="#1565C0",
                command=self._on_click_atender_sala,
            )
            self._btn_atender_sala.pack(side="right", padx=5, pady=10)

    # ==================================================================
    # CARGA DE PACIENTE
    # ==================================================================
    def cargar_paciente(self, paciente) -> None:
        """
        Carga los datos de un paciente en la vista de detalle.

        Args:
            paciente: Instancia de Paciente (o subclase).
        """
        self._paciente = paciente

        # Destruir contenido anterior si existe
        if self._contenedor_principal is not None:
            self._contenedor_principal.destroy()

        # Crear nuevo contenedor con scroll
        self._contenedor_principal = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self._contenedor_principal.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=10
        )

        # Construir las secciones
        self._crear_cabecera()
        self._crear_signos_vitales()
        self._crear_historial()

    def refrescar(self) -> None:
        """
        Refresca la vista con los datos actuales del paciente cargado.
        """
        if self._paciente is None:
            return
        self.cargar_paciente(self._paciente)

    def _on_click_dar_alta(self) -> None:
        """Acción del botón 'Dar de Alta'."""
        if self._paciente is None:
            return
        if self._on_dar_alta:
            self._on_dar_alta(self._paciente)

    def _on_click_atender_sala(self) -> None:
        """Acción del botón 'Atender en Sala'."""
        if self._paciente is None:
            return
        if not isinstance(self._paciente, PacienteSala):
            return
        if self._on_atender_sala:
            self._on_atender_sala(self._paciente)

    # ==================================================================
    # SECCIÓN: CABECERA
    # ==================================================================
    def _crear_cabecera(self) -> None:
        """Sección superior con datos demográficos del paciente."""
        p = self._paciente

        frame_cabecera = ctk.CTkFrame(
            self._contenedor_principal,
            fg_color="#1E1E1E",
            corner_radius=10,
        )
        frame_cabecera.pack(fill="x", pady=(0, 10))

        # Fila superior: avatar + nombre + badge
        fila_sup = ctk.CTkFrame(frame_cabecera, fg_color="transparent")
        fila_sup.pack(fill="x", padx=20, pady=(15, 5))

        # Avatar circular
        iniciales = self._obtener_iniciales(p.nombre)
        color_avatar = COLORES_ESTADO.get(p.estado, "#757575")
        avatar = ctk.CTkFrame(
            fila_sup, width=52, height=52,
            fg_color=color_avatar, corner_radius=26,
        )
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(
            avatar, text=iniciales,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#FFFFFF",
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Nombre
        self._label_nombre = ctk.CTkLabel(
            fila_sup,
            text=p.nombre,
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#FFFFFF",
        )
        self._label_nombre.pack(side="left", padx=(15, 0))

        # Badge de estado (derecha)
        self._badge_estado = BadgeEstado(fila_sup, p.estado)
        self._badge_estado.pack(side="right", padx=(5, 0))

        # Fila inferior: datos demográficos
        fila_info = ctk.CTkFrame(frame_cabecera, fg_color="transparent")
        fila_info.pack(fill="x", padx=20, pady=(5, 15))

        tipo_pac = p.__class__.__name__
        if tipo_pac == "PacienteSala":
            ubicacion = f"Cama {p.numero_cama} — Planta: {p.planta}"
        else:
            ubicacion = (f"Emergencias — Prioridad adm: "
                        f"{p.prioridad_administrativa}/5 — "
                        f"Espera: {p.tiempo_espera_legible()}")

        info_texto = (
            f"ID: {p.id_paciente}  |  Edad: {p.edad} años  |  "
            f"Género: {p.genero}  |  Ingreso: {p.fecha_ingreso.strftime('%d/%m/%Y %H:%M')}\n"
            f"Ubicación: {ubicacion}  |  "
            f"Prioridad clínica: {p.prioridad}/5"
        )
        self._label_info = ctk.CTkLabel(
            fila_info,
            text=info_texto,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#999999",
            justify="left",
            anchor="w",
        )
        self._label_info.pack(anchor="w")

    # ==================================================================
    # SECCIÓN: SIGNOS VITALES
    # ==================================================================
    def _crear_signos_vitales(self) -> None:
        """Sección con tabla de signos vitales actuales."""
        frame_signos = ctk.CTkFrame(
            self._contenedor_principal,
            fg_color="#1E1E1E",
            corner_radius=10,
        )
        frame_signos.pack(fill="x", pady=(0, 10))

        # Título
        titulo = ctk.CTkLabel(
            frame_signos,
            text="Signos Vitales",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#FFFFFF",
        )
        titulo.pack(padx=20, pady=(15, 10), anchor="w")

        # Separador
        sep = ctk.CTkFrame(frame_signos, height=1, fg_color="#444444")
        sep.pack(fill="x", padx=15, pady=(0, 10))

        # Filas de signos vitales
        signos = self._paciente.signos_vitales
        self._filas_signos.clear()

        # Presión arterial (sistólica y diastólica juntas)
        for nombre in [
            "frecuencia_cardiaca",
            "frecuencia_respiratoria",
            "saturacion_oxigeno",
            "presion_sistolica",
            "presion_diastolica",
            "temperatura",
        ]:
            valor = signos._obtener_valor(nombre)
            fila = FilaSignoVital(frame_signos, nombre, valor)
            fila.pack(fill="x", padx=15, pady=3)
            self._filas_signos[nombre] = fila

        # Espacio inferior
        ctk.CTkFrame(frame_signos, height=5, fg_color="transparent").pack()

    # ==================================================================
    # SECCIÓN: HISTORIAL MÉDICO
    # ==================================================================
    def _crear_historial(self) -> None:
        """Sección con el historial médico del paciente."""
        frame_historial = ctk.CTkFrame(
            self._contenedor_principal,
            fg_color="#1E1E1E",
            corner_radius=10,
        )
        frame_historial.pack(fill="x", pady=(0, 10))

        # Título
        titulo = ctk.CTkLabel(
            frame_historial,
            text="Historial Médico",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#FFFFFF",
        )
        titulo.pack(padx=20, pady=(15, 5), anchor="w")

        # Separador
        sep = ctk.CTkFrame(frame_historial, height=1, fg_color="#444444")
        sep.pack(fill="x", padx=15, pady=(0, 10))

        historial = self._paciente.historial

        # Si no hay historial, mostrar mensaje
        if historial is None:
            ctk.CTkLabel(
                frame_historial,
                text="(Historial médico no disponible)",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color="#777777",
            ).pack(padx=20, pady=(0, 15))
            return

        # Sección de exámenes
        seccion_examenes = SeccionHistorial(
            frame_historial,
            f"Exámenes ({historial.total_examenes()})",
        )
        seccion_examenes.pack(fill="x", padx=15, pady=(0, 8))
        seccion_examenes.cargar_items(historial.examenes)

        # Sección de diagnósticos
        seccion_diag = SeccionHistorial(
            frame_historial,
            f"Diagnósticos ({historial.total_diagnosticos()})",
        )
        seccion_diag.pack(fill="x", padx=15, pady=(0, 8))
        seccion_diag.cargar_items(historial.diagnosticos)

        # Sección de tratamientos
        seccion_trat = SeccionHistorial(
            frame_historial,
            f"Tratamientos ({historial.total_tratamientos()})",
        )
        seccion_trat.pack(fill="x", padx=15, pady=(0, 8))
        seccion_trat.cargar_items(historial.tratamientos)

        # Sección de medicamentos
        seccion_med = SeccionHistorial(
            frame_historial,
            f"Medicamentos ({historial.total_medicamentos()})",
        )
        seccion_med.pack(fill="x", padx=15, pady=(0, 15))
        seccion_med.cargar_items(historial.medicamentos)

    # ==================================================================
    # MÉTODOS AUXILIARES
    # ==================================================================
    def _obtener_iniciales(self, nombre: str) -> str:
        """Extrae hasta 2 iniciales del nombre del paciente."""
        partes = nombre.split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[-1][0]).upper()
        return nombre[:2].upper()

    # ==================================================================
    # PROPIEDADES
    # ==================================================================
    @property
    def paciente(self):
        """El paciente actualmente mostrado en el detalle."""
        return self._paciente


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba visual del DetallePaciente.
    Abre una ventana con la ficha completa de un paciente generado
    aleatoriamente: datos personales, signos vitales e historial médico.
    """
    from datos.generador import GeneradorDatos

    print("=" * 60)
    print("  PRUEBA VISUAL: DetallePaciente")
    print("=" * 60)
    print("  Se abrirá una ventana con la ficha completa del paciente.")
    print("  Incluye: datos personales, signos vitales e historial.")
    print("  Usa el botón 'Actualizar' para refrescar los datos.")
    print("  Cierra la ventana para terminar la prueba.")
    print("=" * 60)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    ventana = ctk.CTk()
    ventana.title("GH — Detalle del Paciente (Prueba)")
    ventana.geometry("1000x800")
    ventana.minsize(800, 600)

    # Generar un paciente con historial
    generador = GeneradorDatos(semilla=99)
    paciente = generador.generar_paciente_sala()

    # Asegurar que el historial se generó
    if paciente.historial is None:
        paciente.historial = generador.generar_historial(paciente.id_paciente)

    # Callback volver
    def volver():
        print("\n>>> Volver al panel")
        ventana.destroy()

    # Crear vista de detalle
    detalle = DetallePaciente(
        ventana,
        on_volver_callback=volver,
    )
    detalle.cargar_paciente(paciente)

    print(f"\n  Paciente cargado: {paciente.nombre}")
    print(f"  Estado: {paciente.estado}")
    print(f"  Signos: HR={paciente.signos_vitales.frecuencia_cardiaca:.0f}, "
          f"SpO2={paciente.signos_vitales.saturacion_oxigeno:.0f}%")
    print(f"  Exámenes en historial: {paciente.historial.total_examenes()}")

    ventana.mainloop()
