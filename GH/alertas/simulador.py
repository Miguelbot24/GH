"""
Módulo: simulador.py
Sprint 6 — Simulador de emergencias.

Define la clase SimuladorEmergencia, que permite forzar una emergencia
médica en un paciente específico o aleatorio. Cambia sus signos vitales
a valores críticos según escenarios predefinidos (paro cardíaco, fallo
respiratorio, shock séptico, etc.) y dispara la cadena de detección:
MonitorSignos evalúa el cambio → Notificador emite alertas → GUI se
actualiza con tarjeta roja parpadeante y alarma sonora.

Dependencias previas necesarias:
    - config.py              (estados, umbrales)
    - modelos/signos_vitales.py (SignosVitales)
    - alertas/monitor.py     (MonitorSignos, CambioEstado)
    - alertas/notificador.py (Notificador, Alerta)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random

from modelos.signos_vitales import SignosVitales
from alertas.monitor import MonitorSignos, CambioEstado
from alertas.notificador import Notificador, Alerta


# ============================================================================
# ESCENARIOS DE EMERGENCIA PREDEFINIDOS
# ============================================================================
# Cada escenario define valores críticos realistas para los 6 signos vitales.
# Se basan en cuadros clínicos reales para dar verosimilitud a la simulación.

ESCENARIOS_EMERGENCIA = {
    "paro_cardiaco": {
        "nombre": "Paro Cardíaco",
        "descripcion": (
            "El paciente sufre un paro cardiorrespiratorio súbito. "
            "FC cae a valores incompatibles con la vida, SpO2 desciende "
            "drásticamente y la presión arterial colapsa."
        ),
        "signos": SignosVitales(
            frecuencia_cardiaca=20.0,       # Bradicardia severa pre-paro
            frecuencia_respiratoria=4.0,    # Respiración agónica
            saturacion_oxigeno=60.0,        # Hipoxemia severa
            presion_sistolica=50.0,         # Hipotensión severa
            presion_diastolica=30.0,        # Colapso diastólico
            temperatura=36.0,               # Temperatura descendiendo
        ),
    },
    "fallo_respiratorio": {
        "nombre": "Fallo Respiratorio Agudo",
        "descripcion": (
            "El paciente presenta dificultad respiratoria severa con "
            "caída brusca de la saturación de oxígeno. La frecuencia "
            "respiratoria se eleva como mecanismo compensatorio."
        ),
        "signos": SignosVitales(
            frecuencia_cardiaca=130.0,      # Taquicardia compensatoria
            frecuencia_respiratoria=38.0,   # Taquipnea severa
            saturacion_oxigeno=78.0,        # Hipoxemia crítica
            presion_sistolica=95.0,         # Levemente hipotenso
            presion_diastolica=60.0,
            temperatura=37.8,               # Febrícula por estrés
        ),
    },
    "shock_septico": {
        "nombre": "Shock Séptico",
        "descripcion": (
            "Infección generalizada que provoca fiebre alta, taquicardia "
            "extrema y caída de la presión arterial por vasodilatación "
            "masiva. Riesgo de fallo multiorgánico."
        ),
        "signos": SignosVitales(
            frecuencia_cardiaca=150.0,      # Taquicardia extrema
            frecuencia_respiratoria=35.0,   # Taquipnea
            saturacion_oxigeno=85.0,        # Hipoxemia
            presion_sistolica=65.0,         # Hipotensión (shock)
            presion_diastolica=35.0,        # Diastólica muy baja
            temperatura=40.5,               # Fiebre alta
        ),
    },
    "crisis_hipertensiva": {
        "nombre": "Crisis Hipertensiva",
        "descripcion": (
            "Elevación peligrosa de la presión arterial que puede "
            "provocar daño cerebral (ACV), cardíaco o renal. La FC "
            "se acelera y el paciente presenta cefalea intensa."
        ),
        "signos": SignosVitales(
            frecuencia_cardiaca=120.0,      # Taquicardia
            frecuencia_respiratoria=22.0,   # Leve taquipnea
            saturacion_oxigeno=94.0,        # Levemente baja
            presion_sistolica=200.0,        # Hipertensión severa
            presion_diastolica=120.0,       # Diastólica muy elevada
            temperatura=37.1,               # Normal
        ),
    },
    "hipotermia_severa": {
        "nombre": "Hipotermia Severa",
        "descripcion": (
            "Descenso peligroso de la temperatura corporal que deprime "
            "todas las funciones vitales: bradicardia, bradipnea y "
            "riesgo de arritmias fatales."
        ),
        "signos": SignosVitales(
            frecuencia_cardiaca=35.0,       # Bradicardia severa
            frecuencia_respiratoria=7.0,    # Bradipnea
            saturacion_oxigeno=88.0,        # Hipoxemia (mala perfusión)
            presion_sistolica=70.0,         # Hipotensión
            presion_diastolica=40.0,
            temperatura=30.5,               # Hipotermia severa
        ),
    },
    "arritmia_ventricular": {
        "nombre": "Arritmia Ventricular",
        "descripcion": (
            "Taquicardia ventricular sostenida. El corazón late a un "
            "ritmo extremadamente rápido e ineficaz, comprometiendo "
            "el gasto cardíaco y la perfusión tisular."
        ),
        "signos": SignosVitales(
            frecuencia_cardiaca=180.0,      # Taquicardia ventricular
            frecuencia_respiratoria=28.0,   # Taquipnea
            saturacion_oxigeno=84.0,        # Hipoxemia
            presion_sistolica=60.0,         # Hipotensión
            presion_diastolica=35.0,        # Bajo gasto
            temperatura=36.5,               # Normal
        ),
    },
}


class SimuladorEmergencia:
    """
    Permite simular emergencias médicas en pacientes del sistema.

    Selecciona un escenario clínico predefinido, fuerza los signos
    vitales de un paciente a valores críticos y dispara la cadena
    de detección: monitor evalúa el cambio, notificador emite alertas
    y la interfaz se actualiza (tarjeta roja + sonido).

    Principio OOP — Encapsulamiento:
        Los escenarios están definidos como datos (diccionario de signos).
        La lógica de aplicación del escenario está encapsulada en esta clase.
        El resto del sistema solo llama a los métodos públicos.
    """

    def __init__(
        self,
        monitor:      MonitorSignos = None,
        notificador:  Notificador  = None,
    ):
        """
        Constructor del simulador de emergencias.

        Args:
            monitor:     Instancia de MonitorSignos para evaluar cambios.
                         Si es None, las simulaciones no disparan evaluación.
            notificador: Instancia de Notificador para emitir alertas.
                         Si es None, no se generan alertas (modo silencioso).
        """
        self._monitor      = monitor
        self._notificador  = notificador

        # Historial de simulaciones realizadas
        self._historial_simulaciones: list[dict] = []

        # Callback para notificar a la GUI (parpadeo de tarjeta)
        self._callback_gui = None

    # ==================================================================
    # LISTADO DE ESCENARIOS DISPONIBLES
    # ==================================================================
    @staticmethod
    def obtener_escenarios(self=None) -> list[dict]:
        """
        Devuelve la lista de escenarios de emergencia disponibles
        con su nombre y descripción.

        Returns:
            Lista de diccionarios con claves: 'clave', 'nombre', 'descripcion'.
        """
        return [
            {
                "clave":       clave,
                "nombre":      datos["nombre"],
                "descripcion": datos["descripcion"],
            }
            for clave, datos in ESCENARIOS_EMERGENCIA.items()
        ]

    @classmethod
    def escenarios_disponibles(self) -> list[str]:
        """
        Devuelve las claves de los escenarios disponibles.
        Útil para poblar un combobox en la interfaz.

        Returns:
            Lista de claves (ej. ['paro_cardiaco', 'fallo_respiratorio', ...]).
        """
        return list(ESCENARIOS_EMERGENCIA.keys())

    # ==================================================================
    # SIMULACIÓN DE EMERGENCIA
    # ==================================================================
    def simular_emergencia(
        self,
        paciente,
        escenario: str = "paro_cardiaco",
    ) -> dict:
        """
        Ejecuta una simulación de emergencia sobre un paciente.

        Flujo:
          1. Guarda una copia de los signos anteriores (para referencia).
          2. Reemplaza los signos vitales del paciente con los del escenario.
          3. Si hay monitor configurado, evalúa al paciente y detecta cambios.
          4. El notificador (si existe) emitirá alertas automáticamente
             porque está suscrito al monitor como observador.
          5. Si hay callback GUI configurado, lo invoca con el resultado.

        Args:
            paciente:  Instancia de Paciente sobre la que simular.
            escenario: Clave del escenario (ej. "paro_cardiaco").
                       Debe existir en ESCENARIOS_EMERGENCIA.

        Returns:
            Diccionario con el resultado de la simulación:
              - 'paciente':      El paciente modificado.
              - 'escenario':     Nombre del escenario aplicado.
              - 'estado_anterior': Estado antes de la simulación.
              - 'estado_nuevo':  Estado después de la simulación.
              - 'cambios':       Lista de CambioEstado detectados.
              - 'exito':         True si se detectó al menos un cambio.

        Raises:
            ValueError: Si el escenario no existe.
            TypeError:  Si el paciente no es una instancia válida.
        """
        # Validar escenario
        if escenario not in ESCENARIOS_EMERGENCIA:
            raise ValueError(
                f"Escenario '{escenario}' no válido. Disponibles: "
                f"{', '.join(ESCENARIOS_EMERGENCIA.keys())}"
            )

        datos_escenario = ESCENARIOS_EMERGENCIA[escenario]

        # Guardar estado anterior
        estado_anterior = paciente.estado
        signos_anteriores = paciente.signos_vitales.copiar()

        # Aplicar signos críticos del escenario (sin pasar por setter para
        # que el monitor pueda detectar el cambio)
        paciente._signos_vitales = SignosVitales(
            frecuencia_cardiaca=datos_escenario["signos"].frecuencia_cardiaca,
            frecuencia_respiratoria=datos_escenario["signos"].frecuencia_respiratoria,
            saturacion_oxigeno=datos_escenario["signos"].saturacion_oxigeno,
            presion_sistolica=datos_escenario["signos"].presion_sistolica,
            presion_diastolica=datos_escenario["signos"].presion_diastolica,
            temperatura=datos_escenario["signos"].temperatura,
        )

        # Evaluar con el monitor (detecta cambios y notifica observadores)
        cambios = []
        if self._monitor is not None:
            cambios = self._monitor.evaluar_todos()

        # La notificación visual y sonora ocurre automáticamente porque
        # el Notificador está suscrito como observador del MonitorSignos.
        # No necesitamos llamar al notificador manualmente.

        estado_nuevo = paciente.estado

        # Construir resultado
        resultado = {
            "paciente":        paciente,
            "escenario":       datos_escenario["nombre"],
            "clave_escenario": escenario,
            "estado_anterior": estado_anterior,
            "estado_nuevo":    estado_nuevo,
            "cambios":         cambios,
            "exito":           len(cambios) > 0,
        }

        # Registrar en el historial de simulaciones
        from datetime import datetime
        self._historial_simulaciones.append({
            "resultado":  resultado,
            "momento":    datetime.now(),
        })

        # Invocar callback de GUI si está configurado
        if self._callback_gui is not None:
            try:
                self._callback_gui(resultado)
            except Exception:
                pass

        return resultado

    def simular_emergencia_aleatoria(
        self,
        pacientes: list,
        escenario:  str = None,
    ) -> dict:
        """
        Selecciona un paciente aleatorio de la lista y aplica una
        simulación de emergencia sobre él.

        Útil para el botón "Simular Emergencia" cuando no se quiere
        elegir manualmente un paciente.

        Args:
            pacientes: Lista de pacientes candidatos.
            escenario: Clave del escenario. Si es None, se elige uno
                       aleatorio entre los disponibles.

        Returns:
            Diccionario con el resultado (mismo formato que simular_emergencia).

        Raises:
            ValueError: Si la lista de pacientes está vacía.
        """
        if not pacientes:
            raise ValueError("No hay pacientes disponibles para simular.")

        paciente = random.choice(pacientes)

        if escenario is None:
            escenario = random.choice(list(ESCENARIOS_EMERGENCIA.keys()))

        return self.simular_emergencia(paciente, escenario)

    # ==================================================================
    # CONFIGURACIÓN DE CALLBACKS
    # ==================================================================
    def configurar_callback_gui(self, callback) -> None:
        """
        Configura un callback que se invoca tras cada simulación.
        La GUI lo usa para activar el parpadeo de la tarjeta.

        El callback recibe el diccionario resultado de la simulación.

        Args:
            callback: Función(dict) a invocar tras cada simulación.
        """
        self._callback_gui = callback

    # ==================================================================
    # CONSULTA DE HISTORIAL
    # ==================================================================
    @property
    def historial_simulaciones(self) -> list[dict]:
        """Lista de todas las simulaciones realizadas."""
        return list(self._historial_simulaciones)

    @property
    def total_simulaciones(self) -> int:
        """Cantidad de simulaciones ejecutadas."""
        return len(self._historial_simulaciones)

    def ultima_simulacion(self) -> dict | None:
        """
        Devuelve el resultado de la última simulación, o None si no
        se ha ejecutado ninguna.
        """
        if not self._historial_simulaciones:
            return None
        return self._historial_simulaciones[-1]["resultado"]

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================
    def __str__(self) -> str:
        return (
            f"SimuladorEmergencia: {self.total_simulaciones} simulaciones\n"
            f"  Escenarios disponibles: {len(ESCENARIOS_EMERGENCIA)}\n"
            f"  Monitor conectado: {'Si' if self._monitor else 'No'}\n"
            f"  Notificador conectado: {'Si' if self._notificador else 'No'}"
        )

    def __repr__(self) -> str:
        return (
            f"SimuladorEmergencia(simulaciones={self.total_simulaciones}, "
            f"monitor={self._monitor is not None}, "
            f"notificador={self._notificador is not None})"
        )


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo SimuladorEmergencia.
    Demuestra:
      1. Listado de escenarios disponibles.
      2. Simulación sobre un paciente específico.
      3. Simulación aleatoria sobre un grupo de pacientes.
      4. Detección de cambios de estado por el monitor.
      5. Integración monitor + notificador + simulador.
      6. Historial de simulaciones.
      7. Validación de escenarios inexistentes.
    """
    from datos.generador import GeneradorDatos
    from alertas.monitor import MonitorSignos
    from alertas.notificador import Notificador

    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: SimuladorEmergencia")
    print("=" * 60)

    # --- Preparar dependencias ---
    generador   = GeneradorDatos(semilla=77)
    monitor     = MonitorSignos()
    notificador = Notificador(sonido_activado=False)
    monitor.registrar_observador(notificador.recibir_cambio)
    simulador   = SimuladorEmergencia(monitor=monitor, notificador=notificador)

    # --- Prueba 1: Listar escenarios ---
    print("\n[1] Escenarios de emergencia disponibles:")
    for esc in SimuladorEmergencia.escenarios_disponibles():
        datos = ESCENARIOS_EMERGENCIA[esc]
        print(f"    {esc:<30} — {datos['nombre']}")

    # --- Prueba 2: Generar pacientes y cargar monitor ---
    print("\n[2] Generar 4 pacientes estables para el monitor:")
    pacientes = []
    for _ in range(4):
        p = generador.generar_paciente_sala()
        # Forzar signos normales para empezar desde ESTABLE
        p._signos_vitales = SignosVitales(72, 16, 98, 118, 74, 36.5)
        pacientes.append(p)
        monitor.agregar_paciente(p)
    monitor.evaluar_todos()  # Sincronizar estados
    print(f"    Pacientes generados y en monitor: {monitor.total_monitoreados}")
    for p in pacientes:
        print(f"    {p.id_paciente}: {p.nombre:<25} {p.estado}")

    # --- Prueba 3: Simular emergencia en paciente específico ---
    print("\n[3] Simular PARO CARDIACO en primer paciente:")
    paciente_objetivo = pacientes[0]
    print(f"    Paciente: {paciente_objetivo.nombre}")
    print(f"    Estado antes: {paciente_objetivo.estado}")

    resultado = simulador.simular_emergencia(paciente_objetivo, "paro_cardiaco")
    print(f"    Escenario aplicado: {resultado['escenario']}")
    print(f"    Estado después:     {resultado['estado_nuevo']}")
    print(f"    ¿Detectó cambio?:   {'Si' if resultado['exito'] else 'No'}")
    print(f"    Cambios detectados: {len(resultado['cambios'])}")
    print(f"    Alertas acumuladas: {notificador.total_notificaciones}")

    # --- Prueba 4: Ver cambios en los signos ---
    print("\n[4] Signos vitales tras la simulación:")
    sv = paciente_objetivo.signos_vitales
    print(f"    HR={sv.frecuencia_cardiaca:.0f}, RR={sv.frecuencia_respiratoria:.0f}, "
          f"SpO2={sv.saturacion_oxigeno:.0f}%")
    print(f"    PA={sv.obtener_presion_arterial()}, Temp={sv.temperatura}")

    # --- Prueba 5: Simular emergencia aleatoria ---
    print("\n[5] Simular emergencia ALEATORIA:")
    resultado_aleat = simulador.simular_emergencia_aleatoria(pacientes)
    print(f"    Paciente afectado: {resultado_aleat['paciente'].nombre}")
    print(f"    Escenario:         {resultado_aleat['escenario']}")
    print(f"    Estado anterior:   {resultado_aleat['estado_anterior']}")
    print(f"    Estado nuevo:      {resultado_aleat['estado_nuevo']}")
    print(f"    Alertas totales:   {notificador.total_notificaciones}")

    # --- Prueba 6: Historial de simulaciones ---
    print(f"\n[6] Historial ({simulador.total_simulaciones} simulaciones):")
    for i, registro in enumerate(simulador.historial_simulaciones, 1):
        res = registro["resultado"]
        print(f"    #{i}: {res['paciente'].nombre} -> {res['escenario']} "
              f"({res['estado_anterior']} -> {res['estado_nuevo']})")

    # --- Prueba 7: Última simulación ---
    print(f"\n[7] Última simulación:")
    ultima = simulador.ultima_simulacion()
    if ultima:
        print(f"    Paciente: {ultima['paciente'].nombre}")
        print(f"    Escenario: {ultima['escenario']}")

    # --- Prueba 8: Callback GUI ---
    print("\n[8] Configurar callback GUI:")
    eventos_gui = []

    def mi_callback(resultado):
        eventos_gui.append(resultado)
        print(f"    [GUI] Activaría parpadeo rojo para: "
              f"{resultado['paciente'].nombre}")

    simulador.configurar_callback_gui(mi_callback)

    # Resetear paciente a normal y volver a simular
    paciente_objetivo._signos_vitales = SignosVitales(72, 16, 98, 118, 74, 36.5)
    monitor.evaluar_todos()
    simulador.simular_emergencia(paciente_objetivo, "shock_septico")
    print(f"    Callbacks GUI invocados: {len(eventos_gui)}")

    # --- Prueba 9: Error con escenario inexistente ---
    print("\n[9] Intentar simular escenario inexistente:")
    try:
        simulador.simular_emergencia(pacientes[0], "escenario_inventado")
        print("    ERROR: No se lanzó la excepción.")
    except ValueError as e:
        print(f"    ValueError: {e}")

    # --- Prueba 10: Simular sin pacientes (lista vacía) ---
    print("\n[10] Simular emergencia aleatoria con lista vacía:")
    try:
        simulador.simular_emergencia_aleatoria([])
        print("    ERROR: No se lanzó la excepción.")
    except ValueError as e:
        print(f"    ValueError: {e}")

    # --- Prueba 11: Resumen del simulador ---
    print(f"\n[11] Estado del simulador:\n{simulador}")

    # --- Prueba 12: Escenarios con callback GUI ---
    print("\n[12] Simular todos los escenarios en pacientes estables:")

    # Resetear todos los pacientes a normal
    from modelos.signos_vitales import SignosVitales as SV
    for p in pacientes:
        p._signos_vitales = SV(72, 16, 98, 118, 74, 36.5)
    monitor.evaluar_todos()

    eventos_gui2 = []
    simulador.configurar_callback_gui(
        lambda r: eventos_gui2.append(f"{r['paciente'].nombre}: {r['escenario']}")
    )

    for i, clave_esc in enumerate(SimuladorEmergencia.escenarios_disponibles()):
        if i >= len(pacientes):
            break
        resultado = simulador.simular_emergencia(pacientes[i], clave_esc)
        print(f"    {resultado['escenario']:<30} -> {resultado['estado_nuevo']}")

    print(f"\n    Total simulaciones acumuladas: {simulador.total_simulaciones}")

    print("\n[OK] Pruebas de SimuladorEmergencia completadas.\n")
