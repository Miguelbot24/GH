"""
Módulo: repositorio.py
Sprint 2 — Repositorio de pacientes en memoria.

Define la clase RepositorioPacientes, que actúa como almacén central de todos
los pacientes del sistema. Proporciona métodos para agregar, eliminar, buscar
y filtrar pacientes sin necesidad de una base de datos externa.

Dependencias previas necesarias:
    - config.py              (constantes de estados)
    - modelos/paciente.py    (Paciente ABC)
    - modelos/paciente_sala.py
    - modelos/paciente_emergencia.py
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ESTADOS_SALA, ESTADOS_EMERGENCIA, ESTADO_SIN_DATOS, ESTADO_FALLECIDO, TIPO_EGRESO_ALTA, TIPO_EGRESO_FUGA

# Combinación de todos los estados existentes para validaciones genéricas
_TODOS_LOS_ESTADOS = ESTADOS_SALA + ESTADOS_EMERGENCIA + (ESTADO_FALLECIDO,)

from modelos.paciente import Paciente


class PacienteNoEncontradoError(Exception):
    """
    Excepción lanzada cuando se busca un paciente por ID y no existe
    en el repositorio.
    """
    def __init__(self, id_paciente: str):
        super().__init__(
            f"No se encontró ningún paciente con el ID '{id_paciente}'."
        )
        self.id_paciente = id_paciente


class RepositorioPacientes:
    """
    Almacén central de pacientes del sistema hospitalario.

    Mantiene todos los pacientes en memoria durante la sesión y expone
    métodos de consulta y modificación. Sustituye a una base de datos
    real simplificando la arquitectura para el entorno académico.

    Principio OOP — Encapsulamiento:
        Los datos están protegidos (listas internas _pacientes_sala y
        _pacientes_emergencia). Toda modificación pasa por métodos
        públicos que garantizan la integridad de los datos.
    """

    def __init__(self):
        """
        Constructor del repositorio.
        Inicializa las listas internas vacías.
        """
        # Almacenamiento en memoria: dos listas independientes para cada tipo
        self._pacientes_sala:       list = []
        self._pacientes_emergencia: list = []
        self._pacientes_egresos:    list = []

    # ==================================================================
    # MÉTODOS DE AGREGADO
    # ==================================================================

    def agregar_paciente(self, paciente: Paciente) -> None:
        """
        Agrega un paciente al repositorio.

        Detecta automáticamente si es un paciente de sala o de emergencias
        según su tipo (usando el nombre de la clase o un atributo 'tipo').

        Args:
            paciente: Instancia de PacienteSala o PacienteEmergencia.

        Raises:
            TypeError: Si el argumento no es una subclase de Paciente.
        """
        if not isinstance(paciente, Paciente):
            raise TypeError(
                "El argumento debe ser una instancia de Paciente "
                "(PacienteSala o PacienteEmergencia)."
            )

        # Verificamos si ya existe un paciente con el mismo ID
        if self._existe_id(paciente.id_paciente):
            raise ValueError(
                f"Ya existe un paciente con el ID '{paciente.id_paciente}' "
                f"en el repositorio."
            )

        # Clasificamos según el tipo de paciente
        tipo = paciente.__class__.__name__
        if tipo == "PacienteSala":
            self._pacientes_sala.append(paciente)
        elif tipo == "PacienteEmergencia":
            self._pacientes_emergencia.append(paciente)
        else:
            # Por seguridad, lo asignamos a sala como fallback
            self._pacientes_sala.append(paciente)

    def agregar_pacientes(self, pacientes: list) -> None:
        """
        Agrega múltiples pacientes al repositorio de una sola vez.

        Args:
            pacientes: Lista de instancias de PacienteSala o PacienteEmergencia.
        """
        for paciente in pacientes:
            self.agregar_paciente(paciente)

    # ==================================================================
    # MÉTODOS DE ELIMINACIÓN
    # ==================================================================

    def eliminar_paciente(self, id_paciente: str) -> Paciente:
        """
        Elimina un paciente del repositorio por su ID y lo devuelve.

        Args:
            id_paciente: ID del paciente a eliminar (ej. "PAC-0001").

        Returns:
            La instancia del paciente eliminado.

        Raises:
            PacienteNoEncontradoError: Si el ID no existe.
        """
        paciente = self._extraer_por_id(id_paciente)
        return paciente

    def limpiar(self) -> None:
        """Elimina todos los pacientes del repositorio."""
        self._pacientes_sala.clear()
        self._pacientes_emergencia.clear()
        self._pacientes_egresos.clear()

    # ==================================================================
    # MÉTODOS DE BÚSQUEDA
    # ==================================================================

    def buscar_por_id(self, id_paciente: str) -> Paciente:
        """
        Busca un paciente por su ID exacto.

        Args:
            id_paciente: ID del paciente (ej. "PAC-0001").

        Returns:
            La instancia del paciente encontrado.

        Raises:
            PacienteNoEncontradoError: Si el ID no existe.
        """
        for paciente in self._pacientes_sala + self._pacientes_emergencia:
            if paciente.id_paciente == id_paciente:
                return paciente

        raise PacienteNoEncontradoError(id_paciente)

    def buscar_por_nombre(self, texto: str) -> list[Paciente]:
        """
        Busca pacientes cuyo nombre contenga el texto dado.
        La búsqueda no distingue mayúsculas/minúsculas.

        Args:
            texto: Fragmento del nombre a buscar.

        Returns:
            Lista de pacientes que coinciden (puede estar vacía).
        """
        texto_lower = texto.lower()
        resultados = []
        for paciente in self._pacientes_sala + self._pacientes_emergencia:
            if texto_lower in paciente.nombre.lower():
                resultados.append(paciente)
        return resultados

    # ==================================================================
    # MÉTODOS DE CONSULTA POR TIPO
    # ==================================================================

    def obtener_sala(self) -> list:
        """
        Devuelve la lista completa de pacientes de sala.

        Returns:
            Copia de la lista de PacienteSala (para evitar modificación externa).
        """
        return list(self._pacientes_sala)

    def obtener_emergencia(self) -> list:
        """
        Devuelve la lista completa de pacientes de emergencias.

        Returns:
            Copia de la lista de PacienteEmergencia.
        """
        return list(self._pacientes_emergencia)

    def obtener_todos(self) -> list[Paciente]:
        """
        Devuelve todos los pacientes del repositorio (sala + emergencia).

        Returns:
            Lista combinada de todos los pacientes.
        """
        return self._pacientes_sala + self._pacientes_emergencia

    def obtener_egresos(self) -> list:
        """
        Devuelve la lista completa de pacientes egresados.

        Returns:
            Copia de la lista de pacientes con tipo_egreso distinto de None.
        """
        return list(self._pacientes_egresos)

    def total_egresos(self) -> int:
        """Cantidad de pacientes egresados."""
        return len(self._pacientes_egresos)

    def marcar_egreso(self, id_paciente: str, tipo_egreso: str) -> Paciente:
        """
        Marca un paciente como egresado y lo mueve a la lista de egresos.

        Args:
            id_paciente: ID del paciente a egresar.
            tipo_egreso:  TIPO_EGRESO_ALTA o TIPO_EGRESO_FUGA.

        Returns:
            La instancia del paciente egresado.

        Raises:
            PacienteNoEncontradoError: Si el ID no existe.
            ValueError: Si el tipo_egreso no es válido.
        """
        if tipo_egreso not in (TIPO_EGRESO_ALTA, TIPO_EGRESO_FUGA):
            raise ValueError(
                f"Tipo de egreso no válido: '{tipo_egreso}'. "
                f"Debe ser '{TIPO_EGRESO_ALTA}' o '{TIPO_EGRESO_FUGA}'."
            )

        paciente = self._extraer_por_id(id_paciente)
        paciente.marcar_egreso(tipo_egreso)
        self._pacientes_egresos.append(paciente)
        return paciente

    # ==================================================================
    # MÉTODOS DE FILTRADO POR ESTADO
    # ==================================================================

    def filtrar_por_estado(self, estado: str) -> list[Paciente]:
        """
        Filtra pacientes por su estado clínico actual.

        Args:
            estado: Una de las constantes ESTADO_* de config.py.

        Returns:
            Lista de pacientes que coinciden con el estado.
        """
        if estado not in _TODOS_LOS_ESTADOS:
            raise ValueError(
                f"Estado '{estado}' no válido. Estados permitidos: "
                f"{', '.join(_TODOS_LOS_ESTADOS)}"
            )

        resultados = []
        for paciente in self.obtener_todos():
            if paciente.estado == estado:
                resultados.append(paciente)
        return resultados

    def filtrar_por_prioridad_minima(self, prioridad_min: int) -> list[Paciente]:
        """
        Filtra pacientes con prioridad mayor o igual a la indicada.
        Útil para obtener pacientes urgentes (prioridad >= 4).

        Args:
            prioridad_min: Prioridad mínima (1 a 5).

        Returns:
            Lista de pacientes con prioridad >= prioridad_min.
        """
        resultados = []
        for paciente in self.obtener_todos():
            if paciente.prioridad >= prioridad_min:
                resultados.append(paciente)
        return resultados

    # ==================================================================
    # MÉTODOS DE ESTADÍSTICA Y CONTEOS
    # ==================================================================

    def total_pacientes(self) -> int:
        """Cantidad total de pacientes en el repositorio."""
        return len(self._pacientes_sala) + len(self._pacientes_emergencia)

    def total_sala(self) -> int:
        """Cantidad de pacientes internados en sala."""
        return len(self._pacientes_sala)

    def total_emergencia(self) -> int:
        """Cantidad de pacientes en emergencias."""
        return len(self._pacientes_emergencia)

    def conteo_por_estado(self) -> dict:
        """
        Calcula cuántos pacientes hay en cada estado clínico.

        Returns:
            Diccionario {estado: cantidad} para todos los estados clínicos.
        """
        conteo = {estado: 0 for estado in _TODOS_LOS_ESTADOS}
        for paciente in self.obtener_todos():
            conteo[paciente.estado] += 1
        return conteo

    def estado_mas_frecuente(self) -> tuple[str, int]:
        """
        Determina el estado clínico más común entre todos los pacientes.

        Returns:
            Tupla (estado, cantidad). Si no hay pacientes, retorna (None, 0).
        """
        conteo = self.conteo_por_estado()
        if not conteo:
            return None, 0

        # Excluimos SIN_DATOS y FALLECIDO al buscar el más frecuente
        # si hay pacientes en otros estados
        estados_vivos = {e: c for e, c in conteo.items()
                         if e not in (ESTADO_SIN_DATOS, "FALLECIDO")}
        if estados_vivos:
            estado_max = max(estados_vivos, key=estados_vivos.get)
            return estado_max, estados_vivos[estado_max]

        estado_max = max(conteo, key=conteo.get)
        return estado_max, conteo[estado_max]

    def pacientes_criticos(self) -> list[Paciente]:
        """
        Devuelve la lista de pacientes en estado CRITICO.
        Método de conveniencia para el sistema de alertas.
        """
        return self.filtrar_por_estado("CRITICO")

    # ==================================================================
    # MÉTODOS AUXILIARES INTERNOS
    # ==================================================================

    def _existe_id(self, id_paciente: str) -> bool:
        """Verifica si un ID ya está registrado en el repositorio."""
        for paciente in self.obtener_todos():
            if paciente.id_paciente == id_paciente:
                return True
        return False

    def _extraer_por_id(self, id_paciente: str) -> Paciente:
        """
        Busca y extrae (elimina de la lista) un paciente por ID.

        Args:
            id_paciente: ID del paciente a extraer.

        Returns:
            La instancia del paciente removido.

        Raises:
            PacienteNoEncontradoError: Si el ID no existe.
        """
        # Buscar en sala
        for i, paciente in enumerate(self._pacientes_sala):
            if paciente.id_paciente == id_paciente:
                return self._pacientes_sala.pop(i)

        # Buscar en emergencias
        for i, paciente in enumerate(self._pacientes_emergencia):
            if paciente.id_paciente == id_paciente:
                return self._pacientes_emergencia.pop(i)

        raise PacienteNoEncontradoError(id_paciente)

    # ==================================================================
    # MÉTODOS ESPECIALES
    # ==================================================================

    def __str__(self) -> str:
        """Representación resumida del repositorio."""
        total = self.total_pacientes()
        if total == 0 and self.total_egresos() == 0:
            return "Repositorio de pacientes: (vacío)"

        conteo = self.conteo_por_estado()
        lineas = [
            f"Repositorio de pacientes: {total} en total",
            f"  Sala:       {self.total_sala()}",
            f"  Emergencia: {self.total_emergencia()}",
            f"  Egresos:    {self.total_egresos()}",
            "  Por estado:",
        ]
        for estado, cantidad in conteo.items():
            if cantidad > 0:
                lineas.append(f"    {estado:<12} {cantidad}")
        return "\n".join(lineas)

    def __repr__(self) -> str:
        """Representación técnica para depuración."""
        return (
            f"RepositorioPacientes("
            f"sala={self.total_sala()}, "
            f"emergencia={self.total_emergencia()})"
        )

    def __len__(self) -> int:
        """Cantidad total de pacientes (mismo que total_pacientes())."""
        return self.total_pacientes()

    def __contains__(self, id_paciente: str) -> bool:
        """
        Permite usar 'ID' in repositorio para verificar existencia.
        Ejemplo: if "PAC-0001" in repo: ...
        """
        return self._existe_id(id_paciente)


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo RepositorioPacientes.
    Demuestra:
      1. Creación del repositorio vacío.
      2. Agregar pacientes individuales y en lote.
      3. Búsqueda por ID y por nombre.
      4. Filtrado por estado y por prioridad mínima.
      5. Eliminación de pacientes.
      6. Conteos y estadísticas.
      7. Detección de IDs duplicados y pacientes no encontrados.
      8. Operador 'in' para verificar existencia.
      9. Limpiar repositorio.
    """
    from datos.generador import GeneradorDatos

    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: RepositorioPacientes")
    print("=" * 60)

    generador = GeneradorDatos(semilla=42)

    # --- Prueba 1: Repositorio vacío ---
    print("\n[1] Crear repositorio vacío:")
    repo = RepositorioPacientes()
    print(f"    {repo}")
    print(f"    len(repo) = {len(repo)}")

    # --- Prueba 2: Agregar pacientes ---
    print("\n[2] Agregar 4 pacientes de sala y 3 de emergencias:")
    for _ in range(4):
        repo.agregar_paciente(generador.generar_paciente_sala())
    for _ in range(3):
        repo.agregar_paciente(generador.generar_paciente_emergencia())
    print(f"    Total: {repo.total_pacientes()}")
    print(f"    Sala:  {repo.total_sala()}")
    print(f"    Emerg: {repo.total_emergencia()}")

    # --- Prueba 3: Listar todos ---
    print("\n[3] Listar todos los pacientes:")
    for p in repo.obtener_todos():
        tipo = "Sala" if p.__class__.__name__ == "PacienteSala" else "Emerg"
        print(f"    {p.id_paciente} | {p.nombre:<28} | {p.estado:<10} | {tipo}")

    # --- Prueba 4: Búsqueda por ID ---
    print("\n[4] Buscar paciente por ID:")
    ids = [p.id_paciente for p in repo.obtener_todos()]
    primer_id = ids[0]
    paciente = repo.buscar_por_id(primer_id)
    print(f"    ID buscado: {primer_id}")
    print(f"    Encontrado: {paciente.nombre} — {paciente.estado}")

    # --- Prueba 5: Búsqueda por nombre ---
    print("\n[5] Buscar pacientes por nombre (contiene 'Mar'):")
    resultados = repo.buscar_por_nombre("Garc")
    if resultados:
        for p in resultados:
            print(f"    {p.id_paciente}: {p.nombre}")
    else:
        print(f"    (ningún nombre contiene 'Garc' con semilla 42)")

    # --- Prueba 6: Filtrar por estado ---
    print("\n[6] Filtrar pacientes CRITICOS:")
    criticos = repo.filtrar_por_estado("CRITICO")
    print(f"    Encontrados: {len(criticos)}")
    for p in criticos:
        print(f"    {p.id_paciente}: {p.nombre}")

    # --- Prueba 7: Filtrar por prioridad mínima ---
    print("\n[7] Pacientes con prioridad >= 4:")
    urgentes = repo.filtrar_por_prioridad_minima(4)
    print(f"    Encontrados: {len(urgentes)}")
    for p in urgentes:
        print(f"    {p.id_paciente}: {p.nombre} — prioridad {p.prioridad} ({p.estado})")

    # --- Prueba 8: Conteo por estado ---
    print("\n[8] Conteo de pacientes por estado:")
    conteo = repo.conteo_por_estado()
    for estado, cantidad in conteo.items():
        if cantidad > 0:
            print(f"    {estado:<12} {cantidad}")

    # --- Prueba 9: Estado más frecuente ---
    print("\n[9] Estado clínico más frecuente:")
    estado_frec, cant_frec = repo.estado_mas_frecuente()
    print(f"    {estado_frec}: {cant_frec} paciente(s)")

    # --- Prueba 10: Operador 'in' ---
    print(f"\n[10] Verificar existencia con 'in':")
    print(f"    '{primer_id}' en repo: {primer_id in repo}")
    print(f"    'PAC-9999' en repo: {'PAC-9999' in repo}")

    # --- Prueba 11: Eliminar paciente ---
    print(f"\n[11] Eliminar paciente {primer_id}:")
    eliminado = repo.eliminar_paciente(primer_id)
    print(f"    Eliminado: {eliminado.nombre}")
    print(f"    Total tras eliminar: {repo.total_pacientes()}")
    print(f"    '{primer_id}' en repo: {primer_id in repo}")

    # --- Prueba 12: Error al buscar ID inexistente ---
    print("\n[12] Buscar paciente con ID inexistente (debe lanzar error):")
    try:
        repo.buscar_por_id("PAC-9999")
        print("    ERROR: No se lanzó la excepción.")
    except PacienteNoEncontradoError as e:
        print(f"    PacienteNoEncontradoError: {e}")

    # --- Prueba 13: Error al duplicar ID ---
    print("\n[13] Intentar agregar paciente con ID duplicado:")
    ids_actuales = [p.id_paciente for p in repo.obtener_todos()]
    if ids_actuales:
        dup_id = ids_actuales[0]
        # Creamos un paciente forzando el mismo ID (simulando duplicado)
        from modelos.paciente_sala import PacienteSala
        dup_paciente = PacienteSala(
            nombre="Duplicado Test", edad=99, genero="Masculino",
            numero_cama=999, id_paciente=dup_id,
        )
        try:
            repo.agregar_paciente(dup_paciente)
            print("    ERROR: No se lanzó la excepción de duplicado.")
        except ValueError as e:
            print(f"    ValueError: {e}")

    # --- Prueba 14: Agregar lote de pacientes ---
    print("\n[14] Agregar lote de 5 pacientes de emergencias:")
    lote = generador.generar_pacientes_emergencia(cantidad=5)
    repo.agregar_pacientes(lote)
    print(f"    Total tras lote: {repo.total_pacientes()}")

    # --- Prueba 15: __str__ completo ---
    print(f"\n[15] Representación completa:\n{repo}")

    # --- Prueba 16: Limpiar repositorio ---
    print("\n[16] Limpiar repositorio:")
    repo.limpiar()
    print(f"    {repo}")
    print(f"    len(repo) = {len(repo)}")

    print("\n[OK] Pruebas de RepositorioPacientes completadas.\n")
