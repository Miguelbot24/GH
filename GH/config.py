"""
Módulo de configuración global del proyecto Gestión Hospitalaria (GH).

Define todas las constantes que usarán los demás módulos:
  - Estados clínicos de los pacientes (6 estados).
  - Colores visuales asociados a cada estado.
  - Rangos normales y umbrales de clasificación para cada signo vital.
  - Parámetros de simulación (cantidad de pacientes, intervalos, etc.).
  - Rutas a los activos multimedia (iconos, sonidos).

Al centralizar estas definiciones en un solo archivo, cualquier cambio
en umbrales clínicos o colores se propaga automáticamente a toda la app.
"""

import os

# ============================================================================
# 1. ESTADOS CLÍNICOS — Separados por área
# ============================================================================
# El sistema ya NO usa estados universales. Cada área tiene su propio
# conjunto exclusivo. Ningún estado de sala aparece en emergencias y viceversa.
# FALLECIDO es el único estado universal (aplicable a cualquier paciente).

# ──── Estados exclusivos del ÁREA DE SALAS (4 estados) ────
ESTADO_SIN_DATOS = "SIN_DATOS"   # Desconexión / sin señal del monitor [SALA]
ESTADO_ESTABLE   = "ESTABLE"     # Parámetros dentro del rango normal [SALA]
ESTADO_PRUDENTE  = "PRUDENTE"    # Parámetros en zona de atención de rutina [SALA]
ESTADO_ATENCION  = "ATENCION"    # Parámetros fuera del margen de PRUDENTE [SALA]

# Tupla de estados del área de salas para iteraciones y validaciones
ESTADOS_SALA = (
    ESTADO_SIN_DATOS,
    ESTADO_ESTABLE,
    ESTADO_PRUDENTE,
    ESTADO_ATENCION,
)

# ──── Estados exclusivos del ÁREA DE EMERGENCIAS (2 estados) ────
ESTADO_NO_CRITICO = "NO_CRITICO"  # Paciente estable o en espera [EMERGENCIA]
ESTADO_CRITICO    = "CRITICO"     # Condición crítica, atención inmediata [EMERGENCIA]

# Tupla de estados del área de emergencias para iteraciones y validaciones
ESTADOS_EMERGENCIA = (
    ESTADO_NO_CRITICO,
    ESTADO_CRITICO,
)

# ──── Estado universal (aplicable a cualquier área) ────
ESTADO_FALLECIDO = "FALLECIDO"   # Sin actividad vital [UNIVERSAL]

# ──── Tipos de egreso (Área de Egresos) ────
TIPO_EGRESO_ALTA = "DADO_DE_ALTA"  # Paciente dado de alta médica
TIPO_EGRESO_FUGA = "FUGADO"        # Paciente que abandonó sin completar atención

# Tupla de tipos de egreso para iteraciones y validaciones
ESTADOS_EGRESO = (
    TIPO_EGRESO_ALTA,
    TIPO_EGRESO_FUGA,
)

# Colores visuales para tipos de egreso
COLOR_EGRESO_ALTA = "#4CAF50"   # Verde — alta satisfactoria
COLOR_EGRESO_FUGA = "#FF9800"   # Naranja — fuga/abandono

COLORES_EGRESO = {
    TIPO_EGRESO_ALTA: COLOR_EGRESO_ALTA,
    TIPO_EGRESO_FUGA: COLOR_EGRESO_FUGA,
}

# Prioridad numérica para ordenar pacientes en cola (mayor = más urgente)
# Los valores de prioridad se comparan entre áreas; CRITICO (emergencia)
# es el más alto, seguido de ATENCION (sala).
PRIORIDAD_ESTADO = {
    ESTADO_CRITICO:    5,
    ESTADO_ATENCION:   4,
    ESTADO_PRUDENTE:   3,
    ESTADO_ESTABLE:    2,
    ESTADO_NO_CRITICO: 1,
    ESTADO_FALLECIDO:  1,
    ESTADO_SIN_DATOS:  0,
}

# ============================================================================
# 2. COLORES VISUALES
# ============================================================================
# Cada estado tiene un color hexadecimal asociado para la interfaz gráfica.
# Se usan en tarjetas de pacientes, badges, alertas, etc.

