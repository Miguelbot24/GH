"""
Módulo: panel_salas.py
Sprint 4 — Panel de salas de internación.

Define la clase PanelSalas, que muestra las tarjetas de los pacientes
internados en las salas del hospital. Es un panel con scroll que organiza
las tarjetas en una cuadrícula adaptable y muestra un resumen de estados.

Dependencias previas necesarias:
    - config.py                  (constantes)
    - interfaz/componentes.py    (TarjetaPaciente, BadgeEstado)

Librería externa requerida:
    - customtkinter  (pip install customtkinter)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk

from config import (
    ESTADOS_SALA,
    COLORES_ESTADO,
    COLORES_TEXTO_ESTADO,
    PRIORIDAD_ESTADO,
    ESTADO_ATENCION,
    ESTADO_PRUDENTE,
    ESTADO_ESTABLE,
    ESTADO_FALLECIDO,
    ESTADO_SIN_DATOS,
    SALAS_HOSPITAL,
)

from interfaz.componentes import TarjetaPaciente, BadgeEstado


class BarraResumen(ctk.CTkFrame):
    """
    Barra horizontal que muestra un resumen estadístico de los pacientes:
    total, cuántos hay en cada estado clínico y un indicador visual.
    """

    def __init__(self, parent, **kwargs):
        """Constructor de la barra de resumen."""
        super().__init__(
            parent,
            height=50,
            fg_color="#252525",
            corner_radius=8,
            **kwargs,
        )
        self.pack_propagate(False)

        # Contenedor flexible para los badges de conteo
        self._contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self._contenedor.pack(fill="x", padx=15, pady=8)

        # Etiqueta "Total" a la izquierda
        self._label_total = ctk.CTkLabel(
            self._contenedor,
            text="Total: 0",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#FFFFFF",
        )
        self._label_total.pack(side="left", padx=(0, 20))

        # Badges dinámicos por estado (se crean en actualizar())
        self._badges_estado = {}

    def actualizar(self, pacientes: list, estados_a_mostrar=None) -> None:
        """
        Recalcula y actualiza los conteos por estado.

        Args:
            pacientes:         Lista de pacientes actuales en el panel.
            estados_a_mostrar: Tupla de estados a contar y mostrar.
                               Por defecto ESTADOS_SALA (salas).
        """
        if estados_a_mostrar is None:
            estados_a_mostrar = ESTADOS_SALA

        total = len(pacientes)
        self._label_total.configure(text=f"Total: {total}")

        conteo = {estado: 0 for estado in estados_a_mostrar}
        for p in pacientes:
            conteo[p.estado] = conteo.get(p.estado, 0) + 1

        for estado in estados_a_mostrar:
            cantidad = conteo.get(estado, 0)

            if estado in self._badges_estado:
                frame, label = self._badges_estado[estado]
                label.configure(text=f"{estado}: {cantidad}")
                if cantidad == 0:
                    frame.pack_forget()
                else:
                    frame.pack(side="left", padx=4)
            elif cantidad > 0:
                color_fondo = COLORES_ESTADO.get(estado, "#757575")
                color_texto = COLORES_TEXTO_ESTADO.get(estado, "#FFFFFF")

                frame = ctk.CTkFrame(
                    self._contenedor,
                    fg_color=color_fondo,
                    corner_radius=6,
                    height=28,
                )
                frame.pack(side="left", padx=4)
                frame.pack_propagate(False)

                label = ctk.CTkLabel(
                    frame,
                    text=f"{estado}: {cantidad}",
                    font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                    text_color=color_texto,
                )
                label.pack(padx=10, pady=3)

                self._badges_estado[estado] = (frame, label)


class PanelSalas(ctk.CTkFrame):
    """
    Panel principal que muestra las tarjetas de los pacientes internados
    en las salas del hospital.

    Se compone de:
      - Barra de resumen con conteos por estado.
      - Área desplazable con las tarjetas de pacientes organizadas en grid.

    Este panel es un CTkFrame pensado para ser embebido en la ventana
    principal. Expone callbacks para navegar a otras vistas (detalle de
    paciente, menú principal, etc.).
    """

    def __init__(
        self,
        parent,
        on_ver_detalle_callback=None,
        on_volver_callback=None,
        on_ver_mas_callback=None,
        **kwargs,
    ):
        """
        Constructor del PanelSalas.

        Args:
            parent:               Widget padre (ventana principal).
            on_ver_detalle_callback: Función llamada al hacer click en una
                                 tarjeta. Recibe el paciente como argumento.
            on_volver_callback:   Función llamada al presionar "Volver".
            on_ver_mas_callback:  Función llamada al presionar "Ver más".
        """
        super().__init__(parent, **kwargs)

        self._on_ver_detalle = on_ver_detalle_callback
        self._on_volver      = on_volver_callback
        self._on_ver_mas     = on_ver_mas_callback

        # Lista interna de pacientes mostrados
        self._pacientes: list = []

        # Referencias a las tarjetas creadas (para actualizaciones)
        self._tarjetas: dict[str, TarjetaPaciente] = {}

        # Configurar grid del panel
        self.grid_rowconfigure(0, weight=0)     # Barra superior
        self.grid_rowconfigure(1, weight=1)     # Área de tarjetas (expandible)
        self.grid_columnconfigure(0, weight=1)

        # Construir los elementos
        self._crear_barra_superior()
        self._crear_area_tarjetas()

    # ==================================================================
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ==================================================================
    def _crear_barra_superior(self) -> None:
        """Construye la barra superior con título y controles."""
        barra = ctk.CTkFrame(self, fg_color="#1A1A1A", height=55)
        barra.grid(row=0, column=0, sticky="ew")
        barra.pack_propagate(False)

        # Título de la sección
        titulo = ctk.CTkLabel(
            barra,
            text="Panel de Hospitalización",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#FFFFFF",
        )
        titulo.pack(side="left", padx=20, pady=10)

        # Subtítulo informativo
        subtitulo = ctk.CTkLabel(
            barra,
            text="Pacientes internados",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#888888",
        )
        subtitulo.pack(side="left", padx=(5, 20), pady=10)

        # Botón "Volver" (derecha)
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


    def _crear_area_tarjetas(self) -> None:
        """Construye el área desplazable donde van las tarjetas de pacientes."""
        # Frame contenedor del scroll
        self._frame_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self._frame_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Configurar columnas del grid para las tarjetas (4 columnas)
        for col in range(4):
            self._frame_scroll.grid_columnconfigure(col, weight=1)

        # Texto de placeholder cuando no hay pacientes
        self._label_vacio = ctk.CTkLabel(
            self._frame_scroll,
            text="No hay pacientes internados en sala.\n"
                 "Use 'Actualizar' para cargar los datos.",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color="#666666",
        )

    # ==================================================================
    # BARRA DE RESUMEN (dentro del área de scroll)
    # ==================================================================
    def _crear_barra_resumen(self) -> BarraResumen:
        """Crea la barra de resumen dentro del área de tarjetas."""
        barra = BarraResumen(self._frame_scroll)
        return barra

    # ==================================================================
    # CARGA DE PACIENTES
    # ==================================================================
    def cargar_pacientes(self, pacientes: list) -> None:
        """
        Carga una lista de pacientes en el panel, reemplazando el
        contenido actual.

        Args:
            pacientes: Lista de instancias de Paciente (normalmente PacienteSala).
        """
        self._pacientes = list(pacientes)
        self._reconstruir_tarjetas()

    def refrescar_tarjetas(self) -> None:
        """
        Refresca visualmente todas las tarjetas con los valores actuales
        de los pacientes, sin destruir ni recrear widgets.
        """
        if not self._pacientes:
            return
        for id_pac, tarjeta in self._tarjetas.items():
            tarjeta.actualizar()

    def _reconstruir_tarjetas(self) -> None:
        """
        Limpia el área de tarjetas y las reconstruye agrupadas por sala.
        Cada sala muestra un encabezado con su nombre y color, seguido
        de una cuadrícula de 3×2 con las tarjetas de sus 6 pacientes.
        """
        # Limpiar el área de scroll
        for widget in self._frame_scroll.winfo_children():
            widget.destroy()
        self._tarjetas.clear()

        if not self._pacientes:
            ctk.CTkLabel(
                self._frame_scroll,
                text="No hay pacientes internados en sala.",
                font=ctk.CTkFont(family="Segoe UI", size=16),
                text_color="#666666",
            ).pack(pady=100)
            return

        # Agrupar pacientes por sala (planta)
        salas_agrupadas = {}
        for p in self._pacientes:
            sala = p.planta if hasattr(p, 'planta') else "General"
            if sala not in salas_agrupadas:
                salas_agrupadas[sala] = []
            salas_agrupadas[sala].append(p)

        # Buscar el color de cada sala desde SALAS_HOSPITAL
        colores_salas = {s["nombre"]: s["color"] for s in SALAS_HOSPITAL}

        # Construir cada sección de sala
        for nombre_sala, pacientes_sala in salas_agrupadas.items():
            color_sala = colores_salas.get(nombre_sala, "#555555")
            self._crear_seccion_sala(nombre_sala, color_sala, pacientes_sala)

    def _crear_seccion_sala(
        self, nombre_sala: str, color_sala: str, pacientes: list
    ) -> None:
        """
        Crea una sección visual para una sala: encabezado + grid 3×2 de tarjetas.

        Args:
            nombre_sala: Nombre de la sala (ej. "Sala A — Cardiología").
            color_sala:  Color identificativo de la sala.
            pacientes:   Lista de PacienteSala en esta sala.
        """
        # ── Encabezado de la sala ──
        frame_header = ctk.CTkFrame(
            self._frame_scroll,
            fg_color="#1A1A1A",
            corner_radius=8,
            height=36,
        )
        frame_header.pack(fill="x", padx=10, pady=(15, 5))
        frame_header.pack_propagate(False)

        # Barra de color lateral
        barra_color = ctk.CTkFrame(
            frame_header, width=4, fg_color=color_sala, corner_radius=2
        )
        barra_color.pack(side="left", fill="y", padx=(0, 10))

        # Nombre de la sala
        ctk.CTkLabel(
            frame_header,
            text=nombre_sala,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#FFFFFF",
        ).pack(side="left", padx=5, pady=5)

        # Cantidad de pacientes
        ctk.CTkLabel(
            frame_header,
            text=f"({len(pacientes)} pacientes)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#999999",
        ).pack(side="left", padx=5, pady=5)

        # ── Grid de tarjetas (3 columnas × 2 filas = 6 pacientes) ──
        frame_grid = ctk.CTkFrame(self._frame_scroll, fg_color="transparent")
        frame_grid.pack(fill="x", padx=5, pady=(0, 10))

        columnas = 3
        for indice, paciente in enumerate(pacientes):
            fila    = indice // columnas
            columna = indice % columnas

            # Configurar columnas para que se expandan uniformemente
            frame_grid.grid_columnconfigure(columna, weight=1)

            tarjeta = TarjetaPaciente(
                frame_grid,
                paciente,
                on_click_callback=self._on_tarjeta_click,
                on_ver_mas_callback=self._on_ver_mas,
                ancho=310,
                alto=132,
            )
            tarjeta.grid(row=fila, column=columna, padx=4, pady=4, sticky="nsew")
            self._tarjetas[paciente.id_paciente] = tarjeta

    # ==================================================================
    # MANEJO DE EVENTOS
    # ==================================================================
    def _on_tarjeta_click(self, paciente) -> None:
        """
        Se ejecuta cuando el usuario hace click en una tarjeta de paciente.
        Llama al callback de detalle si está configurado.
        """
        if self._on_ver_detalle:
            self._on_ver_detalle(paciente)

    # ==================================================================
    # MÉTODOS DE CONSULTA
    # ==================================================================
    @property
    def pacientes(self) -> list:
        """Lista de pacientes actualmente mostrados en el panel."""
        return list(self._pacientes)

    def tarjeta_por_id(self, id_paciente: str) -> TarjetaPaciente | None:
        """
        Obtiene la referencia a la tarjeta de un paciente por su ID.

        Args:
            id_paciente: ID del paciente.

        Returns:
            La instancia de TarjetaPaciente o None si no se encuentra.
        """
        return self._tarjetas.get(id_paciente)


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba visual del PanelSalas.
    Abre una ventana que muestra tarjetas de pacientes de sala generados
    aleatoriamente. Incluye botón Actualizar y resumen por estado.
    """
    from datos.generador import GeneradorDatos
    from datos.repositorio import RepositorioPacientes

    print("=" * 60)
    print("  PRUEBA VISUAL: PanelSalas")
    print("=" * 60)
    print("  Se abrirá una ventana con el panel de salas.")
    print("  Muestra tarjetas de pacientes internados.")
    print("  Haz click en una tarjeta para probar el callback.")
    print("  Usa el botón 'Actualizar' para refrescar las tarjetas.")
    print("  Cierra la ventana para terminar la prueba.")
    print("=" * 60)

    # Configurar apariencia
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Crear ventana
    ventana = ctk.CTk()
    ventana.title("GH — Panel de Salas (Prueba)")
    ventana.geometry("1280x750")
    ventana.minsize(900, 500)

    # Generar pacientes de prueba
    generador = GeneradorDatos(semilla=42)
    repo = RepositorioPacientes()
    repo.agregar_pacientes(generador.generar_pacientes_sala(cantidad=10))

    # Callback al hacer click en tarjeta
    def ver_detalle(paciente):
        print(f"\n>>> Ver detalle de: {paciente.nombre}")
        print(f"    ID: {paciente.id_paciente}")
        print(f"    Estado: {paciente.estado}")
        print(f"    Cama: {paciente.numero_cama}")
        print(f"    Signos: HR={paciente.signos_vitales.frecuencia_cardiaca:.0f}, "
              f"SpO2={paciente.signos_vitales.saturacion_oxigeno:.0f}%")

    # Callback al presionar volver
    def volver():
        print("\n>>> Botón Volver presionado")
        ventana.destroy()

    # Crear y mostrar el panel
    panel = PanelSalas(
        ventana,
        on_ver_detalle_callback=ver_detalle,
        on_volver_callback=volver,
    )
    panel.cargar_pacientes(repo.obtener_sala())

    ventana.mainloop()
