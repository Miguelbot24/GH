"""
Módulo: componentes.py
Sprint 4 — Widgets reutilizables de la interfaz gráfica.

Define componentes visuales comunes usados en múltiples paneles del sistema:
  - TarjetaPaciente:   tarjeta individual con datos del paciente y borde de color.
  - BadgeEstado:       etiqueta de estado clínico con color de fondo.
  - IndicadorSigno:    minitarjeta que muestra un signo vital con valor y unidad.

Dependencias previas necesarias:
    - config.py  (COLORES_ESTADO, COLORES_TEXTO_ESTADO, NOMBRES_SIGNOS, UNIDADES_SIGNOS)

Librería externa requerida:
    - customtkinter  (pip install customtkinter)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from PIL import Image

from config import (
    COLORES_ESTADO,
    COLORES_TEXTO_ESTADO,
    NOMBRES_SIGNOS,
    UNIDADES_SIGNOS,
    ANCHO_TARJETA,
    ALTO_TARJETA,
    ICONOS_AVATAR,
    ESTADO_ATENCION,
    COLOR_CRITICO,
)


class BadgeEstado(ctk.CTkFrame):
    """
    Pequeña etiqueta rectangular que muestra el estado clínico del paciente
    con un color de fondo semántico (rojo = CRITICO, verde = ESTABLE, etc.).

    Se usa dentro de TarjetaPaciente y en el panel de detalle.
    """

    def __init__(self, parent, estado: str, **kwargs):
        """
        Constructor del BadgeEstado.

        Args:
            parent: Widget padre donde se colocará el badge.
            estado: Estado clínico (CRITICO, PRUDENTE, etc.).
        """
        # Obtener colores según el estado
        color_fondo = COLORES_ESTADO.get(estado, "#F5F5F5")
        color_texto = COLORES_TEXTO_ESTADO.get(estado, "#000000")

        super().__init__(
            parent,
            fg_color=color_fondo,
            corner_radius=8,
            width=90,
            height=28,
            **kwargs,
        )
        # Evitar que el frame se encoja al contenido
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Etiqueta con el nombre del estado
        self._label = ctk.CTkLabel(
            self,
            text=estado,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=color_texto,
        )
        self._label.place(relx=0.5, rely=0.5, anchor="center")

    def actualizar_estado(self, nuevo_estado: str) -> None:
        """
        Cambia el color y texto del badge para reflejar un nuevo estado.

        Args:
            nuevo_estado: El nuevo estado clínico a mostrar.
        """
        color_fondo = COLORES_ESTADO.get(nuevo_estado, "#F5F5F5")
        color_texto = COLORES_TEXTO_ESTADO.get(nuevo_estado, "#000000")
        self.configure(fg_color=color_fondo)
        self._label.configure(text=nuevo_estado, text_color=color_texto)


class IndicadorSigno(ctk.CTkFrame):
    """
    Minitarjeta que muestra el valor actual de un signo vital con su nombre
    y unidad de medida.

    Se usa en TarjetaPaciente para mostrar HR, SpO2, PA y Temp de un vistazo.
    """

    def __init__(self, parent, nombre_signo: str, valor: float = 0.0, **kwargs):
        """
        Constructor del IndicadorSigno.

        Args:
            parent:       Widget padre.
            nombre_signo: Clave interna del signo (ej. "frecuencia_cardiaca").
            valor:        Valor numérico actual del signo.
        """
        super().__init__(
            parent,
            fg_color="#2B2B2B",
            corner_radius=6,
            **kwargs,
        )

        self._nombre_signo = nombre_signo

        # Etiqueta con el nombre abreviado del signo
        nombre_corto = self._nombre_corto(nombre_signo)
        self._label_nombre = ctk.CTkLabel(
            self,
            text=nombre_corto,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#888888",
        )
        self._label_nombre.pack(pady=(4, 0))

        # Valor del signo (grande)
        self._unidad = UNIDADES_SIGNOS.get(nombre_signo, "")
        self._label_valor = ctk.CTkLabel(
            self,
            text=self._formatear_valor(valor),
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color="#FFFFFF",
        )
        self._label_valor.pack(pady=(0, 4))

    def _nombre_corto(self, nombre_signo: str) -> str:
        """Devuelve una versión abreviada del nombre del signo."""
        abreviaturas = {
            "frecuencia_cardiaca":     "HR",
            "frecuencia_respiratoria": "RR",
            "saturacion_oxigeno":      "SpO2",
            "presion_sistolica":       "SYS",
            "presion_diastolica":      "DIA",
            "temperatura":             "TEMP",
        }
        return abreviaturas.get(nombre_signo, nombre_signo[:4].upper())

    def _formatear_valor(self, valor: float) -> str:
        """Formatea el valor: entero para todos los signos salvo temperatura."""
        if isinstance(valor, (int, float)):
            if valor == 0.0:
                return "--"
            if self._nombre_signo == "temperatura":
                return f"{valor:.1f}"
            return f"{int(round(valor))}"
        return str(valor)

    def actualizar_valor(self, nuevo_valor: float) -> None:
        """
        Actualiza el valor mostrado en el indicador.

        Args:
            nuevo_valor: Nuevo valor numérico del signo vital.
        """
        self._label_valor.configure(text=self._formatear_valor(nuevo_valor))


class TarjetaPaciente(ctk.CTkFrame):
    """
    Tarjeta visual que representa a un paciente en el panel de salas
    o en el panel de emergencias.

    Muestra:
      - Borde lateral de color según el estado clínico.
      - Avatar (ícono de persona según edad/género).
      - Nombre, edad y ubicación (cama o tiempo de espera).
      - Badge de estado clínico.
      - Indicadores de signos vitales (HR, SpO2, PA, Temp).

    Es cliqueable: al hacer click llama a un callback para abrir el
    detalle del paciente.
    """

    def __init__(
        self,
        parent,
        paciente,
        on_click_callback=None,
        on_ver_mas_callback=None,
        ancho: int = ANCHO_TARJETA,
        alto:  int = ALTO_TARJETA,
        **kwargs,
    ):
        """
        Constructor de la TarjetaPaciente.

        Args:
            parent:            Widget padre (el panel donde se coloca).
            paciente:          Instancia de Paciente (o subclase) a representar.
            on_click_callback: Función a llamar al hacer click en la tarjeta.
                               Recibe el paciente como argumento.
            on_ver_mas_callback: Función a llamar al presionar "Ver más".
                                 Recibe el paciente como argumento.
            ancho:             Ancho de la tarjeta en píxeles.
            alto:              Alto de la tarjeta en píxeles.
        """
        self._paciente = paciente
        self._on_click = on_click_callback
        self._on_ver_mas = on_ver_mas_callback

        # Color del estado actual para el borde lateral
        color_borde = COLORES_ESTADO.get(paciente.estado, "#757575")

        super().__init__(
            parent,
            width=ancho,
            height=alto,
            corner_radius=10,
            fg_color="#1E1E1E",
            border_width=3,
            border_color=color_borde,
            **kwargs,
        )
        # Evitar que la tarjeta cambie de tamaño según el contenido
        self.pack_propagate(False)
        self.grid_propagate(False)

        # Vincular evento de click en toda la tarjeta
        self.bind("<Button-1>", self._on_click_event)
        # También vincular a los hijos para que el click funcione
        # en cualquier parte de la tarjeta
        self._vincular_clicks(self)

        # Construir el contenido interno de la tarjeta
        self._crear_contenido()

    # ==================================================================
    # CONSTRUCCIÓN DEL CONTENIDO
    # ==================================================================
    def _crear_contenido(self) -> None:
        """
        Construye todos los elementos visuales dentro de la tarjeta:
        avatar, datos del paciente, badge de estado e indicadores.
        """
        p = self._paciente

        # --- Fila superior: avatar + nombre + estado ---
        fila_superior = ctk.CTkFrame(self, fg_color="transparent")
        fila_superior.pack(fill="x", padx=10, pady=(8, 2))

        # Avatar (círculo con iniciales si no hay imagen)
        self._crear_avatar(fila_superior)

        # Indicador de alerta (círculo rojo parpadeante, inicialmente oculto)
        self._indicador_alerta = ctk.CTkFrame(
            fila_superior,
            width=12, height=12,
            fg_color=COLOR_CRITICO,
            corner_radius=6,
        )
        self._indicador_alerta.pack(side="left", padx=(4, 0))
        self._indicador_alerta.pack_forget()
        self._parpadeo_id = None

        # Contenedor de texto (nombre, edad, ubicación)
        contenedor_texto = ctk.CTkFrame(fila_superior, fg_color="transparent")
        contenedor_texto.pack(side="left", padx=(8, 0), fill="x", expand=True)

        # Nombre del paciente
        self._label_nombre = ctk.CTkLabel(
            contenedor_texto,
            text=p.nombre[:22] + ("..." if len(p.nombre) > 22 else ""),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#FFFFFF",
            anchor="w",
        )
        self._label_nombre.pack(anchor="w")

        # Edad y ubicación
        tipo_info = self._obtener_info_ubicacion()
        self._label_info = ctk.CTkLabel(
            contenedor_texto,
            text=f"{p.edad} años  •  {tipo_info}",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#999999",
            anchor="w",
        )
        self._label_info.pack(anchor="w")

        # Badge de estado (a la derecha)
        self._badge = BadgeEstado(fila_superior, p.estado)
        self._badge.pack(side="right", padx=(5, 0))

        # --- Separador sutil ---
        sep = ctk.CTkFrame(self, height=1, fg_color="#333333")
        sep.pack(fill="x", padx=10, pady=(6, 4))

        # --- Fila inferior: indicadores de signos vitales ---
        fila_signos = ctk.CTkFrame(self, fg_color="transparent")
        fila_signos.pack(fill="x", padx=8, pady=(0, 6))

        signos = p.signos_vitales

        # HR (frecuencia cardíaca)
        hr = IndicadorSigno(fila_signos, "frecuencia_cardiaca",
                           signos.frecuencia_cardiaca)
        hr.pack(side="left", padx=2, fill="x", expand=True)

        # SpO2
        spo2 = IndicadorSigno(fila_signos, "saturacion_oxigeno",
                             signos.saturacion_oxigeno)
        spo2.pack(side="left", padx=2, fill="x", expand=True)

        # PA (presión arterial — mostramos sistólica)
        pa = IndicadorSigno(fila_signos, "presion_sistolica",
                           signos.presion_sistolica)
        pa.pack(side="left", padx=2, fill="x", expand=True)

        # Temperatura
        temp = IndicadorSigno(fila_signos, "temperatura",
                             signos.temperatura)
        temp.pack(side="left", padx=2, fill="x", expand=True)

        # Botón "Ver más" (si hay callback)
        if self._on_ver_mas:
            btn_ver_mas = ctk.CTkButton(
                fila_signos,
                text="Ver mas",
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                width=60,
                height=24,
                corner_radius=5,
                fg_color="#444444",
                hover_color="#666666",
                text_color="#CCCCCC",
                command=self._on_click_ver_mas,
            )
            btn_ver_mas.pack(side="left", padx=2)

        # Guardar referencias a los indicadores para poder actualizarlos
        self._indicadores = {
            "frecuencia_cardiaca": hr,
            "saturacion_oxigeno":  spo2,
            "presion_sistolica":   pa,
            "temperatura":         temp,
        }

    def _crear_avatar(self, parent: ctk.CTkFrame) -> None:
        """
        Crea un círculo con las iniciales del paciente como avatar.
        Si existe un archivo de imagen para el tipo de avatar, intenta cargarlo.

        Args:
            parent: Frame donde se colocará el avatar.
        """
        p = self._paciente
        iniciales = self._obtener_iniciales(p.nombre)

        # Intentar cargar imagen de avatar desde archivo
        ruta_avatar = p.ruta_avatar if hasattr(p, 'ruta_avatar') else ""
        imagen_avatar = None

        if ruta_avatar and os.path.exists(ruta_avatar):
            try:
                img = Image.open(ruta_avatar)
                img = img.resize((38, 38), Image.LANCZOS)
                imagen_avatar = ctk.CTkImage(light_image=img, dark_image=img, size=(38, 38))
            except Exception:
                imagen_avatar = None

        # Crear el contenedor circular
        color_fondo = COLORES_ESTADO.get(p.estado, "#757575")
        avatar_frame = ctk.CTkFrame(
            parent,
            width=42,
            height=42,
            fg_color=color_fondo,
            corner_radius=21,  # Radio = mitad del ancho = círculo
        )
        avatar_frame.pack(side="left")
        avatar_frame.pack_propagate(False)

        if imagen_avatar:
            # Mostrar imagen
            lbl_img = ctk.CTkLabel(avatar_frame, image=imagen_avatar, text="")
            lbl_img.place(relx=0.5, rely=0.5, anchor="center")
        else:
            # Mostrar iniciales
            lbl_iniciales = ctk.CTkLabel(
                avatar_frame,
                text=iniciales,
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color="#FFFFFF",
            )
            lbl_iniciales.place(relx=0.5, rely=0.5, anchor="center")

    # ==================================================================
    # MÉTODOS AUXILIARES
    # ==================================================================
    def _obtener_iniciales(self, nombre: str) -> str:
        """Extrae las iniciales del nombre del paciente (máximo 2 letras)."""
        partes = nombre.split()
        if len(partes) >= 2:
            return (partes[0][0] + partes[-1][0]).upper()
        elif len(partes) == 1:
            return partes[0][:2].upper()
        return "??"

    def _obtener_info_ubicacion(self) -> str:
        """
        Devuelve una cadena con información de ubicación según el tipo
        de paciente (cama para sala, tiempo de espera para emergencia).
        """
        tipo = self._paciente.__class__.__name__
        if tipo == "PacienteSala":
            return f"Cama {self._paciente.numero_cama}"
        elif tipo == "PacienteEmergencia":
            espera = self._paciente.tiempo_espera_legible()
            return f"Espera: {espera}"
        return ""

    def _vincular_clicks(self, widget) -> None:
        """
        Vincula recursivamente el evento <Button-1> a todos los widgets
        hijos para que hacer click en cualquier parte de la tarjeta
        llame al callback.
        """
        for hijo in widget.winfo_children():
            hijo.bind("<Button-1>", self._on_click_event)
            self._vincular_clicks(hijo)

    def _on_click_event(self, event=None) -> None:
        """Maneja el evento de click en la tarjeta."""
        if self._on_click:
            self._on_click(self._paciente)

    def _on_click_ver_mas(self) -> None:
        """Maneja el evento del botón 'Ver más'."""
        if self._on_ver_mas:
            self._on_ver_mas(self._paciente)

    # ==================================================================
    # INDICADOR DE ALERTA PARPADEANTE
    # ==================================================================
    def _parpadeo_toggle(self) -> None:
        """Alterna la visibilidad del círculo rojo de alerta."""
        if not self._indicador_alerta.winfo_exists():
            self._parpadeo_id = None
            return
        try:
            info = self._indicador_alerta.pack_info()
            self._indicador_alerta.pack_forget()
        except Exception:
            self._indicador_alerta.pack(side="left", padx=(4, 0))
        self._parpadeo_id = self.after(500, self._parpadeo_toggle)

    def activar_parpadeo(self) -> None:
        """Activa el parpadeo del círculo rojo de alerta."""
        if self._parpadeo_id is not None:
            return
        self._indicador_alerta.pack(side="left", padx=(4, 0))
        self._parpadeo_id = self.after(500, self._parpadeo_toggle)

    def desactivar_parpadeo(self) -> None:
        """Detiene el parpadeo y oculta el círculo rojo."""
        if self._parpadeo_id is not None:
            self.after_cancel(self._parpadeo_id)
            self._parpadeo_id = None
        try:
            self._indicador_alerta.pack_forget()
        except Exception:
            pass

    # ==================================================================
    # ACTUALIZACIÓN DE LA TARJETA
    # ==================================================================
    def actualizar(self) -> None:
        """
        Actualiza todos los elementos visuales de la tarjeta con los
        valores actuales del paciente (estado, signos vitales, colores).

        Útil cuando el monitor cambia el estado o los signos del paciente
        y se necesita reflejar el cambio en la interfaz.
        """
        p = self._paciente
        color_borde = COLORES_ESTADO.get(p.estado, "#757575")

        # Actualizar borde
        self.configure(border_color=color_borde)

        # Actualizar badge de estado
        self._badge.actualizar_estado(p.estado)

        # Actualizar indicador de alerta parpadeante
        if p.estado == ESTADO_ATENCION and self._parpadeo_id is None:
            self.activar_parpadeo()
        elif p.estado != ESTADO_ATENCION and self._parpadeo_id is not None:
            self.desactivar_parpadeo()

        # Actualizar indicadores de signos vitales
        signos = p.signos_vitales
        self._indicadores["frecuencia_cardiaca"].actualizar_valor(
            signos.frecuencia_cardiaca
        )
        self._indicadores["saturacion_oxigeno"].actualizar_valor(
            signos.saturacion_oxigeno
        )
        self._indicadores["presion_sistolica"].actualizar_valor(
            signos.presion_sistolica
        )
        self._indicadores["temperatura"].actualizar_valor(
            signos.temperatura
        )

    # ==================================================================
    # PROPIEDADES
    # ==================================================================
    @property
    def paciente(self):
        """El paciente asociado a esta tarjeta."""
        return self._paciente


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba visual de los componentes.
    Abre una ventana con varias tarjetas de paciente de ejemplo,
    incluyendo diferentes estados clínicos para verificar los colores
    y la disposición de los widgets.
    """
    from datos.generador import GeneradorDatos
    from modelos.signos_vitales import SignosVitales

    print("=" * 60)
    print("  PRUEBA VISUAL: Componentes (TarjetaPaciente)")
    print("=" * 60)
    print("  Se abrirá una ventana con tarjetas de ejemplo.")
    print("  Cada tarjeta muestra un paciente con distinto estado.")
    print("  Haz click en una tarjeta para probar el callback.")
    print("  Cierra la ventana para terminar la prueba.")
    print("=" * 60)

    # Crear ventana de prueba
    ventana = ctk.CTk()
    ventana.title("GH — Prueba de Componentes")
    ventana.geometry("1000x550")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Frame principal con scroll por si hay muchas tarjetas
    frame_principal = ctk.CTkScrollableFrame(ventana)
    frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

    # --- Configurar grid para las tarjetas ---
    frame_principal.grid_columnconfigure(0, weight=1)
    frame_principal.grid_columnconfigure(1, weight=1)
    frame_principal.grid_columnconfigure(2, weight=1)

    # --- Generar pacientes de ejemplo ---
    generador = GeneradorDatos(semilla=42)

    # Función callback al hacer click
    def al_hacer_click(paciente):
        print(f"\n>>> Click en tarjeta: {paciente.nombre} ({paciente.id_paciente})")
        print(f"    Estado: {paciente.estado} | Prioridad: {paciente.prioridad}")

    # --- Crear tarjetas con distintos estados ---
    fila = 0
    columna = 0

    # Generar 6 pacientes de sala con estados variados
    pacientes = generador.generar_pacientes_sala(cantidad=3)
    pacientes += generador.generar_pacientes_emergencia(cantidad=3)

    # Crear manualmente pacientes con estados específicos para la demo
    from modelos.paciente_sala import PacienteSala
    from modelos.paciente_emergencia import PacienteEmergencia

    # Paciente ESTABLE
    p_estable = PacienteSala("Roberto Alvarado", 45, "Masculino", 201, "General")
    p_estable.signos_vitales = SignosVitales(72, 16, 98, 118, 74, 36.5)

    # Paciente CRITICO
    p_critico = PacienteEmergencia("Juana Ibarra", 67, "Femenino",
                                    prioridad_administrativa=5,
                                    motivo_consulta="Infarto agudo")
    p_critico.signos_vitales = SignosVitales(140, 30, 82, 68, 40, 39.8)

    # Agregar a la lista
    pacientes.extend([p_estable, p_critico])

    for paciente in pacientes:
        tarjeta = TarjetaPaciente(
            frame_principal,
            paciente,
            on_click_callback=al_hacer_click,
            ancho=280,
            alto=130,
        )
        tarjeta.grid(row=fila, column=columna, padx=8, pady=8, sticky="nsew")

        columna += 1
        if columna >= 3:
            columna = 0
            fila += 1

    # --- Badge de ejemplo adicional ---
    frame_badges = ctk.CTkFrame(ventana, fg_color="transparent")
    frame_badges.pack(fill="x", padx=20, pady=(0, 10))

    ctk.CTkLabel(
        frame_badges,
        text="Badges de estado:",
        font=ctk.CTkFont(size=12),
        text_color="#888888",
    ).pack(side="left", padx=(0, 10))

    for estado in ["CRITICO", "ATENCION", "PRUDENTE", "NO_CRITICO", "ESTABLE", "FALLECIDO", "SIN_DATOS"]:
        badge = BadgeEstado(frame_badges, estado)
        badge.pack(side="left", padx=4)

    ventana.mainloop()