COLOR_CRITICO     = "#D32F2F"   # Rojo intenso — CRITICO [EMERGENCIA]
COLOR_ATENCION    = "#c94b3c"   # Rojo atenuado — ATENCION [SALA]
COLOR_PRUDENTE    = "#F57C00"   # Naranja — PRUDENTE [SALA]
COLOR_NO_CRITICO  = "#9e671e"   # Marrón — NO_CRITICO [EMERGENCIA]
COLOR_ESTABLE     = "#388E3C"   # Verde — ESTABLE [SALA]
COLOR_FALLECIDO   = "#757575"   # Gris medio — FALLECIDO [UNIVERSAL]
COLOR_SIN_DATOS   = "#F5F5F5"   # Blanco humo — SIN_DATOS [SALA]

# Diccionario que mapea cada estado a su color hexadecimal
COLORES_ESTADO = {
    ESTADO_CRITICO:     COLOR_CRITICO,
    ESTADO_ATENCION:    COLOR_ATENCION,
    ESTADO_PRUDENTE:    COLOR_PRUDENTE,
    ESTADO_NO_CRITICO:  COLOR_NO_CRITICO,
    ESTADO_ESTABLE:     COLOR_ESTABLE,
    ESTADO_FALLECIDO:   COLOR_FALLECIDO,
    ESTADO_SIN_DATOS:   COLOR_SIN_DATOS,
}

# Colores de texto para cada fondo (aseguran contraste legible)
COLORES_TEXTO_ESTADO = {
    ESTADO_CRITICO:     "#FFFFFF",  # Blanco sobre rojo
    ESTADO_ATENCION:    "#FFFFFF",  # Blanco sobre rojo atenuado
    ESTADO_PRUDENTE:    "#FFFFFF",  # Blanco sobre naranja
    ESTADO_NO_CRITICO:  "#FFFFFF",  # Blanco sobre marrón
    ESTADO_ESTABLE:     "#FFFFFF",  # Blanco sobre verde
    ESTADO_FALLECIDO:   "#FFFFFF",  # Blanco sobre gris
    ESTADO_SIN_DATOS:   "#212121",  # Gris oscuro sobre blanco humo
}

# ============================================================================
# 3. NOMBRES LEGIBLES DE LOS SIGNOS VITALES
# ============================================================================
# Se usan para etiquetas en la interfaz y en mensajes de alerta.

NOMBRES_SIGNOS = {
    "frecuencia_cardiaca":     "Frecuencia Cardíaca (HR)",
    "frecuencia_respiratoria": "Frecuencia Respiratoria (RR)",
    "saturacion_oxigeno":      "Saturación de Oxígeno (SpO2)",
    "presion_sistolica":       "Presión Sistólica",
    "presion_diastolica":      "Presión Diastólica",
    "temperatura":             "Temperatura",
}

# Unidades de medida de cada signo vital
UNIDADES_SIGNOS = {
    "frecuencia_cardiaca":     "bpm",
    "frecuencia_respiratoria": "rpm",
    "saturacion_oxigeno":      "%",
    "presion_sistolica":       "mmHg",
    "presion_diastolica":      "mmHg",
    "temperatura":             "°C",
}

# ============================================================================
# 4. RANGOS NORMALES DE SIGNOS VITALES
# ============================================================================
# Cada tupla contiene (valor_mínimo_normal, valor_máximo_normal).

RANGOS_NORMALES = {
    "frecuencia_cardiaca":     (60, 100),
    "frecuencia_respiratoria": (12, 20),
    "saturacion_oxigeno":      (95, 100),
    "presion_sistolica":       (100, 140),
    "presion_diastolica":      (60, 80),
    "temperatura":             (36.5, 37.5),
}

# ============================================================================
# 5. UMBRALES DE CLASIFICACIÓN — Separados por área
# ============================================================================
# Cada área tiene sus propios umbrales. El monitor elige cuál usar según
# el tipo de paciente (PacienteSala vs PacienteEmergencia).
#
# Estructura: UMBRALES[signo][estado] = [(min1, max1), (min2, max2), ...]
# El primer rango que contenga el valor del signo determina su clasificación.

