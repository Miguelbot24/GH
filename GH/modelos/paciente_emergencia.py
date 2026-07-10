"""
Módulo: paciente_emergencia.py
Sprint 1 — Paciente de Emergencias (urgencias).

Define la clase PacienteEmergencia, que hereda de Paciente y representa a un
paciente en el área de urgencias del hospital. Demuestra los pilares de
Herencia (extiende Paciente) y Polimorfismo (implementa calcular_estado()
con lógica específica de triaje de emergencias).

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
    ESTADO_CRITICO,
    ESTADO_NO_CRITICO,
    ESTADO_FALLECIDO,
    ESTADO_SIN_DATOS,
    UMBRALES_EMERGENCIA,
    ORDEN_SEVERIDAD_EMERGENCIA,
    PRIORIDAD_ESTADO,
    COLORES_ESTADO,
)

from modelos.paciente import Paciente
from modelos.signos_vitales import SignosVitales


class PacienteEmergencia(Paciente):
    """
    Representa a un paciente en el área de urgencias/emergencias.

    Hereda todos los atributos y métodos de Paciente y añade información
    específica del triaje de emergencias: prioridad administrativa asignada
    en la admisión (1 a 5) y tiempo de espera desde el ingreso.

    Principio OOP — Herencia:
        PacienteEmergencia ES-UN Paciente. Reutiliza toda la infraestructura
        de la clase base y añade lo específico del contexto de urgencias.

    Principio OOP — Polimorfismo:
        Implementa calcular_estado() con lógica propia que, además de los
        signos vitales, considera:
          - Prioridad administrativa asignada en admisión (1..5).
          - Tiempo de espera acumulado desde el ingreso.
        Un paciente con prioridad administrativa alta ve elevada su
        clasificación clínica. Un paciente que espera demasiado con signos
        alterados también sube de severidad.
    """

    # Niveles válidos de prioridad administrativa
    PRIORIDAD_MINIMA = 1
    PRIORIDAD_MAXIMA = 5

    def __init__(
        self,
        nombre:                 str,
        edad:                   int,
        genero:                 str,
        prioridad_administrativa: int = 3,
        motivo_consulta:        str = "No especificado",
        tipo_avatar:            str = "hombre",
        id_paciente:            str = None,
        razon_ingreso:          str = "",
        doctor_asignado:        str = "",
    ):
        """
        Constructor de PacienteEmergencia.

        Args:
            nombre:        Nombre completo del paciente.
            edad:          Edad en años.
            genero:        "Masculino" o "Femenino".
            prioridad_administrativa: Nivel de prioridad asignado en la
                           admisión de emergencias (1 = baja, 5 = máxima).
                           Por defecto 3 (media).
            motivo_consulta: Motivo por el que acude a emergencias
                           (ej. "Dolor torácico", "Traumatismo").
            tipo_avatar:   Clave del icono (hombre, mujer, anciano, etc.).
            id_paciente:   ID opcional. Si no se da, se autogenera.
        """
        super().__init__(
            nombre=nombre,
            edad=edad,
            genero=genero,
            tipo_avatar=tipo_avatar,
            id_paciente=id_paciente,
            razon_ingreso=razon_ingreso,
            doctor_asignado=doctor_asignado,
        )

        # Validar y almacenar la prioridad administrativa
        self._prioridad_administrativa = self._validar_prioridad(
            prioridad_administrativa
        )

        # Motivo de consulta (dolor torácico, traumatismo, etc.)
        self._motivo_consulta = motivo_consulta

    # ==================================================================
    # PROPIEDADES ESPECÍFICAS DE EMERGENCIAS
    # ==================================================================

    @property
    def prioridad_administrativa(self) -> int:
        """
        Prioridad administrativa asignada en la admisión de emergencias.
        Escala de 1 (baja) a 5 (máxima urgencia).
        Influye en calcular_estado(): una prioridad alta puede elevar
        la clasificación clínica del paciente.
        """
        return self._prioridad_administrativa

    @prioridad_administrativa.setter
    def prioridad_administrativa(self, valor: int) -> None:
        """
        Cambia la prioridad administrativa del paciente.
        Útil si un médico reevalúa la urgencia tras la admisión inicial.
        Al cambiar, se recalcula el estado automáticamente.
        """
        self._prioridad_administrativa = self._validar_prioridad(valor)
        self.actualizar_estado()

    @property
    def motivo_consulta(self) -> str:
        """Motivo por el que el paciente acudió a emergencias."""
        return self._motivo_consulta

    @motivo_consulta.setter
    def motivo_consulta(self, valor: str) -> None:
        """Actualiza el motivo de consulta."""
        self._motivo_consulta = valor

    @property
    def minutos_espera(self) -> float:
        """
        Minutos transcurridos desde que el paciente ingresó a emergencias.

        Se calcula a partir de self._fecha_ingreso (heredado de Paciente).
        Retorna un float con los minutos totales.

        Returns:
            Minutos de espera acumulados (ej. 45.5 para 45 min 30 s).
        """
        diferencia = datetime.now() - self._fecha_ingreso
        return diferencia.total_seconds() / 60.0

    # ==================================================================
    # IMPLEMENTACIÓN POLIMÓRFICA DE calcular_estado()
    # ==================================================================

    def calcular_estado(self) -> str:
        """
        Calcula el estado clínico del paciente de emergencias usando los
        umbrales exclusivos del área (UMBRALES_EMERGENCIA).

        Lógica específica de triaje (Polimorfismo):
          1. Obtiene el estado base según los signos vitales (CRITICO o NO_CRITICO).
          2. Prioridad administrativa 5 y signos NO_CRITICO → eleva a CRITICO.
          3. Tiempo de espera > 120 min con signos alterados → eleva a CRITICO.

        Estados posibles: FALLECIDO, CRITICO, NO_CRITICO.
        NUNCA retorna ESTABLE, PRUDENTE, ATENCION ni SIN_DATOS.
        """
        estado_base = self._signos_vitales.obtener_estado_global(
            umbrales=UMBRALES_EMERGENCIA,
            orden=ORDEN_SEVERIDAD_EMERGENCIA,
        )

        if estado_base == ESTADO_FALLECIDO:
            return estado_base

        if estado_base == ESTADO_CRITICO:
            return ESTADO_CRITICO  # Ya crítico, no puede empeorar

        # estado_base es NO_CRITICO — aplicar modificadores
        minutos   = self.minutos_espera
        prioridad = self._prioridad_administrativa

        # Prioridad máxima (5) eleva a CRITICO inmediatamente
        if prioridad == 5:
            return ESTADO_CRITICO

        # Tiempo de espera > 120 min con prioridad alta (4)
        if minutos > 120.0 and prioridad >= 4:
            return ESTADO_CRITICO

        # Tiempo de espera extremo (> 180 min)
        if minutos > 180.0:
            return ESTADO_CRITICO

        return ESTADO_NO_CRITICO

    # ==================================================================
    # MÉTODOS AUXILIARES
    # ==================================================================

    def _validar_prioridad(self, valor: int) -> int:
        """
        Valida que la prioridad administrativa esté en el rango 1..5.

        Args:
            valor: Prioridad a validar.

        Returns:
            El mismo valor si es válido.

        Raises:
            ValueError: Si el valor está fuera de rango.
        """
        if not (self.PRIORIDAD_MINIMA <= valor <= self.PRIORIDAD_MAXIMA):
            raise ValueError(
                f"Prioridad administrativa debe estar entre "
                f"{self.PRIORIDAD_MINIMA} y {self.PRIORIDAD_MAXIMA}. "
                f"Recibido: {valor}"
            )
        return int(valor)

    def _elevar_severidad(self, estado: str) -> str:
        """
        Sube la severidad dentro de los estados de emergencia.
        NO_CRITICO -> CRITICO.
        CRITICO y FALLECIDO no se modifican.
        """
        if estado in (ESTADO_FALLECIDO, ESTADO_CRITICO):
            return estado
        if estado == ESTADO_NO_CRITICO:
            return ESTADO_CRITICO
        return estado

    def tiempo_espera_legible(self) -> str:
        """
        Devuelve el tiempo de espera en formato legible.

        Returns:
            Cadena como '1h 25m' o '45m'.
        """
        total_minutos = int(self.minutos_espera)
        horas   = total_minutos // 60
        minutos = total_minutos % 60
        if horas > 0:
            return f"{horas}h {minutos}m"
        return f"{minutos}m"

    # ==================================================================
    # MÉTODO resumen() SOBRESCRITO
    # ==================================================================

    def resumen(self) -> dict:
        """
        Extiende el resumen de la clase base añadiendo los campos
        específicos de emergencias: prioridad administrativa, motivo de
        consulta y tiempo de espera.
        """
        datos = super().resumen()
        datos["tipo"]                     = "Emergencia"
        datos["prioridad_administrativa"] = self._prioridad_administrativa
        datos["motivo_consulta"]          = self._motivo_consulta
        datos["minutos_espera"]           = round(self.minutos_espera, 1)
        datos["espera_legible"]           = self.tiempo_espera_legible()
        return datos

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================

    def __str__(self) -> str:
        """Representación legible incluyendo datos de triaje."""
        base = super().__str__()
        extra = (
            f"\n  [EMERGENCIA] Prioridad adm: {self._prioridad_administrativa}/5"
            f"  |  Espera: {self.tiempo_espera_legible()}"
            f"  |  Motivo: {self._motivo_consulta}"
        )
        return base + extra

    def __repr__(self) -> str:
        """Representación técnica para depuración."""
        return (
            f"PacienteEmergencia(id={self._id_paciente!r}, "
            f"nombre={self._nombre!r}, "
            f"prioridad_adm={self._prioridad_administrativa}, "
            f"estado={self._estado!r})"
        )


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo PacienteEmergencia.
    Demuestra:
      1. Creación de un paciente de emergencias con prioridad adm. y motivo.
      2. Herencia: acceso a propiedades de Paciente.
      3. Polimorfismo: calcular_estado() con lógica de triaje.
      4. Efecto de prioridad administrativa 5 sobre estado ESTABLE.
      5. Efecto de tiempo de espera prolongado sobre signos alterados.
      6. Validación de rango de prioridad administrativa.
      7. Setters de prioridad (reevaluación) y motivo de consulta.
      8. Método resumen() sobrescrito.
    """
    import time

    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: PacienteEmergencia")
    print("=" * 60)

    # --- Prueba 1: Crear paciente de emergencias ---
    print("\n[1] Crear PacienteEmergencia:")
    paciente = PacienteEmergencia(
        nombre="Carlos Diaz",
        edad=34,
        genero="Masculino",
        prioridad_administrativa=3,
        motivo_consulta="Dolor abdominal agudo",
    )
    print(f"    Paciente:          {paciente.nombre}")
    print(f"    ID:                {paciente.id_paciente}")
    print(f"    Prioridad adm:     {paciente.prioridad_administrativa}/5")
    print(f"    Motivo consulta:   {paciente.motivo_consulta}")

    # --- Prueba 2: Estado inicial SIN_DATOS ---
    print(f"\n[2] Estado inicial (signos en cero): {paciente.estado}")

    # --- Prueba 3: Signos normales, prioridad media ---
    print("\n[3] Asignar signos NORMALES con prioridad administrativa media (3):")
    paciente.signos_vitales = SignosVitales(
        frecuencia_cardiaca=80.0,
        frecuencia_respiratoria=17.0,
        saturacion_oxigeno=97.0,
        presion_sistolica=118.0,
        presion_diastolica=74.0,
        temperatura=36.9,
    )
    print(f"    Estado calculado:  {paciente.estado}")
    print(f"    Minutos de espera: {paciente.minutos_espera:.1f}")
    print(f"    (signos normales + prioridad media = ESTABLE)")

    # --- Prueba 4: Prioridad administrativa 5 (máxima) ---
    #   La prioridad 5 eleva el estado al menos a PRUDENTE aunque los signos sean normales
    print("\n[4] Cambiar prioridad administrativa a 5 (máxima):")
    paciente.prioridad_administrativa = 5
    print(f"    Nuevo estado:      {paciente.estado}")
    print(f"    (prioridad 5 eleva ESTABLE -> PRUDENTE por protocolo)")

    # --- Prueba 5: Signos alterados + prioridad alta ---
    print("\n[5] Signos en rango BASICO + prioridad 4:")
    paciente2 = PacienteEmergencia(
        nombre="Elena Vargas",
        edad=71,
        genero="Femenino",
        prioridad_administrativa=4,
        motivo_consulta="Dificultad respiratoria",
        tipo_avatar="anciana",
    )
    paciente2.signos_vitales = SignosVitales(
        frecuencia_cardiaca=55.0,     # BASICO: leve bradicardia
        frecuencia_respiratoria=22.0, # BASICO: leve taquipnea
        saturacion_oxigeno=93.0,      # BASICO: hipoxemia leve
        presion_sistolica=85.0,       # BASICO: hipotensión leve
        presion_diastolica=55.0,      # BASICO
        temperatura=37.5,             # BASICO: febrícula
    )
    estado_base = paciente2._signos_vitales.obtener_estado_global()
    print(f"    Estado base (signos):     {estado_base}")
    print(f"    Estado final (con prioridad 4): {paciente2.estado}")
    print(f"    (BASICO + prioridad 4 = PRUDENTE)")

    # --- Prueba 6: Paciente crítico por signos ---
    print("\n[6] Paciente con signos CRITICOS:")
    paciente3 = PacienteEmergencia(
        nombre="Roberto Silva",
        edad=58,
        genero="Masculino",
        prioridad_administrativa=5,
        motivo_consulta="Dolor torácico + disnea",
    )
    paciente3.signos_vitales = SignosVitales(
        frecuencia_cardiaca=145.0,
        frecuencia_respiratoria=32.0,
        saturacion_oxigeno=81.0,
        presion_sistolica=68.0,
        presion_diastolica=38.0,
        temperatura=39.8,
    )
    print(f"    Estado base (signos): {paciente3._signos_vitales.obtener_estado_global()}")
    print(f"    Estado final:         {paciente3.estado}")
    print(f"    (CRITICO se mantiene CRITICO, no puede empeorar)")

    # --- Prueba 7: Validación de prioridad fuera de rango ---
    print("\n[7] Intento de asignar prioridad 7 (debe lanzar ValueError):")
    try:
        paciente.prioridad_administrativa = 7
        print("    ERROR: No se lanzó la excepción.")
    except ValueError as e:
        print(f"    ValueError capturado: {e}")

    # --- Prueba 8: Cambiar motivo de consulta ---
    print("\n[8] Actualizar motivo de consulta:")
    paciente.motivo_consulta = "Apendicitis sospechada"
    print(f"    Nuevo motivo: {paciente.motivo_consulta}")

    # --- Prueba 9: Resumen extendido ---
    print("\n[9] Resumen del paciente de emergencias (diccionario):")
    resumen = paciente.resumen()
    for clave, valor in resumen.items():
        if clave == "signos":
            print(f"    {clave}: (dict con {len(valor)} signos)")
        else:
            print(f"    {clave}: {valor}")

    # --- Prueba 10: Tiempo de espera legible ---
    print(f"\n[10] Tiempo de espera legible: {paciente.tiempo_espera_legible()}")

    # --- Prueba 11: __str__ y __repr__ ---
    print(f"\n[11] Representaciones:\n{paciente}")
    print(f"    repr: {repr(paciente2)}")

    print("\n[OK] Pruebas de PacienteEmergencia completadas.\n")
