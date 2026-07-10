"""
Módulo: historial.py
Sprint 1 — Historial médico del paciente.

Define las clases Examen e HistorialMedico, que almacenan y gestionan
el registro clínico de cada paciente: exámenes realizados, diagnósticos
y tratamientos.

Dependencias previas necesarias:
    - config.py  (constantes globales)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime


class Examen:
    """
    Representa un examen o prueba médica realizada a un paciente.

    Atributos:
        - tipo:      Tipo de examen (Hemograma, Radiografía, EKG, etc.).
        - fecha:     Fecha y hora en que se realizó el examen.
        - resultado: Descripción del resultado obtenido.
        - notas:     Observaciones adicionales del profesional que lo interpretó.
    """

    def __init__(
        self,
        tipo:      str,
        resultado: str = "Pendiente",
        notas:     str = "",
        fecha:     datetime = None,
    ):
        """
        Constructor de Examen.

        Args:
            tipo:      Tipo de examen (ej. "Hemograma completo").
            resultado: Resultado del examen. Por defecto "Pendiente".
            notas:     Notas u observaciones adicionales.
            fecha:     Fecha del examen. Si no se da, se usa la fecha actual.
        """
        self._tipo      = tipo
        self._resultado = resultado
        self._notas     = notas
        self._fecha     = fecha if fecha is not None else datetime.now()

    # ==================================================================
    # PROPIEDADES
    # ==================================================================

    @property
    def tipo(self) -> str:
        """Tipo de examen realizado."""
        return self._tipo

    @property
    def resultado(self) -> str:
        """Resultado del examen."""
        return self._resultado

    @resultado.setter
    def resultado(self, valor: str) -> None:
        """Actualiza el resultado del examen."""
        self._resultado = valor

    @property
    def notas(self) -> str:
        """Notas u observaciones del profesional."""
        return self._notas

    @notas.setter
    def notas(self, valor: str) -> None:
        """Agrega o actualiza las notas del examen."""
        self._notas = valor

    @property
    def fecha(self) -> datetime:
        """Fecha y hora en que se realizó el examen."""
        return self._fecha

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================

    def __str__(self) -> str:
        """Representación legible del examen."""
        fecha_str = self._fecha.strftime("%Y-%m-%d %H:%M")
        return (
            f"Examen: {self._tipo}\n"
            f"  Fecha:     {fecha_str}\n"
            f"  Resultado: {self._resultado}\n"
            f"  Notas:     {self._notas if self._notas else '(sin notas)'}"
        )

    def __repr__(self) -> str:
        """Representación técnica."""
        return (
            f"Examen(tipo={self._tipo!r}, "
            f"resultado={self._resultado!r}, "
            f"fecha={self._fecha.strftime('%Y-%m-%d')!r})"
        )


class HistorialMedico:
    """
    Almacena y gestiona el historial clínico completo de un paciente.

    Contiene:
        - Lista de exámenes realizados (instancias de Examen).
        - Lista de diagnósticos emitidos por los médicos.
        - Lista de tratamientos prescritos.

    Proporciona métodos para agregar nuevos registros y consultar
    el historial de forma ordenada (por fecha).
    """

    def __init__(self, id_paciente: str = ""):
        """
        Constructor de HistorialMedico.

        Args:
            id_paciente: Identificador del paciente al que pertenece el historial.
        """
        self._id_paciente  = id_paciente

        # Listas internas que almacenan los registros clínicos
        self._examenes:     list[Examen] = []
        self._diagnosticos: list[dict]   = []
        self._tratamientos: list[dict]   = []
        self._medicamentos: list[dict]   = []

    # ==================================================================
    # PROPIEDADES
    # ==================================================================

    @property
    def id_paciente(self) -> str:
        """ID del paciente dueño del historial."""
        return self._id_paciente

    @id_paciente.setter
    def id_paciente(self, valor: str) -> None:
        """Vincula el historial a un paciente por su ID."""
        self._id_paciente = valor

    @property
    def examenes(self) -> list:
        """
        Devuelve una copia de la lista de exámenes para evitar
        modificaciones externas no controladas.
        """
        return list(self._examenes)

    @property
    def diagnosticos(self) -> list:
        """Devuelve una copia de la lista de diagnósticos."""
        return list(self._diagnosticos)

    @property
    def tratamientos(self) -> list:
        """Devuelve una copia de la lista de tratamientos."""
        return list(self._tratamientos)

    @property
    def medicamentos(self) -> list:
        """Devuelve una copia de la lista de medicamentos administrados."""
        return list(self._medicamentos)

    # ==================================================================
    # MÉTODOS PARA AGREGAR REGISTROS
    # ==================================================================

    def agregar_examen(self, examen: Examen) -> None:
        """
        Agrega un examen al historial del paciente.

        Args:
            examen: Instancia de Examen a registrar.
        """
        if not isinstance(examen, Examen):
            raise TypeError("El argumento debe ser una instancia de Examen.")
        self._examenes.append(examen)

    def agregar_diagnostico(
        self,
        descripcion: str,
        autor:       str = "",
        fecha:       datetime = None,
    ) -> None:
        """
        Registra un nuevo diagnóstico en el historial.

        Args:
            descripcion: Descripción del diagnóstico.
            autor:       Nombre del médico que lo emitió.
            fecha:       Fecha del diagnóstico. Si no se da, se usa ahora.
        """
        self._diagnosticos.append({
            "descripcion": descripcion,
            "autor":       autor,
            "fecha":       fecha if fecha is not None else datetime.now(),
        })

    def agregar_tratamiento(
        self,
        descripcion: str,
        autor:       str = "",
        fecha:       datetime = None,
    ) -> None:
        """
        Registra un nuevo tratamiento en el historial.

        Args:
            descripcion: Descripción del tratamiento prescrito.
            autor:       Nombre del médico que lo prescribió.
            fecha:       Fecha de prescripción. Si no se da, se usa ahora.
        """
        self._tratamientos.append({
            "descripcion": descripcion,
            "autor":       autor,
            "fecha":       fecha if fecha is not None else datetime.now(),
        })

    def agregar_medicamento(
        self,
        descripcion: str,
        autor:       str = "",
        fecha:       datetime = None,
    ) -> None:
        """
        Registra un medicamento administrado en el historial.

        Args:
            descripcion: Nombre y dosis del medicamento.
            autor:       Nombre del médico que lo prescribió.
            fecha:       Fecha de administración. Si no se da, se usa ahora.
        """
        self._medicamentos.append({
            "descripcion": descripcion,
            "autor":       autor,
            "fecha":       fecha if fecha is not None else datetime.now(),
        })

    # ==================================================================
    # MÉTODOS DE CONSULTA
    # ==================================================================

    def ultimo_diagnostico(self) -> dict | None:
        """
        Retorna el diagnóstico más reciente, o None si no hay ninguno.
        """
        if not self._diagnosticos:
            return None
        return max(self._diagnosticos, key=lambda d: d["fecha"])

    def ultimo_tratamiento(self) -> dict | None:
        """
        Retorna el tratamiento más reciente, o None si no hay ninguno.
        """
        if not self._tratamientos:
            return None
        return max(self._tratamientos, key=lambda t: t["fecha"])

    def examenes_por_tipo(self, tipo: str) -> list[Examen]:
        """
        Filtra los exámenes por tipo (ej. "Hemograma").

        Args:
            tipo: Tipo de examen a buscar (coincidencia parcial, case-insensitive).

        Returns:
            Lista de exámenes que coinciden con el tipo.
        """
        tipo_lower = tipo.lower()
        return [e for e in self._examenes if tipo_lower in e.tipo.lower()]

    def total_examenes(self) -> int:
        """Cantidad total de exámenes registrados."""
        return len(self._examenes)

    def total_diagnosticos(self) -> int:
        """Cantidad total de diagnósticos registrados."""
        return len(self._diagnosticos)

    def total_tratamientos(self) -> int:
        """Cantidad total de tratamientos registrados."""
        return len(self._tratamientos)

    def total_medicamentos(self) -> int:
        """Cantidad total de medicamentos registrados."""
        return len(self._medicamentos)

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================

    def __str__(self) -> str:
        """
        Representación legible del historial médico completo.
        Muestra exámenes, diagnósticos y tratamientos ordenados por fecha.
        """
        lineas = [f"HISTORIAL MÉDICO — Paciente: {self._id_paciente}"]

        # Exámenes
        lineas.append(f"\n  Exámenes ({self.total_examenes()}):")
        if self._examenes:
            for ex in sorted(self._examenes, key=lambda e: e.fecha):
                fecha_str = ex.fecha.strftime("%d/%m/%Y %H:%M")
                lineas.append(
                    f"    [{fecha_str}] {ex.tipo}: {ex.resultado}"
                )
        else:
            lineas.append("    (sin exámenes registrados)")

        # Diagnósticos
        lineas.append(f"\n  Diagnósticos ({self.total_diagnosticos()}):")
        if self._diagnosticos:
            for d in sorted(self._diagnosticos, key=lambda x: x["fecha"]):
                fecha_str = d["fecha"].strftime("%d/%m/%Y %H:%M")
                autor_str = f" por {d['autor']}" if d["autor"] else ""
                lineas.append(
                    f"    [{fecha_str}]{autor_str}: {d['descripcion']}"
                )
        else:
            lineas.append("    (sin diagnósticos registrados)")

        # Tratamientos
        lineas.append(f"\n  Tratamientos ({self.total_tratamientos()}):")
        if self._tratamientos:
            for t in sorted(self._tratamientos, key=lambda x: x["fecha"]):
                fecha_str = t["fecha"].strftime("%d/%m/%Y %H:%M")
                autor_str = f" por {t['autor']}" if t["autor"] else ""
                lineas.append(
                    f"    [{fecha_str}]{autor_str}: {t['descripcion']}"
                )
        else:
            lineas.append("    (sin tratamientos registrados)")

        # Medicamentos
        lineas.append(f"\n  Medicamentos ({self.total_medicamentos()}):")
        if self._medicamentos:
            for m in sorted(self._medicamentos, key=lambda x: x["fecha"]):
                fecha_str = m["fecha"].strftime("%d/%m/%Y %H:%M")
                autor_str = f" por {m['autor']}" if m["autor"] else ""
                lineas.append(
                    f"    [{fecha_str}]{autor_str}: {m['descripcion']}"
                )
        else:
            lineas.append("    (sin medicamentos registrados)")

        return "\n".join(lineas)

    def __repr__(self) -> str:
        """Representación técnica para depuración."""
        return (
            f"HistorialMedico(id_paciente={self._id_paciente!r}, "
            f"examenes={self.total_examenes()}, "
            f"diagnosticos={self.total_diagnosticos()}, "
            f"tratamientos={self.total_tratamientos()}, "
            f"medicamentos={self.total_medicamentos()})"
        )

    def __len__(self) -> int:
        """
        Cantidad total de registros en el historial
        (exámenes + diagnósticos + tratamientos + medicamentos).
        """
        return (
            self.total_examenes()
            + self.total_diagnosticos()
            + self.total_tratamientos()
            + self.total_medicamentos()
        )


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo de historial médico.
    Demuestra:
      1. Creación de Examen con atributos básicos.
      2. Modificación de resultado y notas de un examen.
      3. Creación de HistorialMedico vinculado a un paciente.
      4. Agregar exámenes de distintos tipos.
      5. Agregar diagnósticos con autor y fecha.
      6. Agregar tratamientos prescritos.
      7. Consulta de último diagnóstico y último tratamiento.
      8. Filtrado de exámenes por tipo.
      9. Representación completa con __str__.
     10. Conteo total con __len__.
    """
    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: HistorialMedico y Examen")
    print("=" * 60)

    # --- Prueba 1: Crear un examen ---
    print("\n[1] Crear Examen:")
    examen1 = Examen(
        tipo="Hemograma completo",
        resultado="Normal",
        notas="Leucocitos dentro de parámetros normales.",
    )
    print(f"    {examen1}")

    # --- Prueba 2: Modificar resultado de un examen ---
    print("\n[2] Modificar resultado del examen:")
    examen1.resultado = "Leve leucocitosis"
    print(f"    Nuevo resultado: {examen1.resultado}")

    # --- Prueba 3: Crear historial médico ---
    print("\n[3] Crear HistorialMedico para PAC-0001:")
    historial = HistorialMedico(id_paciente="PAC-0001")
    print(f"    {repr(historial)}")

    # --- Prueba 4: Agregar exámenes ---
    print("\n[4] Agregar exámenes al historial:")
    historial.agregar_examen(examen1)
    historial.agregar_examen(Examen(
        tipo="Radiografía de tórax",
        resultado="Sin hallazgos patológicos",
        notas="Campos pulmonares limpios.",
    ))
    historial.agregar_examen(Examen(
        tipo="Electrocardiograma",
        resultado="Ritmo sinusal normal",
        notas="FC 72 bpm, sin arritmias.",
    ))
    historial.agregar_examen(Examen(
        tipo="Hemograma de control",
        resultado="Normal",
        notas="Leucocitos normalizados tras tratamiento.",
    ))
    print(f"    Total exámenes: {historial.total_examenes()}")

    # --- Prueba 5: Agregar diagnósticos ---
    print("\n[5] Agregar diagnósticos:")
    historial.agregar_diagnostico(
        descripcion="Infección respiratoria alta",
        autor="Dr. Ricardo Fernandez",
    )
    historial.agregar_diagnostico(
        descripcion="Hipertensión arterial controlada",
        autor="Dra. Marta Silva",
    )
    print(f"    Total diagnósticos: {historial.total_diagnosticos()}")

    # --- Prueba 6: Agregar tratamientos ---
    print("\n[6] Agregar tratamientos:")
    historial.agregar_tratamiento(
        descripcion="Amoxicilina 500mg cada 8h por 7 días",
        autor="Dr. Ricardo Fernandez",
    )
    historial.agregar_tratamiento(
        descripcion="Enalapril 10mg cada 24h. Control en 30 días.",
        autor="Dra. Marta Silva",
    )
    print(f"    Total tratamientos: {historial.total_tratamientos()}")

    # --- Prueba 7: Último diagnóstico y tratamiento ---
    print("\n[7] Consultar último diagnóstico y tratamiento:")
    ult_diag = historial.ultimo_diagnostico()
    ult_trat = historial.ultimo_tratamiento()
    print(f"    Último diagnóstico: {ult_diag['descripcion']} (por {ult_diag['autor']})")
    print(f"    Último tratamiento: {ult_trat['descripcion']} (por {ult_trat['autor']})")

    # --- Prueba 8: Filtrar exámenes por tipo ---
    print("\n[8] Filtrar exámenes que contengan 'Hemograma':")
    examenes_hemo = historial.examenes_por_tipo("Hemograma")
    for ex in examenes_hemo:
        print(f"    - {ex.tipo}: {ex.resultado}")

    # --- Prueba 9: Representación completa ---
    print(f"\n[9] Representación completa del historial:\n{historial}")

    # --- Prueba 10: __len__ ---
    print(f"\n[10] Total de registros en el historial: {len(historial)}")
    print(f"     ({historial.total_examenes()} exámenes + "
          f"{historial.total_diagnosticos()} diagnósticos + "
          f"{historial.total_tratamientos()} tratamientos)")

    # --- Prueba 11: Validación de tipo en agregar_examen ---
    print("\n[11] Intento de agregar algo que no es un Examen (debe lanzar TypeError):")
    try:
        historial.agregar_examen("esto no es un examen")
        print("    ERROR: No se lanzó la excepción.")
    except TypeError as e:
        print(f"    TypeError capturado: {e}")

    # --- Prueba 12: Historial vacío ---
    print("\n[12] Historial nuevo sin registros:")
    historial_vacio = HistorialMedico(id_paciente="PAC-0099")
    print(f"    Último diagnóstico: {historial_vacio.ultimo_diagnostico()}")
    print(f"    Último tratamiento: {historial_vacio.ultimo_tratamiento()}")
    print(f"    Total registros:    {len(historial_vacio)}")

    print("\n[OK] Pruebas de HistorialMedico y Examen completadas.\n")