# ──── Umbrales para el ÁREA DE SALAS ────
# Estados: FALLECIDO, ATENCION, PRUDENTE, ESTABLE
# PRUDENTE absorbe lo que antes era BASICO + PRUDENTE
UMBRALES_SALA = {
    "frecuencia_cardiaca": {
        ESTADO_FALLECIDO: [(0, 0)],
        ESTADO_ATENCION:  [(1, 56),  (104, 300)],
        ESTADO_PRUDENTE:  [(57, 59), (101, 103)],
        ESTADO_ESTABLE:   [(60, 100)],
    },
    "frecuencia_respiratoria": {
        ESTADO_FALLECIDO: [(0, 0)],
        ESTADO_ATENCION:  [(1, 8),   (24, 60)],
        ESTADO_PRUDENTE:  [(9, 11),  (21, 23)],
        ESTADO_ESTABLE:   [(12, 20)],
    },
    "saturacion_oxigeno": {
        ESTADO_FALLECIDO: [(0, 0)],
        ESTADO_ATENCION:  [(1, 91)],
        ESTADO_PRUDENTE:  [(92, 94)],
        ESTADO_ESTABLE:   [(95, 100)],
    },
    "presion_sistolica": {
        ESTADO_FALLECIDO: [(0, 0)],
        ESTADO_ATENCION:  [(1, 96),  (144, 300)],
        ESTADO_PRUDENTE:  [(97, 99), (141, 143)],
        ESTADO_ESTABLE:   [(100, 140)],
    },
    "presion_diastolica": {
        ESTADO_FALLECIDO: [(0, 0)],
        ESTADO_ATENCION:  [(1, 56),  (84, 200)],
        ESTADO_PRUDENTE:  [(57, 59), (81, 83)],
        ESTADO_ESTABLE:   [(60, 80)],
    },
    "temperatura": {
        ESTADO_FALLECIDO: [(0, 0)],
        ESTADO_ATENCION:  [(1, 36.1),  (37.9, 45)],
        ESTADO_PRUDENTE:  [(36.2, 36.4), (37.6, 37.8)],
        ESTADO_ESTABLE:   [(36.5, 37.5)],
    },
}

# Límites duros de variación para área de salas:
# ningún signo puede cruzar estos valores durante un tick normal.
# Solo el simulador de emergencia puede superarlos.
LIMITES_VARIACION_SALA = {
    "frecuencia_cardiaca":     (57, 103),
    "frecuencia_respiratoria": (9, 23),
    "saturacion_oxigeno":      (92, 100),
    "presion_sistolica":       (97, 143),
    "presion_diastolica":      (57, 83),
    "temperatura":             (36.2, 37.8),
}

# ──── Umbrales para el ÁREA DE EMERGENCIAS ────
# Estados: FALLECIDO, CRITICO, NO_CRITICO
# CRITICO = zona crítica. NO_CRITICO = todo lo demás (incluye normales y leves)
UMBRALES_EMERGENCIA = {
    "frecuencia_cardiaca": {
        ESTADO_FALLECIDO:  [(0, 0)],
        ESTADO_CRITICO:    [(1, 40),  (150, 300)],       # Zona crítica
        ESTADO_NO_CRITICO: [(40, 150)],                  # Todo lo demás
    },
    "frecuencia_respiratoria": {
        ESTADO_FALLECIDO:  [(0, 0)],
        ESTADO_CRITICO:    [(1, 8),   (30, 60)],
        ESTADO_NO_CRITICO: [(8, 30)],
    },
    "saturacion_oxigeno": {
        ESTADO_FALLECIDO:  [(0, 0)],
        ESTADO_CRITICO:    [(1, 85)],                    # Hipoxemia severa
        ESTADO_NO_CRITICO: [(85, 100)],
    },
    "presion_sistolica": {
        ESTADO_FALLECIDO:  [(0, 0)],
        ESTADO_CRITICO:    [(1, 70),  (180, 300)],
        ESTADO_NO_CRITICO: [(70, 180)],
    },
    "presion_diastolica": {
        ESTADO_FALLECIDO:  [(0, 0)],
        ESTADO_CRITICO:    [(1, 40),  (110, 200)],
        ESTADO_NO_CRITICO: [(40, 110)],
    },
    "temperatura": {
        ESTADO_FALLECIDO:  [(0, 0)],
        ESTADO_CRITICO:    [(1, 35),  (40, 45)],
        ESTADO_NO_CRITICO: [(35, 40)],
    },
}

