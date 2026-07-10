"""
Módulo: notificador.py
Sprint 3 — Notificador de alertas y emergencias.

Define la clase Notificador, que actúa como suscriptor del MonitorSignos
(patrón Observer) y gestiona la emisión de alertas visuales y sonoras
cuando se detectan cambios de estado relevantes.

En el Sprint 3 funciona en modo consola. En sprints posteriores se
conectará a la interfaz gráfica para mostrar tarjetas parpadeantes,
notificaciones emergentes y reproducir la alarma sonora.

Dependencias previas necesarias:
    - config.py           (RUTA_ALERTA_WAV, estados, colores)
    - alertas/monitor.py  (MonitorSignos, CambioEstado)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import time
import winsound
from datetime import datetime

from config import (
    ESTADO_CRITICO,
    ESTADO_ATENCION,
    ESTADO_PRUDENTE,
    ESTADO_FALLECIDO,
    COLOR_CRITICO,
    COLOR_PRUDENTE,
    RUTA_ALERTA_WAV,
    RUTA_ALERTA_SALA_WAV,
)

from alertas.monitor import CambioEstado
from modelos.paciente_sala import PacienteSala


class Alerta:
    """
    Representa una alerta individual generada por el sistema.

    Atributos:
        - tipo:      Tipo de alerta ("CRITICA", "MODERADA", "INFORMATIVA").
        - mensaje:   Texto descriptivo de la alerta.
        - paciente:  Paciente asociado a la alerta.
        - momento:   Fecha y hora en que se generó.
        - atendida:  Si la alerta ya fue revisada por el personal.
    """

    TIPOS_VALIDOS = ("CRITICA", "MODERADA", "INFORMATIVA")

    def __init__(
        self,
        tipo:     str,
        mensaje:  str,
        paciente = None,
        momento:  datetime = None,
    ):
        """
        Constructor de Alerta.

        Args:
            tipo:     "CRITICA", "MODERADA" o "INFORMATIVA".
            mensaje:  Descripción de la alerta.
            paciente: Instancia de Paciente asociada (opcional).
            momento:  Timestamp del evento.
        """
        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError(
                f"Tipo de alerta '{tipo}' no válido. Usar: {self.TIPOS_VALIDOS}"
            )

        self._tipo      = tipo
        self._mensaje   = mensaje
        self._paciente  = paciente
        self._momento   = momento if momento is not None else datetime.now()
        self._atendida  = False

    # ==================================================================
    # PROPIEDADES
    # ==================================================================

    @property
    def tipo(self) -> str:
        """Tipo de alerta (CRITICA, MODERADA, INFORMATIVA)."""
        return self._tipo

    @property
    def mensaje(self) -> str:
        """Mensaje descriptivo de la alerta."""
        return self._mensaje

    @property
    def paciente(self):
        """Paciente asociado a la alerta (puede ser None)."""
        return self._paciente

    @property
    def momento(self) -> datetime:
        """Fecha y hora de la alerta."""
        return self._momento

    @property
    def atendida(self) -> bool:
        """Indica si la alerta ya fue revisada."""
        return self._atendida

    def marcar_atendida(self) -> None:
        """Marca la alerta como revisada por el personal."""
        self._atendida = True

    @property
    def es_critica(self) -> bool:
        """True si la alerta es de tipo CRITICA."""
        return self._tipo == "CRITICA"

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================

    def __str__(self) -> str:
        estado = "ATENDIDA" if self._atendida else "PENDIENTE"
        paciente_str = f" - {self._paciente.nombre}" if self._paciente else ""
        return (
            f"[{self._momento.strftime('%H:%M:%S')}] "
            f"{self._tipo}{paciente_str}: {self._mensaje} [{estado}]"
        )

    def __repr__(self) -> str:
        return (
            f"Alerta(tipo={self._tipo!r}, "
            f"mensaje={self._mensaje!r}, "
            f"atendida={self._atendida})"
        )


class Notificador:
    """
    Gestiona las alertas del sistema hospitalario.

    Se suscribe al MonitorSignos como observador y reacciona a los
    cambios de estado generando alertas visuales (consola) y sonoras
    (archivo .wav) según la gravedad del evento.

    Clasificación de cambios en alertas:
        - Cambio a CRITICO  → Alerta CRITICA     (sonido + visual)
        - Cambio a PRUDENTE → Alerta MODERADA     (visual)
        - Cambio a FALLECIDO → Alerta CRITICA     (sonido + visual)
        - Resto de cambios  → Alerta INFORMATIVA  (solo registro)
    """

    def __init__(self, sonido_activado: bool = True):
        """
        Constructor del notificador.

        Args:
            sonido_activado: Si es True, intenta reproducir sonido en alertas
                             críticas. False = solo alertas visuales/log.
        """
        # Lista de todas las alertas generadas
        self._notificaciones: list[Alerta] = []

        # Control de sonido
        self._sonido_activado = sonido_activado

        # Contador de alertas críticas (para estadísticas rápidas)
        self._total_criticas = 0

        # Callback para interfaz gráfica (se configurará en Sprint 5-6)
        self._callback_visual = None

        # Alarma sonora activa de sala (solo una a la vez con winsound)
        self._alarma_sala_activa: bool = False

    # ==================================================================
    # CALLBACK PARA EL MONITOR (PATRÓN OBSERVER)
    # ==================================================================

    def recibir_cambio(self, cambio: CambioEstado) -> None:
        """
        Callback que recibe un CambioEstado del MonitorSignos.

        Este método se registra en MonitorSignos.registrar_observador()
        para que el monitor notifique automáticamente cada cambio.

        Args:
            cambio: Objeto CambioEstado con los detalles del cambio.
        """
        # Determinar el tipo de alerta según el nuevo estado
        if cambio.estado_nuevo in (ESTADO_CRITICO, ESTADO_ATENCION):
            tipo = "CRITICA"
        elif cambio.estado_nuevo == ESTADO_FALLECIDO:
            tipo = "CRITICA"
        elif cambio.estado_nuevo == ESTADO_PRUDENTE:
            tipo = "MODERADA"
        else:
            tipo = "INFORMATIVA"

        # Construir el mensaje descriptivo
        if cambio.es_agravamiento:
            direccion = "EMPEORÓ"
        elif cambio.es_mejoria:
            direccion = "MEJORÓ"
        else:
            direccion = "CAMBIO"

        mensaje = (
            f"{direccion}: {cambio.paciente.nombre} "
            f"pasó de {cambio.estado_anterior} a {cambio.estado_nuevo}"
        )

        # Crear y registrar la alerta
        alerta = Alerta(
            tipo=tipo,
            mensaje=mensaje,
            paciente=cambio.paciente,
            momento=cambio.momento,
        )
        self._notificaciones.append(alerta)

        # Acciones según el tipo de alerta
        if alerta.es_critica:
            self._total_criticas += 1
            self._emitir_alerta_critica(alerta)
        elif tipo == "MODERADA":
            self._emitir_alerta_visual(alerta)
        else:
            # Las informativas solo se registran en el log
            pass

    # ==================================================================
    # EMISIÓN DE ALERTAS
    # ==================================================================

    def _emitir_alerta_critica(self, alerta: Alerta) -> None:
        """
        Acciones a tomar cuando se genera una alerta crítica:
          1. Mostrar alerta visual en consola.
          2. Reproducir sonido de alarma (si está activado).
             Para sala usa genhi.wav en bucle; para emergencias alerta.wav.
          3. Invocar callback de GUI si está configurado.
        """
        self.mostrar_alerta_consola(alerta)
        if self._sonido_activado:
            es_sala = isinstance(alerta.paciente, PacienteSala)
            if es_sala:
                self._iniciar_alarma_sala(alerta.paciente.id_paciente)
            else:
                self.reproducir_alerta_sonora()
        if self._callback_visual:
            try:
                self._callback_visual(alerta)
            except Exception:
                pass

    def _emitir_alerta_visual(self, alerta: Alerta) -> None:
        """
        Muestra una alerta moderada solo en consola.
        """
        self.mostrar_alerta_consola(alerta)

    def mostrar_alerta_consola(self, alerta: Alerta) -> None:
        """
        Imprime una representación visual de la alerta en la terminal.
        Usa prefijos de color ANSI cuando es posible.

        Args:
            alerta: La instancia de Alerta a mostrar.
        """
        prefijo = ""
        if alerta.tipo == "CRITICA":
            prefijo = "[!!!] "
        elif alerta.tipo == "MODERADA":
            prefijo = "[ ! ] "

        print(prefijo + str(alerta))

    def reproducir_alerta_sonora(self) -> bool:
        """
        Reproduce el archivo de sonido de alarma usando winsound (nativo de Windows).

        Returns:
            True si se reprodujo el sonido, False en caso contrario.
        """
        if not os.path.exists(RUTA_ALERTA_WAV):
            print(f"    (sonido: archivo no encontrado en '{RUTA_ALERTA_WAV}')")
            return False

        try:
            winsound.PlaySound(RUTA_ALERTA_WAV, winsound.SND_ASYNC)
            return True
        except Exception as e:
            print(f"    (sonido: error al reproducir: {e})")
            return False

    # ==================================================================
    # ALARMA SONORA CONTINUA PARA SALA
    # ==================================================================

    def _iniciar_alarma_sala(self, id_paciente: str) -> None:
        """
        Inicia la reproducción en bucle manual de genhi.wav. Reproduce
        el audio una vez, espera 5 segundos (4s de audio + 1s buffer),
        y repite. Sin superposición porque cada reproducción termina
        antes de iniciar la siguiente.

        Args:
            id_paciente: ID del paciente que activó la alarma.
        """
        if self._alarma_sala_activa:
            return

        if not os.path.exists(RUTA_ALERTA_SALA_WAV):
            print(f"    (sonido sala: archivo no encontrado en '{RUTA_ALERTA_SALA_WAV}')")
            return

        self._alarma_sala_activa = True

        def _bucle():
            while self._alarma_sala_activa:
                try:
                    winsound.PlaySound(RUTA_ALERTA_SALA_WAV, winsound.SND_ASYNC)
                except Exception:
                    break
                time.sleep(6.2)

        hilo = threading.Thread(target=_bucle, daemon=True)
        hilo.start()

    def detener_alarma_sala(self, id_paciente: str) -> None:
        """
        Detiene la alarma sonora de sala: corta la reproducción en curso
        y marca el flag para que el bucle no reinicie.

        Args:
            id_paciente: ID del paciente cuya alarma se va a detener.
        """
        self._alarma_sala_activa = False
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    # ==================================================================
    # CONFIGURACIÓN DE CALLBACK PARA GUI
    # ==================================================================

    def configurar_callback_visual(self, callback) -> None:
        """
        Configura un callback que será invocado cuando se genere una
        alerta crítica. La GUI usará esto para mostrar tarjetas
        parpadeantes, notificaciones emergentes, etc.

        Args:
            callback: Función que recibe una instancia de Alerta.
        """
        self._callback_visual = callback

    # ==================================================================
    # CONSULTA DE NOTIFICACIONES
    # ==================================================================

    @property
    def notificaciones(self) -> list[Alerta]:
        """Lista completa de alertas generadas."""
        return list(self._notificaciones)

    @property
    def total_notificaciones(self) -> int:
        """Cantidad total de alertas generadas."""
        return len(self._notificaciones)

    @property
    def total_criticas(self) -> int:
        """Cantidad de alertas críticas generadas."""
        return self._total_criticas

    def notificaciones_recientes(self, cantidad: int = 10) -> list[Alerta]:
        """
        Devuelve las N alertas más recientes.

        Args:
            cantidad: Número de alertas a devolver.

        Returns:
            Lista de las últimas Alerta generadas.
        """
        return self._notificaciones[-cantidad:]

    def alertas_pendientes(self) -> list[Alerta]:
        """
        Devuelve las alertas que aún no han sido marcadas como atendidas.

        Returns:
            Lista de Alerta no atendidas.
        """
        return [a for a in self._notificaciones if not a.atendida]

    def alertas_criticas(self) -> list[Alerta]:
        """
        Devuelve solo las alertas de tipo CRITICA.

        Returns:
            Lista de Alerta críticas.
        """
        return [a for a in self._notificaciones if a.es_critica]

    def alertas_por_paciente(self, id_paciente: str) -> list[Alerta]:
        """
        Filtra las alertas asociadas a un paciente específico.

        Args:
            id_paciente: ID del paciente.

        Returns:
            Lista de Alerta de ese paciente.
        """
        return [
            a for a in self._notificaciones
            if a.paciente and a.paciente.id_paciente == id_paciente
        ]

    def marcar_todas_atendidas(self) -> int:
        """
        Marca todas las alertas pendientes como atendidas.

        Returns:
            Cantidad de alertas marcadas.
        """
        pendientes = self.alertas_pendientes()
        for alerta in pendientes:
            alerta.marcar_atendida()
        return len(pendientes)

    # ==================================================================
    # CONTROL DE SONIDO
    # ==================================================================

    def activar_sonido(self) -> None:
        """Activa las alertas sonoras."""
        self._sonido_activado = True
        print("    Sonido de alerta: ACTIVADO")

    def desactivar_sonido(self) -> None:
        """Desactiva las alertas sonoras (modo silencioso)."""
        self._sonido_activado = False
        print("    Sonido de alerta: DESACTIVADO")

    @property
    def sonido_activado(self) -> bool:
        """Indica si las alertas sonoras están activadas."""
        return self._sonido_activado

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================

    def __str__(self) -> str:
        """Representación resumida del notificador."""
        pendientes = len(self.alertas_pendientes())
        sonido = "ON" if self._sonido_activado else "OFF"
        return (
            f"Notificador: {self.total_notificaciones} alertas totales\n"
            f"  Críticas:   {self._total_criticas}\n"
            f"  Pendientes: {pendientes}\n"
            f"  Sonido:     {sonido}"
        )

    def __repr__(self) -> str:
        """Representación técnica."""
        return (
            f"Notificador(alertas={self.total_notificaciones}, "
            f"criticas={self._total_criticas}, "
            f"sonido={self._sonido_activado})"
        )

    def __len__(self) -> int:
        """Cantidad total de alertas."""
        return self.total_notificaciones


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo Notificador.
    Demuestra:
      1. Creación de Alerta con distintos tipos.
      2. Registro del notificador como observador del monitor.
      3. Generación automática de alertas al detectar cambios.
      4. Clasificación correcta: CRITICO → CRITICA, PRUDENTE → MODERADA.
      5. Consulta de notificaciones, pendientes, por paciente.
      6. Marcar alertas como atendidas.
      7. Control de sonido (activar/desactivar).
      8. Integración completa: generador → repositorio → monitor → notificador.
    """
    from datos.generador import GeneradorDatos
    from alertas.monitor import MonitorSignos, CambioEstado

    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: Notificador")
    print("=" * 60)

    generador = GeneradorDatos(semilla=42)
    monitor = MonitorSignos()
    notificador = Notificador(sonido_activado=False)  # Sin sonido en pruebas

    # --- Prueba 1: Crear alertas manualmente ---
    print("\n[1] Crear alertas manuales de cada tipo:")
    a1 = Alerta("CRITICA", "Paciente con paro cardiorrespiratorio")
    a2 = Alerta("MODERADA", "Signos vitales alterados")
    a3 = Alerta("INFORMATIVA", "Paciente dado de alta")
    print(f"    {a1}")
    print(f"    {a2}")
    print(f"    {a3}")

    # --- Prueba 2: Validación de tipo de alerta ---
    print("\n[2] Intentar crear alerta con tipo inválido:")
    try:
        Alerta("INVENTADO", "Esto debería fallar")
        print("    ERROR: No se lanzó la excepción.")
    except ValueError as e:
        print(f"    ValueError: {e}")

    # --- Prueba 3: Suscribir notificador al monitor ---
    print("\n[3] Suscribir notificador al monitor:")
    monitor.registrar_observador(notificador.recibir_cambio)
    print(f"    Observadores del monitor: {len(monitor._observadores)}")

    # --- Prueba 4: Generar pacientes y monitorearlos ---
    print("\n[4] Generar 4 pacientes y agregarlos al monitor:")
    pacientes_sala = generador.generar_pacientes_sala(cantidad=2)
    pacientes_emerg = generador.generar_pacientes_emergencia(cantidad=2)
    monitor.agregar_pacientes(pacientes_sala)
    monitor.agregar_pacientes(pacientes_emerg)
    monitor.evaluar_todos()  # Primera evaluación (sin alertas, sin estado previo)
    print(f"    Pacientes: {monitor.total_monitoreados}")
    for p in monitor.pacientes_monitoreados:
        print(f"    {p.id_paciente}: {p.nombre:<28} {p.estado}")

    # --- Prueba 5: Forzar cambios críticos y ver alertas ---
    print("\n[5] Forzar estado CRITICO en dos pacientes:")
    lista = monitor.pacientes_monitoreados
    p1 = lista[0]
    p2 = lista[1]

    # Forzamos signos críticos sin pasar por el setter
    from modelos.signos_vitales import SignosVitales
    p1._signos_vitales = SignosVitales(
        frecuencia_cardiaca=140.0, frecuencia_respiratoria=30.0,
        saturacion_oxigeno=82.0, presion_sistolica=70.0,
        presion_diastolica=40.0, temperatura=39.5,
    )
    p2._signos_vitales = SignosVitales(
        frecuencia_cardiaca=38.0, frecuencia_respiratoria=10.0,
        saturacion_oxigeno=88.0, presion_sistolica=160.0,
        presion_diastolica=100.0, temperatura=38.0,
    )
    cambios = monitor.evaluar_todos()
    print(f"    Cambios detectados: {len(cambios)}")
    print(f"    Alertas generadas:  {notificador.total_notificaciones}")

    # --- Prueba 6: Simular varios ticks ---
    print("\n[6] Simular 3 ticks de monitoreo:")
    for tick in range(1, 4):
        import random
        random.seed(tick * 42)
        cambios_tick = monitor.simular_tick()
        print(f"    Tick {tick}: {len(cambios_tick)} cambios, "
              f"total alertas acumuladas: {notificador.total_notificaciones}")

    # --- Prueba 7: Resumen del notificador ---
    print(f"\n[7] Estado del notificador:\n{notificador}")

    # --- Prueba 8: Alertas críticas ---
    print(f"\n[8] Alertas críticas: {len(notificador.alertas_criticas())}")
    for a in notificador.alertas_criticas():
        print(f"    {a}")

    # --- Prueba 9: Alertas pendientes ---
    pendientes = notificador.alertas_pendientes()
    print(f"\n[9] Alertas pendientes: {len(pendientes)}")
    for a in pendientes[:5]:  # Primeras 5
        print(f"    {a}")

    # --- Prueba 10: Marcar como atendidas ---
    print(f"\n[10] Marcar todas como atendidas:")
    marcadas = notificador.marcar_todas_atendidas()
    print(f"    Marcadas: {marcadas}")
    print(f"    Pendientes restantes: {len(notificador.alertas_pendientes())}")

    # --- Prueba 11: Notificaciones recientes ---
    print("\n[11] Últimas 3 notificaciones:")
    for a in notificador.notificaciones_recientes(3):
        print(f"    {a}")

    # --- Prueba 12: Alertas por paciente ---
    id_primero = monitor.pacientes_monitoreados[0].id_paciente
    alertas_p1 = notificador.alertas_por_paciente(id_primero)
    print(f"\n[12] Alertas del paciente {id_primero}: {len(alertas_p1)}")
    for a in alertas_p1[:3]:
        print(f"    {a}")

    # --- Prueba 13: Control de sonido ---
    print("\n[13] Control de sonido:")
    print(f"    Estado actual: {'ON' if notificador.sonido_activado else 'OFF'}")
    notificador.activar_sonido()
    notificador.desactivar_sonido()

    # --- Prueba 14: Callback visual personalizado ---
    print("\n[14] Configurar callback visual personalizado:")
    eventos_gui = []

    def callback_personalizado(alerta: Alerta):
        eventos_gui.append(alerta)
        print(f"    [GUI] Mostraría tarjeta roja parpadeante para: "
              f"{alerta.paciente.nombre if alerta.paciente else 'N/A'}")

    notificador.configurar_callback_visual(callback_personalizado)

    # Forzamos otro cambio crítico para probar el callback
    p3 = monitor.pacientes_monitoreados[2]
    p3._signos_vitales = SignosVitales(
        frecuencia_cardiaca=145.0, frecuencia_respiratoria=35.0,
        saturacion_oxigeno=78.0, presion_sistolica=60.0,
        presion_diastolica=35.0, temperatura=40.0,
    )
    monitor.evaluar_todos()
    print(f"    Callbacks GUI invocados: {len(eventos_gui)}")

    # --- Prueba 15: __repr__ y __len__ ---
    print(f"\n[15] Representación técnica: {repr(notificador)}")
    print(f"    len(notificador) = {len(notificador)}")

    print("\n[OK] Pruebas de Notificador completadas.\n")
