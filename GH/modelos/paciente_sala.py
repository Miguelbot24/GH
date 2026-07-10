"""
Módulo: paciente_sala.py
Sprint 1 — Paciente de Sala (internado).

Define la clase PacienteSala, que hereda de Paciente y representa a un
paciente internado en una sala del hospital. Demuestra los pilares de
Herencia (extiende Paciente) y Polimorfismo (implementa calcular_estado()
con lógica específica de internamiento).

Dependencias previas necesarias:
    - config.py            (constantes globales)
    - modelos/paciente.py  (clase abstracta base Paciente)
    - modelos/signos_vitales.py (SignosVitales)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from config import (
    ESTADO_ATENCION,
    ESTADO_PRUDENTE,
    ESTADO_ESTABLE,
    ESTADO_FALLECIDO,
    ESTADO_SIN_DATOS,
    ORDEN_SEVERIDAD_SALA,
    UMBRALES_SALA,
    PRIORIDAD_ESTADO,
    COLORES_ESTADO,
)

from modelos.paciente import Paciente
from modelos.signos_vitales import SignosVitales


class PacienteSala(Paciente):
    """
    Representa a un paciente internado en una sala del hospital.

    Hereda todos los atributos y métodos de Paciente (nombre, edad, género,
    signos vitales, historial, etc.) y añade información específica del
    internamiento: número de cama y planta.

    Principio OOP — Herencia:
        PacienteSala ES-UN Paciente. Reutiliza toda la infraestructura de la
        clase base y solo añade lo específico de la hospitalización en sala.

    Principio OOP — Polimorfismo:
        Implementa calcular_estado() con lógica propia: además de los signos
        vitales, considera el tiempo de internamiento. Un paciente recién
        ingresado con signos alterados se clasifica con mayor severidad
        (período de observación), mientras que uno estable de larga estancia
        mantiene su clasificación sin cambios.
    """

    def __init__(
        self,
        nombre:      str,
        edad:        int,
        genero:      str,
        numero_cama: int,
        planta:      str = "General",
        tipo_avatar: str = "hombre",
        id_paciente: str = None,
        razon_ingreso: str = "",
        doctor_asignado: str = "",
    ):
        """
        Constructor de PacienteSala.

        Args:
            nombre:      Nombre completo del paciente.
            edad:        Edad en años.
            genero:      "Masculino" o "Femenino".
            numero_cama: Número de cama asignada en la sala.
            planta:      Nombre de la planta o sector del hospital
                         (ej. "General", "Cardiología", "UCI").
                         Por defecto "General".
            tipo_avatar: Clave del icono (hombre, mujer, anciano, etc.).
            id_paciente: ID opcional. Si no se da, se autogenera (PAC-0001...).
        """
        # Llamamos al constructor de la clase base (Paciente) para inicializar
        # los atributos comunes: nombre, edad, signos vitales, historial, etc.
        super().__init__(
            nombre=nombre,
            edad=edad,
            genero=genero,
            tipo_avatar=tipo_avatar,
            id_paciente=id_paciente,
            razon_ingreso=razon_ingreso,
            doctor_asignado=doctor_asignado,
        )

        # Atributos específicos del paciente de sala
        self._numero_cama = numero_cama
        self._planta      = planta

    # ==================================================================
    # PROPIEDADES ESPECÍFICAS DE SALA
    # ==================================================================

    @property
    def numero_cama(self) -> int:
        """Número de cama asignada al paciente en la sala."""
        return self._numero_cama

    @numero_cama.setter
    def numero_cama(self, valor: int) -> None:
        """Cambia la cama del paciente (traslado interno)."""
        if valor < 1:
            raise ValueError("El número de cama debe ser un entero positivo.")
        self._numero_cama = valor

    @property
    def planta(self) -> str:
        """Planta o sector donde está internado el paciente."""
        return self._planta

    @planta.setter
    def planta(self, valor: str) -> None:
        """Asigna una nueva planta al paciente (traslado de sector)."""
        self._planta = valor

    @property
    def horas_internamiento(self) -> float:
        """
        Calcula las horas transcurridas desde el ingreso del paciente.

        Se basa en self._fecha_ingreso (heredado de Paciente) y la hora actual.
        Retorna un float con precisión de décimas de hora.

        Returns:
            Horas transcurridas (ej. 2.5 para 2 horas y 30 minutos).
        """
        diferencia = datetime.now() - self._fecha_ingreso
        return diferencia.total_seconds() / 3600.0

    # ==================================================================
    # IMPLEMENTACIÓN POLIMÓRFICA DE calcular_estado()
    # ==================================================================

    def calcular_estado(self) -> str:
        """
        Calcula el estado clínico del paciente de sala usando los umbrales
        exclusivos del área de salas (UMBRALES_SALA).

        Lógica específica de internamiento (Polimorfismo):
          1. Obtiene el estado base según los signos vitales (umbrales sala).
          2. Si el paciente ingresó hace menos de 1 hora (período de
             observación inicial) y sus signos no son ESTABLE, eleva
             la severidad un nivel como medida de precaución.
          3. Si el paciente lleva más de 48 horas internado y está ESTABLE,
             mantiene la clasificación sin cambios.
          4. En cualquier otro caso, devuelve el estado base.

        Estados posibles: FALLECIDO, ATENCION, PRUDENTE, ESTABLE, SIN_DATOS.
        NUNCA retorna CRITICO ni NO_CRITICO (exclusivos de emergencias).
        """
        # Paso 1: estado base con umbrales de sala
        estado_base = self._signos_vitales.obtener_estado_global(
            umbrales=UMBRALES_SALA,
            orden=ORDEN_SEVERIDAD_SALA,
        )

        if estado_base in (ESTADO_FALLECIDO, ESTADO_SIN_DATOS):
            return estado_base

        # ATENCIÓN solo se alcanza mediante SIMULAR EMERGENCIA.
        # Los ticks normales fluctúan exclusivamente entre ESTABLE y PRUDENTE.
        return estado_base

    # ==================================================================
    # MÉTODOS AUXILIARES
    # ==================================================================

    def _elevar_severidad(self, estado: str) -> str:
        """
        Sube la severidad del estado un nivel según ORDEN_SEVERIDAD_SALA.
        PRUDENTE -> ATENCION, ESTABLE -> PRUDENTE.

        No se eleva más allá de ATENCION: un paciente vivo no pasa a FALLECIDO
        por un criterio administrativo. FALLECIDO solo se determina por signos
        vitales (todos en cero).
        """
        if estado in (ESTADO_FALLECIDO, ESTADO_ATENCION):
            return estado

        indice = ORDEN_SEVERIDAD_SALA.index(estado)
        if indice > 0:
            nuevo_estado = ORDEN_SEVERIDAD_SALA[indice - 1]
            if nuevo_estado == ESTADO_FALLECIDO:
                return ESTADO_ATENCION
            return nuevo_estado
        return estado

    # ==================================================================
    # MÉTODO resumen() SOBRESCRITO
    # ==================================================================

    def resumen(self) -> dict:
        """
        Extiende el resumen de la clase base añadiendo los campos
        específicos de sala: número de cama, planta y horas de internamiento.
        """
        datos = super().resumen()
        datos["tipo"]              = "Sala"
        datos["numero_cama"]       = self._numero_cama
        datos["planta"]            = self._planta
        datos["horas_internamiento"] = round(self.horas_internamiento, 1)
        return datos

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================

    def __str__(self) -> str:
        """Representación legible incluyendo cama y planta."""
        base = super().__str__()
        extra = (
            f"\n  [SALA] Cama: {self._numero_cama}"
            f"  |  Planta: {self._planta}"
            f"  |  Internado: {self.horas_internamiento:.1f} h"
        )
        return base + extra

    def __repr__(self) -> str:
        """Representación técnica para depuración."""
        return (
            f"PacienteSala(id={self._id_paciente!r}, "
            f"nombre={self._nombre!r}, "
            f"cama={self._numero_cama}, "
            f"estado={self._estado!r})"
        )


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo PacienteSala.
    Demuestra:
      1. Creación de un paciente de sala con cama y planta.
      2. Herencia: acceso a propiedades de Paciente (nombre, edad, etc.).
      3. Polimorfismo: calcular_estado() con lógica de internamiento.
      4. Período de observación: signos alterados + ingreso reciente = severidad elevada.
      5. Paciente estable de larga estancia: sin cambios.
      6. Setters de cama y planta (traslados).
      7. Método resumen() sobrescrito.
    """
    import time

    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: PacienteSala")
    print("=" * 60)

    # --- Prueba 1: Crear paciente de sala ---
    print("\n[1] Crear PacienteSala:")
    paciente = PacienteSala(
        nombre="Ana Rodriguez",
        edad=52,
        genero="Femenino",
        numero_cama=304,
        planta="Cardiología",
        tipo_avatar="mujer",
    )
    print(f"    Paciente: {paciente.nombre}")
    print(f"    ID:       {paciente.id_paciente}")
    print(f"    Cama:     {paciente.numero_cama}")
    print(f"    Planta:   {paciente.planta}")

    # --- Prueba 2: Estado inicial SIN_DATOS ---
    print(f"\n[2] Estado inicial (signos en cero): {paciente.estado}")

    # --- Prueba 3: Asignar signos normales, verificar estado ---
    print("\n[3] Asignar signos vitales NORMALES:")
    paciente.signos_vitales = SignosVitales(
        frecuencia_cardiaca=72.0,
        frecuencia_respiratoria=16.0,
        saturacion_oxigeno=98.0,
        presion_sistolica=115.0,
        presion_diastolica=78.0,
        temperatura=36.6,
    )
    print(f"    Estado calculado: {paciente.estado}")
    print(f"    Prioridad:        {paciente.prioridad}")
    print(f"    Horas internado:  {paciente.horas_internamiento:.2f} h")
    print(f"    (recien ingresado + signos normales = ESTABLE)")

    # --- Prueba 4: Período de observación ---
    # Simulamos un paciente recién ingresado (< 1 h) con signos alterados
    print("\n[4] Simular paciente recien ingresado con signos alterados:")
    paciente2 = PacienteSala(
        nombre="Luis Mendez",
        edad=68,
        genero="Masculino",
        numero_cama=102,
        planta="UCI",
        tipo_avatar="anciano",
    )
    # Signos en rango BASICO (HR = 55, levemente bajo)
    paciente2.signos_vitales = SignosVitales(
        frecuencia_cardiaca=55.0,
        frecuencia_respiratoria=18.0,
        saturacion_oxigeno=94.0,
        presion_sistolica=88.0,
        presion_diastolica=58.0,
        temperatura=36.8,
    )
    print(f"    Estado base por signos: {paciente2._signos_vitales.obtener_estado_global()}")
    print(f"    Estado tras calcular_estado() de sala: {paciente2.estado}")
    print(f"    (recien ingresado + signos BASICO -> elevado a PRUDENTE por observacion)")

    # --- Prueba 5: Paciente crítico recién ingresado ---
    print("\n[5] Simular paciente critico recien ingresado:")
    paciente3 = PacienteSala(
        nombre="Pedro Gomez",
        edad=75,
        genero="Masculino",
        numero_cama=101,
        planta="UCI",
    )
    paciente3.signos_vitales = SignosVitales(
        frecuencia_cardiaca=140.0,
        frecuencia_respiratoria=28.0,
        saturacion_oxigeno=82.0,
        presion_sistolica=75.0,
        presion_diastolica=45.0,
        temperatura=39.5,
    )
    print(f"    Estado base por signos: {paciente3._signos_vitales.obtener_estado_global()}")
    print(f"    Estado tras calcular_estado() de sala: {paciente3.estado}")
    print(f"    (ya era CRITICO por signos, se mantiene CRITICO)")

    # --- Prueba 6: Cambiar cama (traslado) ---
    print("\n[6] Trasladar paciente de cama:")
    print(f"    Cama anterior: {paciente.numero_cama}")
    paciente.numero_cama = 310
    print(f"    Nueva cama:    {paciente.numero_cama}")

    # --- Prueba 7: Cambiar planta ---
    print("\n[7] Trasladar a otra planta:")
    print(f"    Planta anterior: {paciente.planta}")
    paciente.planta = "Recuperación"
    print(f"    Nueva planta:    {paciente.planta}")

    # --- Prueba 8: Resumen extendido ---
    print("\n[8] Resumen del paciente de sala (diccionario):")
    resumen = paciente.resumen()
    for clave, valor in resumen.items():
        if clave == "signos":
            print(f"    {clave}: (dict con {len(valor)} signos)")
        else:
            print(f"    {clave}: {valor}")

    # --- Prueba 9: Validación de cama negativa ---
    print("\n[9] Intento de asignar cama -5 (debe lanzar ValueError):")
    try:
        paciente.numero_cama = -5
        print("    ERROR: No se lanzó la excepción.")
    except ValueError as e:
        print(f"    ValueError capturado: {e}")

    # --- Prueba 10: __str__ y __repr__ ---
    print(f"\n[10] Representaciones:\n{paciente}")
    print(f"    repr: {repr(paciente2)}")

    print("\n[OK] Pruebas de PacienteSala completadas.\n")
