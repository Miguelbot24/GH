"""
Módulo: pantalla_inicio.py
Sprint 4 — Pantalla de bienvenida de la interfaz gráfica.

Define la clase PantallaInicio, que muestra la pantalla de bienvenida del
sistema GH con el logo, el nombre del hospital y un botón para iniciar
la simulación.

Dependencias previas necesarias:
    - config.py  (TEMA_APARIENCIA, TEMA_COLOR, ANCHO_VENTANA, ALTO_VENTANA)

Librería externa requerida:
    - customtkinter  (pip install customtkinter)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk

from config import (
    TEMA_APARIENCIA,
    TEMA_COLOR,
    ANCHO_VENTANA,
    ALTO_VENTANA,
    COLOR_CRITICO,
    COLOR_ESTABLE,
    COLORES_ESTADO,
    ESTADO_ESTABLE,
)


class PantallaInicio(ctk.CTkFrame):
    """
    Pantalla de bienvenida del sistema de Gestión Hospitalaria (GH).

    Muestra el nombre del hospital, un subtítulo descriptivo y un botón
    "Iniciar Sistema" que notifica a la aplicación principal mediante
    un callback para cambiar a la pantalla de paneles.

    Esta clase es un CTkFrame pensado para ser contenido dentro de la
    ventana principal (CTk). No crea su propia ventana; permite que
    main.py controle la navegación entre pantallas.
    """

    def __init__(
        self,
        parent,
        on_iniciar_callback=None,
        **kwargs,
    ):
        """
        Constructor de la pantalla de inicio.

        Args:
            parent:             Widget padre (normalmente la ventana CTk).
            on_iniciar_callback: Función a ejecutar cuando el usuario presione
                                "Iniciar Sistema". Recibe la instancia de
                                PantallaInicio como argumento.
        """
        super().__init__(parent, **kwargs)

        # Guardamos el callback para notificar a la app principal
        self._on_iniciar_callback = on_iniciar_callback

        # Configurar el frame para que ocupe todo el espacio del padre
        self._configurar_grid()

        # Construir los elementos visuales
        self._crear_widgets()

    # ==================================================================
    # CONFIGURACIÓN DE LAYOUT
    # ==================================================================
    def _configurar_grid(self) -> None:
        """
        Configura el sistema de grid del frame para que los widgets
        se expandan y centren correctamente al redimensionar la ventana.

        NOTA: No llama a pack()/grid() sobre self. El posicionamiento
        de esta pantalla lo controla main.py mediante tkraise().
        """
        # Tres filas: superior (espacio), central (contenido), inferior (espacio)
        self.grid_rowconfigure(0, weight=1)  # Espacio superior elástico
        self.grid_rowconfigure(1, weight=0)  # Contenido (tamaño fijo)
        self.grid_rowconfigure(2, weight=0)  # Espacio pequeño
        self.grid_rowconfigure(3, weight=1)  # Espacio inferior elástico

        # Una columna centrada
        self.grid_columnconfigure(0, weight=1)

    # ==================================================================
    # CREACIÓN DE WIDGETS
    # ==================================================================
    def _crear_widgets(self) -> None:
        """
        Construye todos los elementos visuales de la pantalla de inicio:
        logo decorativo, título, subtítulo y botón de inicio.
        """
        # --- Contenedor central para agrupar todo el contenido ---
        contenedor = ctk.CTkFrame(self, fg_color="transparent")
        contenedor.grid(row=1, column=0, padx=40, pady=20)

        # --- Símbolo médico decorativo (cruz) ---
        self._crear_simbolo_medico(contenedor)

        # --- Título principal ---
        titulo = ctk.CTkLabel(
            contenedor,
            text="GESTIÓN HOSPITALARIA",
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"),
            text_color="#FFFFFF",
        )
        titulo.pack(pady=(10, 5))

        # --- Subtítulo ---
        subtitulo = ctk.CTkLabel(
            contenedor,
            text="Sistema de Monitoreo y Atención de Pacientes",
            font=ctk.CTkFont(family="Segoe UI", size=18),
            text_color="#B0B0B0",
        )
        subtitulo.pack(pady=(0, 5))

        # --- Versión / siglas ---
        version = ctk.CTkLabel(
            contenedor,
            text="GH v1.0 — Proyecto Universitario POO",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#707070",
        )
        version.pack(pady=(0, 30))

        # --- Línea separadora decorativa ---
        separador = ctk.CTkFrame(
            contenedor,
            height=2,
            fg_color=COLOR_ESTABLE,
            corner_radius=1,
        )
        separador.pack(fill="x", padx=60, pady=(0, 30))

        # --- Botón "Iniciar Sistema" ---
        btn_iniciar = ctk.CTkButton(
            contenedor,
            text="INICIAR SISTEMA",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            height=55,
            width=280,
            corner_radius=12,
            fg_color=COLOR_ESTABLE,
            hover_color="#2E7D32",
            text_color="#FFFFFF",
            command=self._on_iniciar_click,
        )
        btn_iniciar.pack(pady=(0, 15))

        # --- Mensaje de ayuda debajo del botón ---
        ayuda = ctk.CTkLabel(
            contenedor,
            text="Presione el botón para ingresar al sistema de monitoreo",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#606060",
        )
        ayuda.pack(pady=(0, 10))

        # --- Pie de página ---
        pie = ctk.CTkLabel(
            contenedor,
            text="© 2026 — Facultad de Ingeniería",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#505050",
        )
        pie.pack(pady=(20, 0))

    def _crear_simbolo_medico(self, parent: ctk.CTkFrame) -> None:
        """
        Crea un símbolo decorativo con forma de cruz médica usando frames
        de CustomTkinter (sin necesidad de imágenes externas).
        """
        contenedor_cruz = ctk.CTkFrame(
            parent, fg_color="transparent", width=80, height=80
        )
        contenedor_cruz.pack(pady=(0, 10))
        contenedor_cruz.pack_propagate(False)

        # Barra horizontal de la cruz
        barra_h = ctk.CTkFrame(
            contenedor_cruz,
            width=60,
            height=18,
            fg_color=COLOR_ESTABLE,
            corner_radius=4,
        )
        barra_h.place(relx=0.5, rely=0.5, anchor="center")

        # Barra vertical de la cruz
        barra_v = ctk.CTkFrame(
            contenedor_cruz,
            width=18,
            height=60,
            fg_color=COLOR_ESTABLE,
            corner_radius=4,
        )
        barra_v.place(relx=0.5, rely=0.5, anchor="center")

    # ==================================================================
    # MANEJO DE EVENTOS
    # ==================================================================
    def _on_iniciar_click(self) -> None:
        """
        Se ejecuta cuando el usuario presiona el botón "Iniciar Sistema".
        Invoca el callback registrado para que la app principal cambie
        de pantalla.
        """
        if self._on_iniciar_callback is not None:
            self._on_iniciar_callback(self)

    # ==================================================================
    # MÉTODO ESTÁTICO PARA PRUEBA RÁPIDA
    # ==================================================================
    @staticmethod
    def probar(ancho: int = ANCHO_VENTANA, alto: int = ALTO_VENTANA) -> None:
        """
        Abre una ventana independiente con la pantalla de inicio para
        probarla visualmente sin necesidad del resto de la app.

        Args:
            ancho: Ancho de la ventana de prueba.
            alto:  Alto de la ventana de prueba.
        """
        ventana = ctk.CTk()
        ventana.title("GH — Pantalla de Inicio (Prueba)")
        ventana.geometry(f"{ancho}x{alto}")
        ventana.minsize(800, 600)

        # Configurar apariencia
        ctk.set_appearance_mode(TEMA_APARIENCIA)
        ctk.set_default_color_theme(TEMA_COLOR)

        pantalla = PantallaInicio(
            ventana,
            on_iniciar_callback=lambda p: print(">>> Callback: Iniciar Sistema presionado <<<"),
        )

        ventana.mainloop()


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba visual de la pantalla de inicio.
    Abre una ventana independiente con la pantalla de bienvenida.
    Al presionar "Iniciar Sistema", se imprime un mensaje en consola.
    Cierra la ventana para terminar la prueba.
    """
    print("=" * 60)
    print("  PRUEBA VISUAL: PantallaInicio")
    print("=" * 60)
    print("  Se abrirá una ventana con la pantalla de bienvenida.")
    print("  Presiona 'Iniciar Sistema' para probar el callback.")
    print("  Cierra la ventana para terminar la prueba.")
    print("=" * 60)

    PantallaInicio.probar()
