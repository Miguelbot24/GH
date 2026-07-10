"""
Módulo: personal.py
Sprint 1 — Personal del hospital.

Define las clases PersonalHospital (abstracta), Doctor y Enfermero,
que representan al personal sanitario del sistema. Demuestra los pilares
de Abstracción y Herencia de la POO.

Dependencias previas necesarias:
    - config.py            (constantes globales)
    - modelos/paciente.py  (clase Paciente para interactuar)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abc import ABC, abstractmethod
from datetime import datetime


class PersonalHospital(ABC):
    """
    Clase abstracta base para todo el personal del hospital.

    Principio OOP — Abstracción:
        Declara la interfaz común que deben implementar todos los tipos
        de personal sanitario (médicos, enfermeros, etc.).

    Principio OOP — Herencia:
        Doctor y Enfermero heredan de esta clase, reutilizando atributos
        comunes (id, nombre, turno) y especializando el método abstracto
        atender_paciente().
    """

    # Contador de clase para IDs únicos
    _contador_empleados = 0

    def __init__(
        self,
        nombre: str,
        cargo:  str,
        turno:  str = "Diurno",
        id_empleado: str = None,
    ):
        """
        Constructor de la clase base PersonalHospital.

        Args:
            nombre:      Nombre completo del profesional.
            cargo:       Cargo o puesto (ej. "Cardiólogo", "Enfermero UCI").
            turno:       Turno asignado ("Diurno", "Nocturno", "Mixto").
            id_empleado: ID único. Si no se da, se autogenera (EMP-0001...).
        """
        if id_empleado is None:
            PersonalHospital._contador_empleados += 1
            id_empleado = f"EMP-{PersonalHospital._contador_empleados:04d}"

        self._id_empleado = id_empleado
        self._nombre      = nombre
        self._cargo       = cargo
        self._turno       = turno
        self._disponible  = True  # True = libre para atender, False = ocupado

    # ==================================================================
    # PROPIEDADES COMUNES
    # ==================================================================

    @property
    def id_empleado(self) -> str:
        """Identificador único del empleado (ej. 'EMP-0001')."""
        return self._id_empleado

    @property
    def nombre(self) -> str:
        """Nombre completo del profesional."""
        return self._nombre

    @property
    def cargo(self) -> str:
        """Cargo o puesto que ocupa."""
        return self._cargo

    @property
    def turno(self) -> str:
        """Turno asignado (Diurno, Nocturno, Mixto)."""
        return self._turno

    @turno.setter
    def turno(self, valor: str) -> None:
        """Cambia el turno del profesional."""
        self._turno = valor

    @property
    def disponible(self) -> bool:
        """
        Indica si el profesional está libre para atender un paciente.
        True = disponible, False = ocupado atendiendo a alguien.
        """
        return self._disponible

    def marcar_ocupado(self) -> None:
        """Marca al profesional como ocupado (atendiendo un paciente)."""
        self._disponible = False

    def marcar_disponible(self) -> None:
        """Marca al profesional como libre para atender."""
        self._disponible = True

    # ==================================================================
    # MÉTODO ABSTRACTO
    # ==================================================================

    @abstractmethod
    def atender_paciente(self, paciente) -> str:
        """
        Realiza la atención médica al paciente.

        Principio OOP — Polimorfismo:
            Doctor y Enfermero implementan este método de forma diferente:
            - Doctor: evalúa, diagnostica, prescribe tratamiento.
            - Enfermero: toma signos vitales, administra medicación, monitorea.

        Args:
            paciente: Instancia de Paciente (o subclase) a atender.

        Returns:
            Resumen en texto de la atención realizada.
        """
        pass

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================

    def __str__(self) -> str:
        """Representación legible del profesional."""
        estado = "Disponible" if self._disponible else "Ocupado"
        return (
            f"{self._cargo}: {self._nombre}\n"
            f"  ID:     {self._id_empleado}\n"
            f"  Turno:  {self._turno}\n"
            f"  Estado: {estado}"
        )

    def __repr__(self) -> str:
        """Representación técnica para depuración."""
        return (
            f"{self.__class__.__name__}("
            f"id={self._id_empleado!r}, "
            f"nombre={self._nombre!r}, "
            f"cargo={self._cargo!r})"
        )


class Doctor(PersonalHospital):
    """
    Representa a un médico del hospital.

    Hereda de PersonalHospital y especializa el método atender_paciente()
    con lógica de evaluación y diagnóstico.

    Atributos adicionales:
        - especialidad: rama médica (Cardiología, Neurología, etc.).
        - numero_colegiatura: número de registro profesional.
    """

    def __init__(
        self,
        nombre:            str,
        especialidad:      str = "Medicina General",
        numero_colegiatura: str = "",
        turno:             str = "Diurno",
        id_empleado:       str = None,
    ):
        """
        Constructor de Doctor.

        Args:
            nombre:             Nombre completo del médico.
            especialidad:       Especialidad médica (ej. "Cardiología").
            numero_colegiatura: Número de colegiatura / registro profesional.
            turno:              Turno asignado.
            id_empleado:        ID único opcional.
        """
        cargo = f"Dr(a). {especialidad}"
        super().__init__(
            nombre=nombre,
            cargo=cargo,
            turno=turno,
            id_empleado=id_empleado,
        )

        self._especialidad       = especialidad
        self._numero_colegiatura = numero_colegiatura

    # ==================================================================
    # PROPIEDADES ESPECÍFICAS DE DOCTOR
    # ==================================================================

    @property
    def especialidad(self) -> str:
        """Especialidad médica del doctor."""
        return self._especialidad

    @property
    def numero_colegiatura(self) -> str:
        """Número de registro profesional."""
        return self._numero_colegiatura

    # ==================================================================
    # IMPLEMENTACIÓN POLIMÓRFICA DE atender_paciente()
    # ==================================================================

    def atender_paciente(self, paciente) -> str:
        """
        El doctor evalúa al paciente, revisa sus signos vitales,
        determina el estado clínico y emite un diagnóstico preliminar.

        Args:
            paciente: Instancia de Paciente a evaluar.

        Returns:
            Resumen de la atención médica realizada.
        """
        if not self._disponible:
            return f"Dr(a). {self._nombre} ya está atendiendo a otro paciente."

        self.marcar_ocupado()

        # El doctor fuerza el recálculo del estado del paciente
        estado = paciente.actualizar_estado()

        # Generar un diagnóstico preliminar basado en el estado
        diagnosticos = {
            "CRITICO":   "Requiere intervención inmediata. Posible fallo multiorgánico.",
            "PRUDENTE":  "Requiere atención prioritaria. Evaluar causa subyacente.",
            "BASICO":    "Signos levemente alterados. Observación y pruebas complementarias.",
            "ESTABLE":   "Signos dentro de parámetros normales. Alta probable.",
            "FALLECIDO": "Sin signos vitales. Confirmar deceso.",
            "SIN_DATOS": "No hay datos de monitor. Conectar monitor y reevaluar.",
        }
        diagnostico = diagnosticos.get(estado, "Evaluación pendiente.")

        resumen = (
            f"ATENCIÓN MÉDICA — Dr(a). {self._nombre} ({self._especialidad})\n"
            f"  Paciente:   {paciente.nombre} ({paciente.id_paciente})\n"
            f"  Estado:     {estado}\n"
            f"  Diagnóstico preliminar: {diagnostico}"
        )

        self.marcar_disponible()
        return resumen


class Enfermero(PersonalHospital):
    """
    Representa a un enfermero/a del hospital.

    Hereda de PersonalHospital y especializa el método atender_paciente()
    con lógica de cuidados, monitoreo y administración de medicación.
    """

    def __init__(
        self,
        nombre:       str,
        sector:       str = "General",
        turno:        str = "Diurno",
        id_empleado:  str = None,
    ):
        """
        Constructor de Enfermero.

        Args:
            nombre:      Nombre completo del enfermero/a.
            sector:      Sector o planta asignada (ej. "UCI", "General").
            turno:       Turno asignado.
            id_empleado: ID único opcional.
        """
        cargo = f"Enf. {sector}"
        super().__init__(
            nombre=nombre,
            cargo=cargo,
            turno=turno,
            id_empleado=id_empleado,
        )

        self._sector = sector

    # ==================================================================
    # PROPIEDADES ESPECÍFICAS DE ENFERMERO
    # ==================================================================

    @property
    def sector(self) -> str:
        """Sector o planta donde trabaja el enfermero."""
        return self._sector

    @sector.setter
    def sector(self, valor: str) -> None:
        """Reasigna al enfermero a otro sector."""
        self._sector = valor
        self._cargo  = f"Enf. {valor}"

    # ==================================================================
    # IMPLEMENTACIÓN POLIMÓRFICA DE atender_paciente()
    # ==================================================================

    def atender_paciente(self, paciente) -> str:
        """
        El enfermero monitorea al paciente: registra signos vitales,
        administra cuidados y reporta novedades.

        Args:
            paciente: Instancia de Paciente a atender.

        Returns:
            Resumen de la atención de enfermería realizada.
        """
        if not self._disponible:
            return f"Enf. {self._nombre} ya está atendiendo a otro paciente."

        self.marcar_ocupado()

        # El enfermero toma los signos vitales actuales del paciente
        signos = paciente.signos_vitales

        # Verifica si hay signos fuera de rango para reportar
        alertas_signos = []
        for nombre_signo in [
            "frecuencia_cardiaca",
            "frecuencia_respiratoria",
            "saturacion_oxigeno",
            "presion_sistolica",
            "presion_diastolica",
            "temperatura",
        ]:
            if not signos.esta_en_rango_normal(nombre_signo):
                alertas_signos.append(nombre_signo)

        if alertas_signos:
            alerta_str = f"Signos alterados: {len(alertas_signos)} parámetro(s) fuera de rango."
        else:
            alerta_str = "Todos los signos dentro de rangos normales."

        resumen = (
            f"ATENCIÓN ENFERMERÍA — Enf. {self._nombre} ({self._sector})\n"
            f"  Paciente:   {paciente.nombre} ({paciente.id_paciente})\n"
            f"  Estado:     {paciente.estado}\n"
            f"  Presión:    {signos.obtener_presion_arterial()}\n"
            f"  Reporte:    {alerta_str}"
        )

        self.marcar_disponible()
        return resumen


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo de personal.
    Demuestra:
      1. Creación de Doctor y Enfermero.
      2. Herencia de atributos comunes (id, nombre, turno, disponible).
      3. Polimorfismo: atender_paciente() tiene comportamientos distintos.
      4. Disponibilidad del personal (ocupado / libre).
      5. Cambio de turno y sector.
      6. IDs automáticos.
      7. Manejo de intento de atender estando ocupado.
    """
    from modelos.paciente_sala import PacienteSala
    from modelos.signos_vitales import SignosVitales

    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: Personal (Doctor y Enfermero)")
    print("=" * 60)

    # --- Prueba 1: Crear Doctor ---
    print("\n[1] Crear Doctor:")
    doctor = Doctor(
        nombre="Ricardo Fernandez",
        especialidad="Cardiología",
        numero_colegiatura="COL-7845",
        turno="Diurno",
    )
    print(f"    {doctor}")

    # --- Prueba 2: Crear Enfermero ---
    print("\n[2] Crear Enfermero:")
    enfermero = Enfermero(
        nombre="Laura Castillo",
        sector="UCI",
        turno="Nocturno",
    )
    print(f"    {enfermero}")

    # --- Prueba 3: Propiedades específicas ---
    print("\n[3] Propiedades específicas:")
    print(f"    Doctor - Especialidad:    {doctor.especialidad}")
    print(f"    Doctor - Colegiatura:     {doctor.numero_colegiatura}")
    print(f"    Enfermero - Sector:       {enfermero.sector}")

    # --- Prueba 4: Crear paciente de prueba para atender ---
    print("\n[4] Crear paciente para pruebas de atención:")
    paciente = PacienteSala(
        nombre="Julia Mendoza",
        edad=42,
        genero="Femenino",
        numero_cama=205,
        tipo_avatar="mujer",
    )
    paciente.signos_vitales = SignosVitales(
        frecuencia_cardiaca=58.0,
        frecuencia_respiratoria=22.0,
        saturacion_oxigeno=93.0,
        presion_sistolica=85.0,
        presion_diastolica=56.0,
        temperatura=37.8,
    )
    print(f"    Paciente: {paciente.nombre} — Estado: {paciente.estado}")

    # --- Prueba 5: Doctor atiende al paciente (POLIMORFISMO) ---
    print("\n[5] Doctor atiende al paciente:")
    resultado_doc = doctor.atender_paciente(paciente)
    print(f"    {resultado_doc}")

    # --- Prueba 6: Enfermero atiende al paciente (POLIMORFISMO) ---
    print("\n[6] Enfermero atiende al paciente:")
    resultado_enf = enfermero.atender_paciente(paciente)
    print(f"    {resultado_enf}")

    # --- Prueba 7: Intentar atender estando ocupado ---
    print("\n[7] Simular atención estando ocupado:")
    # Forzamos estado ocupado manualmente
    doctor.marcar_ocupado()
    resultado_ocupado = doctor.atender_paciente(paciente)
    print(f"    {resultado_ocupado}")
    doctor.marcar_disponible()  # Restaurar

    # --- Prueba 8: Cambio de turno ---
    print("\n[8] Cambiar turno del doctor:")
    print(f"    Turno anterior: {doctor.turno}")
    doctor.turno = "Mixto"
    print(f"    Nuevo turno:    {doctor.turno}")

    # --- Prueba 9: Cambio de sector del enfermero ---
    print("\n[9] Reasignar enfermero a otro sector:")
    print(f"    Sector anterior: {enfermero.sector}")
    enfermero.sector = "Cardiología"
    print(f"    Nuevo sector:   {enfermero.sector}")
    print(f"    Nuevo cargo:    {enfermero.cargo}")

    # --- Prueba 10: Paciente con signos normales ---
    print("\n[10] Atender paciente con signos NORMALES:")
    paciente_normal = PacienteSala(
        nombre="Diego Rojas",
        edad=28,
        genero="Masculino",
        numero_cama=210,
    )
    paciente_normal.signos_vitales = SignosVitales(
        frecuencia_cardiaca=72.0,
        frecuencia_respiratoria=16.0,
        saturacion_oxigeno=98.0,
        presion_sistolica=118.0,
        presion_diastolica=74.0,
        temperatura=36.5,
    )
    print(f"    {enfermero.atender_paciente(paciente_normal)}")

    # --- Prueba 11: IDs automáticos ---
    print("\n[11] Segundo doctor (ID automático):")
    doctor2 = Doctor(nombre="Marta Silva", especialidad="Neurología")
    print(f"    ID Doctor 1: {doctor.id_empleado}")
    print(f"    ID Doctor 2: {doctor2.id_empleado}")

    # --- Prueba 12: __repr__ ---
    print(f"\n[12] Representaciones técnicas:")
    print(f"    {repr(doctor)}")
    print(f"    {repr(enfermero)}")

    print("\n[OK] Pruebas de Personal completadas.\n")