# ──── Órdenes de severidad por área (de mayor a menor gravedad) ────
ORDEN_SEVERIDAD_SALA = [
    ESTADO_FALLECIDO,
    ESTADO_ATENCION,
    ESTADO_PRUDENTE,
    ESTADO_ESTABLE,
    ESTADO_SIN_DATOS,
]

ORDEN_SEVERIDAD_EMERGENCIA = [
    ESTADO_FALLECIDO,
    ESTADO_CRITICO,
    ESTADO_NO_CRITICO,
]

# ============================================================================
# 6. PARÁMETROS DE SIMULACIÓN
# ============================================================================
# Controlan la generación de datos y el comportamiento de la simulación.

# Cantidad predeterminada de pacientes a generar en cada área
CANTIDAD_PACIENTES_SALA = 24       # 4 salas × 6 pacientes cada una
CANTIDAD_PACIENTES_EMERGENCIA = 10

# Salas de internación disponibles
# A-D: pobladas al inicio con 6 pacientes cada una
# E-F: vacías al inicio, reciben transferidos desde emergencias
SALAS_HOSPITAL = [
    {"nombre": "Sala A", "camas_inicio": 101, "color": "#1976D2"},
    {"nombre": "Sala B", "camas_inicio": 201, "color": "#388E3C"},
    {"nombre": "Sala C", "camas_inicio": 301, "color": "#F57C00"},
    {"nombre": "Sala D", "camas_inicio": 401, "color": "#7B1FA2"},
    {"nombre": "Sala E", "camas_inicio": 501, "color": "#0097A7"},
    {"nombre": "Sala F", "camas_inicio": 601, "color": "#689F38"},
]

# Solo las primeras 4 salas reciben pacientes al generar la simulación
SALAS_GENERACION = SALAS_HOSPITAL[:4]

PACIENTES_POR_SALA = 6

# Intervalo de actualización del monitor (en milisegundos)
# 5000 ms = 5 segundos entre ticks para una simulación más realista
INTERVALO_MONITOREO_MS = 5000

# Probabilidad de que un signo vital cambie en cada tick de simulación (0.0 a 1.0)
PROBABILIDAD_CAMBIO_SIGNO = 0.15

# Magnitud máxima de variación aleatoria de signos en cada tick
# Reducidas para cambios más suaves y realistas (no saltos bruscos)
VARIACION_MAXIMA_HR   = 2    # bpm
VARIACION_MAXIMA_RR   = 1    # rpm
VARIACION_MAXIMA_SPO  = 1    # %
VARIACION_MAXIMA_PA   = 2    # mmHg
VARIACION_MAXIMA_TEMP = 0.1  # °C

# ============================================================================
# 7. CONFIGURACIÓN DE LA INTERFAZ GRÁFICA
# ============================================================================

# Dimensiones de la ventana principal
ANCHO_VENTANA  = 1280
ALTO_VENTANA   = 800

# Tema de CustomTkinter ("dark", "light" o "system")
TEMA_APARIENCIA = "dark"
TEMA_COLOR      = "blue"

# Tamaño de las tarjetas de paciente en el panel de salas
ANCHO_TARJETA = 200
ALTO_TARJETA  = 140

# ============================================================================
# 8. RUTAS DE ASSETS MULTIMEDIA
# ============================================================================
# Se usa os.path.dirname para que las rutas funcionen sin importar desde
# dónde se ejecute el programa.

_RUTA_BASE = os.path.dirname(os.path.abspath(__file__))

RUTA_ICONOS  = os.path.join(_RUTA_BASE, "assets", "iconos")
RUTA_SONIDOS = os.path.join(_RUTA_BASE, "assets", "sonidos")

# Archivo de sonido para la alarma de emergencia
RUTA_ALERTA_WAV = os.path.join(RUTA_SONIDOS, "alerta.wav")

# Archivo de sonido para alertas del área de hospitalización
RUTA_ALERTA_SALA_WAV = os.path.join(RUTA_SONIDOS, "genhi.wav")

