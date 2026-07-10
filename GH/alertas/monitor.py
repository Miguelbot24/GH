"""
Módulo: monitor.py
Sprint 3 — Monitor de signos vitales.

Define la clase MonitorSignos, que evalúa periódicamente los signos vitales
de los pacientes, determina su estado clínico según los umbrales definidos
en config.py, y notifica a los observadores suscritos cuando ocurre un
cambio de estado relevante.

Implementa el patrón Observer: el monitor emite eventos de cambio de estado
y los suscriptores (notificador, sistema de colas, interfaz) reaccionan
sin que el monitor necesite conocerlos.

Dependencias previas necesarias:
    - config.py              (umbrales, estados, orden severidad)
    - modelos/paciente.py    (Paciente ABC)
    - modelos/signos_vitales.py (SignosVitales)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime

from config import (
    ESTADO_CRITICO,
    ESTADO_PRUDENTE,
    ESTADO_ATENCION,
    ESTADO_ESTABLE,
    ESTADO_FALLECIDO,
    ESTADO_SIN_DATOS,
    ORDEN_SEVERIDAD_SALA,
    PRIORIDAD_ESTADO,
    VARIACION_MAXIMA_HR,
    VARIACION_MAXIMA_RR,
    VARIACION_MAXIMA_SPO,
    VARIACION_MAXIMA_PA,
    VARIACION_MAXIMA_TEMP,
    LIMITES_VARIACION_SALA,
    RANGOS_NORMALES,
)

from modelos.paciente import Paciente
from modelos.paciente_sala import PacienteSala
from modelos.signos_vitales import SignosVitales


class CambioEstado:
    """
    Registro inmutable de un cambio de estado detectado por el monitor.

    Almacena el paciente, el estado anterior, el nuevo estado, la
    diferencia de prioridad y el momento exacto del cambio.
    """

    def __init__(
        self,
        paciente:        Paciente,
        estado_anterior: str,
        estado_nuevo:    str,
        momento:         datetime = None,
    ):
        self.paciente        = paciente
        self.estado_anterior = estado_anterior
        self.estado_nuevo    = estado_nuevo
        self.momento         = momento if momento is not None else datetime.now()

    @property
    def es_agravamiento(self) -> bool:
        """
        Indica si el cambio fue a peor (mayor severidad).
        # Usa la referencia de importación ya renombrada
        """
        idx_anterior = ORDEN_SEVERIDAD_SALA.index(self.estado_anterior)
        idx_nuevo    = ORDEN_SEVERIDAD_SALA.index(self.estado_nuevo)
        return idx_nuevo < idx_anterior

    @property
    def es_mejoria(self) -> bool:
        """Indica si el cambio fue a mejor (menor severidad)."""
        idx_anterior = ORDEN_SEVERIDAD_SALA.index(self.estado_anterior)
        idx_nuevo    = ORDEN_SEVERIDAD_SALA.index(self.estado_nuevo)
        return idx_nuevo > idx_anterior

    @property
    def diferencial_prioridad(self) -> int:
        """
        Cuánto cambió la prioridad numérica.
        Positivo = empeoró, negativo = mejoró.
        """
        prio_anterior = PRIORIDAD_ESTADO.get(self.estado_anterior, 0)
        prio_nueva    = PRIORIDAD_ESTADO.get(self.estado_nuevo, 0)
        return prio_nueva - prio_anterior

    def __str__(self) -> str:
        direccion = "EMPEORO" if self.es_agravamiento else "MEJORO"
        return (
            f"[{self.momento.strftime('%H:%M:%S')}] {direccion}: "
            f"{self.paciente.nombre} ({self.paciente.id_paciente}) "
            f"{self.estado_anterior} -> {self.estado_nuevo}"
        )

    def __repr__(self) -> str:
        return (
            f"CambioEstado(paciente={self.paciente.id_paciente!r}, "
            f"{self.estado_anterior}->{self.estado_nuevo})"
        )


class MonitorSignos:
    """
    Evalúa los signos vitales de los pacientes bajo monitoreo y detecta
    cambios de estado clínico.

    Patrón Observer:
        Los interesados (notificador, cola de atención, interfaz gráfica)
        se suscriben mediante registrar_observador(callback). Cuando el
        monitor detecta un cambio de estado, invoca todos los callbacks
        pasándoles un objeto CambioEstado.

    Modos de operación:
        - Modo pasivo: solo evalúa el estado actual (evaluar_todos).
        - Modo activo: además, aplica pequeñas variaciones aleatorias a
          los signos vitales para simular cambios fisiológicos en el tiempo
          (simular_tick).
    """

    def __init__(self):
        """Constructor del monitor."""
        # Pacientes bajo monitoreo: diccionario {id_paciente: Paciente}
        self._pacientes: dict[str, Paciente] = {}

        # Observadores suscritos: lista de funciones callback
        # Cada callback recibe un objeto CambioEstado
        self._observadores: list = []

        # Historial de todos los cambios detectados
        self._historial_cambios: list[CambioEstado] = []

        # Control de modo simulación
        self._simulacion_activa: bool = False

    # ==================================================================
    # GESTIÓN DE PACIENTES MONITOREADOS
    # ==================================================================

    def agregar_paciente(self, paciente: Paciente) -> None:
        """
        Añade un paciente al monitoreo continuo.

        Si el paciente ya estaba siendo monitoreado, no hace nada.

        Args:
            paciente: Instancia de Paciente a monitorear.

        Raises:
            TypeError: Si el argumento no es una instancia de Paciente.
        """
        if not isinstance(paciente, Paciente):
            raise TypeError("Solo se pueden monitorear instancias de Paciente.")
        self._pacientes[paciente.id_paciente] = paciente

    def agregar_pacientes(self, pacientes: list) -> None:
        """
        Añade múltiples pacientes al monitoreo.

        Args:
            pacientes: Lista de instancias de Paciente.
        """
        for paciente in pacientes:
            self.agregar_paciente(paciente)

    def remover_paciente(self, id_paciente: str) -> Paciente:
        """
        Retira un paciente del monitoreo.

        Args:
            id_paciente: ID del paciente a remover.

        Returns:
            La instancia del paciente removido.

        Raises:
            KeyError: Si el ID no está siendo monitoreado.
        """
        if id_paciente not in self._pacientes:
            raise KeyError(
                f"El paciente '{id_paciente}' no está siendo monitoreado."
            )
        return self._pacientes.pop(id_paciente)

    @property
    def pacientes_monitoreados(self) -> list[Paciente]:
        """Lista de pacientes actualmente bajo monitoreo."""
        return list(self._pacientes.values())

    @property
    def total_monitoreados(self) -> int:
        """Cantidad de pacientes bajo monitoreo."""
        return len(self._pacientes)

    # ==================================================================
    # SISTEMA DE OBSERVADORES
    # ==================================================================

    def registrar_observador(self, callback) -> None:
        """
        Suscribe una función callback que será llamada cuando ocurra
        un cambio de estado.

        El callback debe aceptar un argumento: una instancia de CambioEstado.

        Args:
            callback: Función que recibe un CambioEstado.
        """
        if callback not in self._observadores:
            self._observadores.append(callback)

    def remover_observador(self, callback) -> None:
        """
        Elimina un observador previamente registrado.

        Args:
            callback: La función callback a remover.
        """
        if callback in self._observadores:
            self._observadores.remove(callback)

    def _notificar_observadores(self, cambio: CambioEstado) -> None:
        """
        Invoca todos los callbacks registrados con el cambio detectado.
        Si un callback lanza una excepción, se captura y continúa con
        el siguiente para no interrumpir la cadena de notificación.
        """
        for callback in self._observadores:
            try:
                callback(cambio)
            except Exception:
                # En producción se loguearía; aquí seguimos para no
                # romper el pipeline de notificaciones.
                pass

    # ==================================================================
    # EVALUACIÓN DE ESTADO
    # ==================================================================

    def evaluar_paciente(self, paciente: Paciente) -> CambioEstado | None:
        """
        Evalúa el estado clínico actual de un paciente y detecta si
        hubo un cambio respecto a su estado anterior registrado.

        Args:
            paciente: Paciente a evaluar.

        Returns:
            CambioEstado si el estado cambió, None si permanece igual.
        """
        estado_anterior = paciente.estado
        estado_nuevo    = paciente.actualizar_estado()

        if estado_anterior != estado_nuevo:
            cambio = CambioEstado(
                paciente=paciente,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
            )
            # Registrar en el historial
            self._historial_cambios.append(cambio)
            # Notificar a todos los observadores suscritos
            self._notificar_observadores(cambio)
            return cambio

        return None

    def evaluar_todos(self) -> list[CambioEstado]:
        """
        Evalúa el estado de todos los pacientes monitoreados.

        Returns:
            Lista de CambioEstado para los pacientes cuyo estado cambió.
        """
        cambios = []
        for paciente in self._pacientes.values():
            cambio = self.evaluar_paciente(paciente)
            if cambio is not None:
                cambios.append(cambio)
        return cambios

    # ==================================================================
    # SIMULACIÓN DE VARIACIONES DE SIGNOS VITALES
    # ==================================================================

    def variar_signos_aleatoriamente(self, paciente: Paciente) -> None:
        """
        Aplica pequeñas variaciones aleatorias a los signos vitales de
        un paciente, simulando cambios fisiológicos en tiempo real.

        Para pacientes de sala, aplica reversión a la media y clamp duro
        para que los signos nunca crucen a ATENCIÓN sin intervención del
        simulador de emergencia. Pacientes en ATENCIÓN o FALLECIDO no
        varían sus signos (solo regresan con el botón Atender en Sala).

        Args:
            paciente: Paciente cuyos signos se van a variar.
        """
        es_sala = isinstance(paciente, PacienteSala)

        if es_sala and paciente.estado in (ESTADO_ATENCION, ESTADO_FALLECIDO):
            return  # Congelado: solo el botón Atender en Sala lo saca

        signos = paciente.signos_vitales

        if es_sala:
            self._variar_signo(signos, "frecuencia_cardiaca",
                               VARIACION_MAXIMA_HR, es_sala=True)
            self._variar_signo(signos, "frecuencia_respiratoria",
                               VARIACION_MAXIMA_RR, es_sala=True)
            self._variar_signo(signos, "saturacion_oxigeno",
                               VARIACION_MAXIMA_SPO, es_sala=True)
            self._variar_signo(signos, "presion_sistolica",
                               VARIACION_MAXIMA_PA, es_sala=True)
            self._variar_signo(signos, "presion_diastolica",
                               VARIACION_MAXIMA_PA, es_sala=True)
            self._variar_signo(signos, "temperatura",
                               VARIACION_MAXIMA_TEMP, es_sala=True)
        else:
            self._variar_signo(signos, "frecuencia_cardiaca", VARIACION_MAXIMA_HR)
            self._variar_signo(signos, "frecuencia_respiratoria", VARIACION_MAXIMA_RR)
            self._variar_signo(signos, "saturacion_oxigeno", VARIACION_MAXIMA_SPO)
            self._variar_signo(signos, "presion_sistolica", VARIACION_MAXIMA_PA)
            self._variar_signo(signos, "presion_diastolica", VARIACION_MAXIMA_PA)
            self._variar_signo(signos, "temperatura", VARIACION_MAXIMA_TEMP)

    def _variar_signo(
        self, signos: SignosVitales, nombre: str, variacion_max: float,
        es_sala: bool = False,
    ) -> None:
        """
        Aplica una variación aleatoria a un signo vital específico,
        respetando los límites fisiológicos definidos en SignosVitales.

        Para sala: aplica sesgo de reversión a la media (80% hacia ESTABLE
        si está en PRUDENTE) y clamp duro para impedir cruzar a ATENCIÓN.

        Args:
            signos:        Instancia de SignosVitales a modificar.
            nombre:        Nombre del signo (ej. "frecuencia_cardiaca").
            variacion_max: Máxima variación permitida (+/-).
            es_sala:       True si el paciente es de sala.
        """
        setters = {
            "frecuencia_cardiaca":     lambda v: setattr(signos, "frecuencia_cardiaca", v),
            "frecuencia_respiratoria": lambda v: setattr(signos, "frecuencia_respiratoria", v),
            "saturacion_oxigeno":      lambda v: setattr(signos, "saturacion_oxigeno", v),
            "presion_sistolica":       lambda v: setattr(signos, "presion_sistolica", v),
            "presion_diastolica":      lambda v: setattr(signos, "presion_diastolica", v),
            "temperatura":             lambda v: setattr(signos, "temperatura", v),
        }

        limites = {
            "frecuencia_cardiaca":     (0.0, 350.0),
            "frecuencia_respiratoria": (0.0, 80.0),
            "saturacion_oxigeno":      (0.0, 100.0),
            "presion_sistolica":       (0.0, 300.0),
            "presion_diastolica":      (0.0, 200.0),
            "temperatura":             (20.0, 45.0),
        }

        if nombre not in setters:
            return

        valor_actual = signos._obtener_valor(nombre)

        if es_sala:
            vmin_estable, vmax_estable = RANGOS_NORMALES[nombre]
            en_estable = vmin_estable <= valor_actual <= vmax_estable

            if en_estable:
                # Dentro de ESTABLE: random walk normal
                delta = random.uniform(-variacion_max, variacion_max)
                nuevo_valor = valor_actual + delta
            elif valor_actual > vmax_estable:
                # Por encima de ESTABLE (PRUDENTE): 80% hacia abajo
                if random.random() < 0.8:
                    delta = random.uniform(-variacion_max, 0)
                else:
                    delta = random.uniform(-variacion_max, variacion_max)
                nuevo_valor = valor_actual + delta
            else:
                # Por debajo de ESTABLE (PRUDENTE): 80% hacia arriba
                if random.random() < 0.8:
                    delta = random.uniform(0, variacion_max)
                else:
                    delta = random.uniform(-variacion_max, variacion_max)
                nuevo_valor = valor_actual + delta

            # Clamp duro: no puede cruzar a ATENCIÓN
            vmin_clamp, vmax_clamp = LIMITES_VARIACION_SALA[nombre]
            nuevo_valor = max(vmin_clamp, min(vmax_clamp, nuevo_valor))
        else:
            # Emergencias: random walk sin restricciones
            delta = random.uniform(-variacion_max, variacion_max)
            nuevo_valor = valor_actual + delta

        # Evitar valores negativos (salvo 0 que es válido para FALLECIDO)
        if valor_actual > 0 and nuevo_valor < 0:
            nuevo_valor = 0.1

        # Acotar al rango fisiológico
        vmin, vmax = limites[nombre]
        nuevo_valor = max(vmin, min(vmax, nuevo_valor))

        setters[nombre](
            round(nuevo_valor) if nombre != "temperatura"
            else round(nuevo_valor, 1)
        )

    def simular_tick(self) -> list[CambioEstado]:
        """
        Ejecuta un ciclo completo de simulación:
          1. Aplica variaciones aleatorias a los signos de cada paciente.
          2. Reevalúa el estado de todos los pacientes.
          3. Notifica los cambios detectados.

        Returns:
            Lista de CambioEstado detectados en este tick.
        """
        # Paso 1: variar signos de todos los pacientes
        for paciente in self._pacientes.values():
            self.variar_signos_aleatoriamente(paciente)

        # Paso 2 y 3: evaluar y notificar cambios
        return self.evaluar_todos()

    # ==================================================================
    # CONSULTA DE HISTORIAL
    # ==================================================================

    @property
    def historial_cambios(self) -> list[CambioEstado]:
        """Historial completo de cambios de estado detectados."""
        return list(self._historial_cambios)

    def cambios_recientes(self, cantidad: int = 10) -> list[CambioEstado]:
        """
        Devuelve los N cambios más recientes.

        Args:
            cantidad: Número de cambios a devolver (por defecto 10).

        Returns:
            Lista de los últimos CambioEstado.
        """
        return self._historial_cambios[-cantidad:]

    def cambios_por_paciente(self, id_paciente: str) -> list[CambioEstado]:
        """
        Filtra el historial de cambios para un paciente específico.

        Args:
            id_paciente: ID del paciente.

        Returns:
            Lista de CambioEstado de ese paciente.
        """
        return [
            c for c in self._historial_cambios
            if c.paciente.id_paciente == id_paciente
        ]

    def total_cambios(self) -> int:
        """Cantidad total de cambios de estado registrados."""
        return len(self._historial_cambios)

    # ==================================================================
    # ESTADÍSTICAS DEL MONITOREO
    # ==================================================================

    def resumen_estados(self) -> dict:
        """
        Calcula cuántos pacientes monitoreados hay en cada estado.

        Returns:
            Diccionario {estado: cantidad}.
        """
        # Inicializar dinámicamente con todos los estados posibles
        from config import ESTADOS_SALA, ESTADOS_EMERGENCIA
        conteo = {}
        for estado in ESTADOS_SALA + ESTADOS_EMERGENCIA + (ESTADO_FALLECIDO,):
            conteo[estado] = 0
        for paciente in self._pacientes.values():
            conteo[paciente.estado] += 1
        return conteo

    def pacientes_en_estado(self, estado: str) -> list[Paciente]:
        """
        Devuelve los pacientes monitoreados que están en un estado dado.

        Args:
            estado: Estado clínico a filtrar.

        Returns:
            Lista de pacientes en ese estado.
        """
        return [
            p for p in self._pacientes.values()
            if p.estado == estado
        ]

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================

    def __str__(self) -> str:
        """Representación resumida del estado del monitor."""
        conteo = self.resumen_estados()
        lineas = [
            f"Monitor de signos: {self.total_monitoreados} pacientes",
            f"  Cambios registrados: {self.total_cambios()}",
            "  Distribución de estados:",
        ]
        for estado, cantidad in conteo.items():
            if cantidad > 0:
                lineas.append(f"    {estado:<12} {cantidad}")
        return "\n".join(lineas)

    def __repr__(self) -> str:
        """Representación técnica."""
        return (
            f"MonitorSignos(pacientes={self.total_monitoreados}, "
            f"observadores={len(self._observadores)}, "
            f"cambios={self.total_cambios()})"
        )


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo MonitorSignos.
    Demuestra:
      1. Creación del monitor y registro de pacientes.
      2. Evaluación pasiva: detectar cambios de estado al modificar signos.
      3. Patrón Observer: callbacks que reaccionan a cambios.
      4. Simulación activa: simular_tick() con variaciones aleatorias.
      5. Historial de cambios y filtrado por paciente.
      6. Estadísticas de pacientes monitoreados.
      7. Agravamiento vs mejoría en CambioEstado.
    """
    from datos.generador import GeneradorDatos

    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: MonitorSignos")
    print("=" * 60)

    generador = GeneradorDatos(semilla=100)
    monitor = MonitorSignos()

    # --- Prueba 1: Registrar observador (patrón Observer) ---
    print("\n[1] Registrar observador de cambios:")
    alertas_recibidas = []  # Lista para acumular las notificaciones

    def mi_observador(cambio: CambioEstado):
        """Callback de prueba que acumula los cambios detectados."""
        alertas_recibidas.append(cambio)
        print(f"    [OBSERVADOR] {cambio}")

    monitor.registrar_observador(mi_observador)
    print(f"    Observadores registrados: {len(monitor._observadores)}")

    # --- Prueba 2: Agregar pacientes al monitoreo ---
    print("\n[2] Agregar 3 pacientes al monitor:")
    for _ in range(3):
        monitor.agregar_paciente(generador.generar_paciente_sala())
    print(f"    Pacientes monitoreados: {monitor.total_monitoreados}")
    for p in monitor.pacientes_monitoreados:
        print(f"    {p.id_paciente}: {p.nombre} — {p.estado}")

    # --- Prueba 3: Evaluación inicial sin cambios ---
    print("\n[3] Evaluar todos los pacientes (primera vez):")
    cambios = monitor.evaluar_todos()
    print(f"    Cambios detectados: {len(cambios)}")
    print(f"    (sin cambios porque es la primera evaluación)")

    # --- Prueba 4: Modificar signos y detectar cambio ---
    print("\n[4] Modificar signos vitales (sin pasar por setter) y evaluar:")
    lista_pacientes = monitor.pacientes_monitoreados
    paciente_prueba = lista_pacientes[0]
    print(f"    Paciente: {paciente_prueba.nombre} — Estado actual: {paciente_prueba.estado}")

    # Primero forzamos signos ESTABLE directamente (sin disparar actualizar_estado)
    paciente_prueba._signos_vitales = SignosVitales(
        frecuencia_cardiaca=72.0,
        frecuencia_respiratoria=16.0,
        saturacion_oxigeno=98.0,
        presion_sistolica=115.0,
        presion_diastolica=74.0,
        temperatura=36.6,
    )
    # Ahora el monitor evalúa: detecta el cambio del estado anterior al nuevo
    cambios_antes = monitor.evaluar_paciente(paciente_prueba)
    if cambios_antes:
        print(f"    Cambio detectado: {cambios_antes}")

    # Ahora cambiamos a signos CRITICOS directamente
    paciente_prueba._signos_vitales = SignosVitales(
        frecuencia_cardiaca=145.0,
        frecuencia_respiratoria=32.0,
        saturacion_oxigeno=80.0,
        presion_sistolica=68.0,
        presion_diastolica=38.0,
        temperatura=39.8,
    )
    cambios = monitor.evaluar_todos()
    print(f"    Cambios tras forzar CRITICO: {len(cambios)}")
    for c in cambios:
        print(f"    -> {c}")

    # --- Prueba 5: Simular tick con variaciones ---
    print("\n[5] Simular 5 ticks de monitoreo activo:")
    # Colocamos al paciente en un estado límite (BASICO) para que
    # pequeñas variaciones puedan provocar cambios de estado
    paciente_prueba._signos_vitales = SignosVitales(
        frecuencia_cardiaca=55.0,     # BASICO (bradicardia leve)
        frecuencia_respiratoria=22.0, # BASICO (taquipnea leve)
        saturacion_oxigeno=94.0,      # BASICO (hipoxemia leve)
        presion_sistolica=85.0,       # BASICO (hipotensión leve)
        presion_diastolica=55.0,      # BASICO
        temperatura=37.5,             # BASICO (febrícula)
    )
    monitor.evaluar_paciente(paciente_prueba)  # Sincronizar estado
    print(f"    Estado inicial para ticks: {paciente_prueba.estado}")

    for tick in range(1, 6):
        random.seed(tick * 100)
        cambios_tick = monitor.simular_tick()
        if cambios_tick:
            for c in cambios_tick:
                print(f"    Tick {tick}: {c}")
        else:
            # Mostrar los signos actuales aunque no haya cambio
            sv = paciente_prueba.signos_vitales
            print(f"    Tick {tick}: sin cambios (HR={sv.frecuencia_cardiaca:.0f}, "
                  f"SpO2={sv.saturacion_oxigeno:.0f}%, estado={paciente_prueba.estado})")

    # --- Prueba 6: Historial de cambios ---
    print(f"\n[6] Historial completo ({monitor.total_cambios()} cambios):")
    for c in monitor.historial_cambios:
        print(f"    {c}")

    # --- Prueba 7: Cambios por paciente ---
    print(f"\n[7] Cambios del paciente {paciente_prueba.id_paciente}:")
    cambios_pac = monitor.cambios_por_paciente(paciente_prueba.id_paciente)
    print(f"    Total: {len(cambios_pac)} cambio(s)")
    for c in cambios_pac:
        print(f"    {c}")

    # --- Prueba 8: Últimos cambios ---
    print("\n[8] Últimos 3 cambios registrados:")
    for c in monitor.cambios_recientes(3):
        print(f"    {c}")

    # --- Prueba 9: Resumen de estados ---
    print(f"\n[9] Resumen del monitor:\n{monitor}")

    # --- Prueba 10: Pacientes en estado crítico ---
    criticos = monitor.pacientes_en_estado(ESTADO_CRITICO)
    print(f"\n[10] Pacientes en estado CRITICO: {len(criticos)}")
    for p in criticos:
        print(f"    {p.id_paciente}: {p.nombre}")

    # --- Prueba 11: Propiedades de CambioEstado ---
    print("\n[11] Propiedades de un CambioEstado (agravamiento/mejoría):")
    if monitor.historial_cambios:
        ultimo = monitor.historial_cambios[-1]
        print(f"    Cambio: {ultimo.estado_anterior} -> {ultimo.estado_nuevo}")
        print(f"    ¿Agravamiento?:  {ultimo.es_agravamiento}")
        print(f"    ¿Mejoría?:       {ultimo.es_mejoria}")
        print(f"    Diferencial prio: {ultimo.diferencial_prioridad}")

    # --- Prueba 12: Remover paciente ---
    print("\n[12] Remover paciente del monitoreo:")
    removido = monitor.remover_paciente(paciente_prueba.id_paciente)
    print(f"    Removido: {removido.nombre}")
    print(f"    Pacientes restantes: {monitor.total_monitoreados}")

    # --- Prueba 13: Error al remover paciente no monitoreado ---
    print("\n[13] Intentar remover paciente inexistente:")
    try:
        monitor.remover_paciente("PAC-9999")
        print("    ERROR: No se lanzó la excepción.")
    except KeyError as e:
        print(f"    KeyError: {e}")

    # --- Prueba 14: Notificaciones acumuladas ---
    print(f"\n[14] Total de notificaciones enviadas al observador: {len(alertas_recibidas)}")
    print(f"    (coincide con total de cambios: {monitor.total_cambios()})")

    print("\n[OK] Pruebas de MonitorSignos completadas.\n")