# Iconos de avatar disponibles (se mapean por tipo de paciente)
ICONOS_AVATAR = {
    "hombre":  os.path.join(RUTA_ICONOS, "hombre.png"),
    "mujer":   os.path.join(RUTA_ICONOS, "mujer.png"),
    "anciano": os.path.join(RUTA_ICONOS, "anciano.png"),
    "anciana": os.path.join(RUTA_ICONOS, "anciana.png"),
    "nino":    os.path.join(RUTA_ICONOS, "nino.png"),
    "nina":    os.path.join(RUTA_ICONOS, "nina.png"),
}

# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Al ejecutar este archivo directamente se imprimen todas las constantes
    definidas para verificar visualmente que los valores son correctos.
    """
    print("=" * 50)
    print("  VERIFICACIÓN DE CONFIGURACIÓN - GH")
    print("=" * 50)

    print("\n[ESTADOS CLÍNICOS — SALA]")
    for estado in ESTADOS_SALA:
        print(f"  {estado:<15} -> Prioridad: {PRIORIDAD_ESTADO[estado]}"
              f"  |  Color: {COLORES_ESTADO[estado]}")

    print("\n[ESTADOS CLÍNICOS — EMERGENCIA]")
    for estado in ESTADOS_EMERGENCIA:
        print(f"  {estado:<15} -> Prioridad: {PRIORIDAD_ESTADO[estado]}"
              f"  |  Color: {COLORES_ESTADO[estado]}")

    print(f"\n[ESTADO UNIVERSAL]")
    print(f"  {ESTADO_FALLECIDO:<15} -> Prioridad: {PRIORIDAD_ESTADO[ESTADO_FALLECIDO]}"
          f"  |  Color: {COLORES_ESTADO[ESTADO_FALLECIDO]}")

    print("\n[RANGOS NORMALES DE SIGNOS VITALES]")
    for signo, (vmin, vmax) in RANGOS_NORMALES.items():
        unidad = UNIDADES_SIGNOS[signo]
        print(f"  {NOMBRES_SIGNOS[signo]:<35} {vmin}-{vmax} {unidad}")

    print("\n[UMBRALES DE CLASIFICACIÓN — SALA]")
    for signo, umbrales in UMBRALES_SALA.items():
        print(f"\n  --- {NOMBRES_SIGNOS[signo]} ---")
        for estado in ORDEN_SEVERIDAD_SALA:
            if estado in umbrales:
                rangos_str = "  o  ".join(
                    f"{vmin}-{vmax}" for vmin, vmax in umbrales[estado]
                )
                print(f"    {estado:<12} -> {rangos_str} {UNIDADES_SIGNOS[signo]}")

    print("\n[UMBRALES DE CLASIFICACIÓN — EMERGENCIA]")
    for signo, umbrales in UMBRALES_EMERGENCIA.items():
        print(f"\n  --- {NOMBRES_SIGNOS[signo]} ---")
        for estado in ORDEN_SEVERIDAD_EMERGENCIA:
            if estado in umbrales:
                rangos_str = "  o  ".join(
                    f"{vmin}-{vmax}" for vmin, vmax in umbrales[estado]
                )
                print(f"    {estado:<12} -> {rangos_str} {UNIDADES_SIGNOS[signo]}")

    print("\n[PARÁMETROS DE SIMULACIÓN]")
    print(f"  Pacientes en sala:        {CANTIDAD_PACIENTES_SALA}")
    print(f"  Pacientes en emergencia:  {CANTIDAD_PACIENTES_EMERGENCIA}")
    print(f"  Intervalo monitoreo:      {INTERVALO_MONITOREO_MS} ms")
    print(f"  Prob. cambio signo:       {PROBABILIDAD_CAMBIO_SIGNO}")

    print("\n[INTERFAZ GRÁFICA]")
    print(f"  Ventana: {ANCHO_VENTANA}x{ALTO_VENTANA}")
    print(f"  Tema:    {TEMA_APARIENCIA} / {TEMA_COLOR}")
    print(f"  Tarjeta: {ANCHO_TARJETA}x{ALTO_TARJETA}")

    print("\n[RUTAS DE ACTIVOS]")
    print(f"  Iconos:  {RUTA_ICONOS}")
    print(f"  Sonidos: {RUTA_SONIDOS}")
    print(f"  Alerta:  {RUTA_ALERTA_WAV}")

    print("\n[OK] Configuracion cargada correctamente.\n")
