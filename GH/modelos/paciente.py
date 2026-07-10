"""
Módulo: paciente.py
Sprint 0 — Clase abstracta base Paciente.

Define la clase Paciente como una clase abstracta (ABC) de la que heredarán
PacienteSala y PacienteEmergencia. Demuestra el pilar de Abstracción de la
POO: declara la interfaz común que toda subclase debe implementar, usando
@abstractmethod para forzar la implementación de calcular_estado().

Dependencias previas necesarias:
    - config.py       (constantes de estados, colores, prioridades)
    - signos_vitales.py (SignosVitales, modelo de signos encapsulados)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abc import ABC, abstractmethod
from datetime import datetime

from config import (
    ESTADO_SIN_DATOS,
    ESTADO_FALLECIDO,
    PRIORIDAD_ESTADO,
    COLORES_ESTADO,
    ICONOS_AVATAR,
)

from modelos.signos_vitales import SignosVitales


class Paciente(ABC):
    """
    Clase abstracta base para todos los pacientes del sistema hospitalario.

    Principio OOP — Abstracción:
        Declara atributos y métodos comunes a todo paciente (nombre, edad,
        signos vitales, historial) pero deja como abstracto el método
        calcular_estado(), obligando a cada subclase a definir su propia
        lógica de clasificación clínica según el contexto (sala o emergencia).

    No se puede instanciar directamente: hacer Paciente(...) lanza TypeError.
    Solo se instancian sus subclases concretas: PacienteSala, PacienteEmergencia.
    """

    # ------------------------------------------------------------------
    # Contador interno de clase para generar IDs únicos automáticamente
    # ------------------------------------------------------------------
    _contador_ids = 0

    def __init__(
        self,
        nombre:      str,
        edad:        int,
        genero:      str,
        tipo_avatar: str = "hombre",
        id_paciente: str = None,
        razon_ingreso: str = "",
        doctor_asignado: str = "",
    ):
        """
        Constructor de la clase abstracta Paciente.

        Args:
            nombre:      Nombre completo del paciente.
            edad:        Edad en años.
            genero:      "Masculino" o "Femenino".
            tipo_avatar: Clave del icono en ICONOS_AVATAR. Define qué imagen
                         se muestra en la tarjeta (hombre, mujer, anciano,
                         anciana, nino, nina). Por defecto "hombre".
            id_paciente: Identificador único opcional. Si no se proporciona,
                         se genera automáticamente con el formato "PAC-0001".
            razon_ingreso: Razón de ingreso al hospital (ej. "Dolor torácico").
            doctor_asignado: Nombre del médico asignado al paciente.
        """
        # Generar ID automático si no se proporciona uno
        if id_paciente is None:
            Paciente._contador_ids += 1
            id_paciente = f"PAC-{Paciente._contador_ids:04d}"

        # ------------------------------------------------------------------
        # Atributos protegidos (un guion bajo): accesibles desde subclases,
        # pero por convención no deben usarse fuera de la jerarquía.
        # ------------------------------------------------------------------
        self._id_paciente = id_paciente
        self._nombre      = nombre
        self._edad        = edad
        self._genero      = genero
        self._tipo_avatar = tipo_avatar

        # Fecha y hora de ingreso al sistema (se registra al crear el paciente)
        self._fecha_ingreso = datetime.now()

        # Signos vitales: inicialmente SIN_DATOS (todo en cero).
        # Se actualizarán con el generador de datos o con el monitor.
        self._signos_vitales = SignosVitales()

        # Historial médico: se inicializará en Sprint 1 cuando exista la clase.
        # Por ahora se almacena como None para evitar dependencia circular.
        self._historial = None

        # Estado clínico actual: comienza como SIN_DATOS hasta que el monitor
        # evalúe los signos vitales por primera vez.
        self._estado = ESTADO_SIN_DATOS

        # Atributos de egreso: None mientras el paciente esté activo
        self._tipo_egreso  = None   # DADO_DE_ALTA, FUGADO o None
        self._fecha_egreso = None   # datetime del egreso

        # Razón de ingreso y médico asignado
        self._razon_ingreso   = razon_ingreso
        self._doctor_asignado = doctor_asignado

    # ==================================================================
    # PROPIEDADES DE SOLO LECTURA (GETTERS)
    # ==================================================================

    @property
    def id_paciente(self) -> str:
        """Identificador único del paciente (ej. 'PAC-0001')."""
        return self._id_paciente

    @property
    def nombre(self) -> str:
        """Nombre completo del paciente."""
        return self._nombre

    @property
    def edad(self) -> int:
        """Edad del paciente en años."""
        return self._edad

    @property
    def genero(self) -> str:
        """Género del paciente ('Masculino' o 'Femenino')."""
        return self._genero

    @property
    def tipo_avatar(self) -> str:
        """
        Clave del icono de avatar a usar en la interfaz gráfica.
        Valores posibles: 'hombre', 'mujer', 'anciano', 'anciana', 'nino', 'nina'.
        """
        return self._tipo_avatar

    @property
    def fecha_ingreso(self) -> datetime:
        """Fecha y hora en que el paciente ingresó al sistema."""
        return self._fecha_ingreso

    @property
    def signos_vitales(self) -> SignosVitales:
        """Objeto SignosVitales con los parámetros biomédicos actuales."""
        return self._signos_vitales

    @signos_vitales.setter
    def signos_vitales(self, nuevos_signos: SignosVitales) -> None:
        """
        Reemplaza los signos vitales del paciente.
        Tras actualizar los signos, se recalcula automáticamente el estado.
        """
        if not isinstance(nuevos_signos, SignosVitales):
            raise TypeError("signos_vitales debe ser una instancia de SignosVitales")
        self._signos_vitales = nuevos_signos
        self.actualizar_estado()

    @property
    def historial(self):
        """
        Historial médico del paciente.
        Retorna None hasta que el módulo historial.py sea implementado (Sprint 1).
        """
        return self._historial

    @historial.setter
    def historial(self, valor) -> None:
        """Asigna el historial médico al paciente."""
        self._historial = valor

    @property
    def estado(self) -> str:
        """
        Estado clínico actual del paciente.
        Una de las constantes: CRITICO, PRUDENTE, BASICO, ESTABLE,
        FALLECIDO o SIN_DATOS.
        """
        return self._estado

    @property
    def prioridad(self) -> int:
        """
        Prioridad numérica del paciente según su estado clínico.
        Se usa para ordenar colas de atención (mayor = más urgente).
        """
        return PRIORIDAD_ESTADO.get(self._estado, 0)

    @property
    def color_estado(self) -> str:
        """Color hexadecimal asociado al estado clínico actual."""
        return COLORES_ESTADO.get(self._estado, "#FFFFFF")

    @property
    def ruta_avatar(self) -> str:
        """
        Ruta al archivo PNG del avatar según el tipo_avatar del paciente.
        Si el tipo no se encuentra en el mapeo, retorna cadena vacía.
        """
        return ICONOS_AVATAR.get(self._tipo_avatar, "")

    @property
    def tipo_egreso(self) -> str | None:
        """
        Tipo de egreso del paciente.
        None si está activo, 'DADO_DE_ALTA' o 'FUGADO' si fue egresado.
        """
        return self._tipo_egreso

    @property
    def fecha_egreso(self) -> datetime | None:
        """
        Fecha y hora en que el paciente fue egresado.
        None si el paciente sigue activo.
        """
        return self._fecha_egreso

    @property
    def esta_activo(self) -> bool:
        """True si el paciente NO ha sido egresado (tipo_egreso es None)."""
        return self._tipo_egreso is None

    @property
    def razon_ingreso(self) -> str:
        """Razón o motivo de ingreso al hospital."""
        return self._razon_ingreso

    @razon_ingreso.setter
    def razon_ingreso(self, valor: str) -> None:
        """Actualiza la razón de ingreso."""
        self._razon_ingreso = valor

    @property
    def doctor_asignado(self) -> str:
        """Nombre del médico asignado al paciente."""
        return self._doctor_asignado

    @doctor_asignado.setter
    def doctor_asignado(self, valor: str) -> None:
        """Actualiza el médico asignado."""
        self._doctor_asignado = valor

    # ==================================================================
    # MÉTODO ABSTRACTO (DEBE SER IMPLEMENTADO POR LAS SUBCLASES)
    # ==================================================================

    @abstractmethod
    def calcular_estado(self) -> str:
        """
        Calcula y devuelve el estado clínico del paciente.

        Principio OOP — Polimorfismo:
            Cada subclase implementa su propia versión de este método:
            - PacienteSala: considera número de cama y tiempo de internamiento.
            - PacienteEmergencia: considera tiempo de espera y prioridad
              administrativa.

        Returns:
            Una de las constantes de estado: CRITICO, PRUDENTE, BASICO,
            ESTABLE, FALLECIDO o SIN_DATOS.
        """
        pass

    # ==================================================================
    # MÉTODOS CONCRETOS (HEREDADOS TAL CUAL POR LAS SUBCLASES)
    # ==================================================================

    def actualizar_estado(self) -> str:
        """
        Recalcula el estado clínico llamando a calcular_estado() (polimórfico)
        y actualiza el atributo interno _estado.

        Returns:
            El nuevo estado clínico.
        """
        self._estado = self.calcular_estado()
        return self._estado

    def marcar_egreso(self, tipo_egreso: str) -> None:
        """
        Marca al paciente como egresado (DADO_DE_ALTA o FUGADO).

        Args:
            tipo_egreso: Una de las constantes TIPO_EGRESO_ALTA o TIPO_EGRESO_FUGA.

        Raises:
            ValueError: Si el tipo de egreso no es válido.
        """
        from config import ESTADOS_EGRESO
        if tipo_egreso not in ESTADOS_EGRESO:
            raise ValueError(
                f"Tipo de egreso no válido: '{tipo_egreso}'. "
                f"Debe ser uno de: {ESTADOS_EGRESO}"
            )
        self._tipo_egreso = tipo_egreso
        self._fecha_egreso = datetime.now()

    def tiempo_transcurrido(self) -> str:
        """
        Calcula cuánto tiempo lleva el paciente en el sistema desde su ingreso.

        Returns:
            Cadena legible como '2h 15m' o '45m'.
        """
        diferencia = datetime.now() - self._fecha_ingreso
        horas   = diferencia.seconds // 3600
        minutos = (diferencia.seconds % 3600) // 60

        if diferencia.days > 0:
            return f"{diferencia.days}d {horas}h"
        elif horas > 0:
            return f"{horas}h {minutos}m"
        else:
            return f"{minutos}m"

    def resumen(self) -> dict:
        """
        Devuelve un diccionario con los datos principales del paciente.
        Útil para pasar información a la interfaz gráfica o a reportes.
        """
        return {
            "id":            self._id_paciente,
            "nombre":        self._nombre,
            "edad":          self._edad,
            "genero":        self._genero,
            "estado":        self._estado,
            "prioridad":     self.prioridad,
            "color":         self.color_estado,
            "avatar":        self.ruta_avatar,
            "tiempo":        self.tiempo_transcurrido(),
            "signos":        self._signos_vitales.a_diccionario(),
            "presion":       self._signos_vitales.obtener_presion_arterial(),
        }

    # ==================================================================
    # MÉTODOS ESPECIALES (DUNDERS)
    # ==================================================================

    def __str__(self) -> str:
        """
        Representación legible en consola.
        Muestra los datos demográficos, el estado y los signos vitales.
        """
        return (
            f"Paciente: {self._nombre}\n"
            f"  ID:      {self._id_paciente}\n"
            f"  Edad:    {self._edad} años\n"
            f"  Género:  {self._genero}\n"
            f"  Avatar:  {self._tipo_avatar}\n"
            f"  Ingreso: {self._fecha_ingreso.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"  Estado:  {self._estado} (prioridad: {self.prioridad})\n"
            f"  Tiempo:  {self.tiempo_transcurrido()}\n"
            f"{self._signos_vitales}"
        )

    def __repr__(self) -> str:
        """
        Representación técnica para depuración.
        """
        return (
            f"Paciente(id={self._id_paciente!r}, "
            f"nombre={self._nombre!r}, "
            f"edad={self._edad}, "
            f"estado={self._estado!r})"
        )


# ============================================================================
# CLASE CONCRETA DE PRUEBA (SOLO PARA EL BLOQUE if __name__ == "__main__")
# ============================================================================
# Como Paciente es abstracta, no se puede instanciar directamente.
# Para probarla, definimos una subclase temporal dentro del bloque de prueba.


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo Paciente.
    Demuestra:
      1. Que NO se puede instanciar la clase abstracta directamente.
      2. Creación de una subclase concreta temporal con su propio
         calcular_estado().
      3. Uso de getters para datos demográficos.
      4. Asignación de signos vitales y recálculo de estado.
      5. Tiempo transcurrido desde el ingreso.
      6. Método resumen() como diccionario.
      7. Representaciones __str__ y __repr__.
      8. Prioridad según el estado.
    """
    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: Paciente (clase abstracta)")
    print("=" * 60)

    # --- Prueba 1: No se puede instanciar Paciente directamente ---
    print("\n[1] Intentar instanciar Paciente directamente (debe fallar):")
    try:
        p = Paciente(nombre="Test", edad=30, genero="Masculino")
        print("    ERROR: Se instanció la clase abstracta (no debería).")
    except TypeError as e:
        print(f"    TypeError capturado: {e}")

    # --- Prueba 2: Subclase concreta de prueba ---
    print("\n[2] Crear una subclase concreta para pruebas:")

    class PacientePrueba(Paciente):
        """
        Subclase temporal de Paciente que implementa calcular_estado().
        Solo existe dentro del bloque de prueba para validar la clase base.
        Delega la clasificación al método obtener_estado_global() de los
        signos vitales (comportamiento por defecto simple).
        """

        def calcular_estado(self) -> str:
            """
            Implementación de prueba: el estado se determina exclusivamente
            por los signos vitales, sin considerar factores de contexto.
            """
            return self._signos_vitales.obtener_estado_global()

    paciente = PacientePrueba(
        nombre="Maria Lopez",
        edad=45,
        genero="Femenino",
        tipo_avatar="mujer",
    )
    print(f"    Paciente creado: {paciente.nombre} (ID: {paciente.id_paciente})")

    # --- Prueba 3: Leer datos demográficos ---
    print("\n[3] Lectura de datos demográficos (getters):")
    print(f"    Nombre:   {paciente.nombre}")
    print(f"    Edad:     {paciente.edad}")
    print(f"    Género:   {paciente.genero}")
    print(f"    Avatar:   {paciente.tipo_avatar}")
    print(f"    Ingreso:  {paciente.fecha_ingreso.strftime('%H:%M:%S')}")

    # --- Prueba 4: Estado inicial (SIN_DATOS porque signos están en cero) ---
    print(f"\n[4] Estado inicial (signos en cero): {paciente.estado}")
    print(f"    Prioridad: {paciente.prioridad}")
    print(f"    Color:     {paciente.color_estado}")

    # --- Prueba 5: Asignar signos vitales normales y ver estado ---
    print("\n[5] Asignar signos vitales normales:")
    signos_normales = SignosVitales(
        frecuencia_cardiaca=75.0,
        frecuencia_respiratoria=15.0,
        saturacion_oxigeno=97.0,
        presion_sistolica=115.0,
        presion_diastolica=72.0,
        temperatura=36.7,
    )
    paciente.signos_vitales = signos_normales  # Usa el setter, recalcula estado
    print(f"    Nuevo estado:  {paciente.estado}")
    print(f"    Nueva prioridad: {paciente.prioridad}")

    # --- Prueba 6: Tiempo transcurrido ---
    print(f"\n[6] Tiempo desde el ingreso: {paciente.tiempo_transcurrido()}")

    # --- Prueba 7: Método resumen() ---
    print("\n[7] Resumen del paciente (diccionario):")
    resumen = paciente.resumen()
    for clave, valor in resumen.items():
        if clave == "signos":
            print(f"    {clave}: (dict con {len(valor)} signos vitales)")
        else:
            print(f"    {clave}: {valor}")

    # --- Prueba 8: Modificar signos a valores críticos ---
    print("\n[8] Cambiar signos a valores críticos (SpO2 = 80%):")
    paciente.signos_vitales.saturacion_oxigeno = 80.0
    paciente.actualizar_estado()  # Recalcular explícitamente
    print(f"    Estado:  {paciente.estado}")
    print(f"    Color:   {paciente.color_estado}")
    print(f"    Prioridad: {paciente.prioridad}")

    # --- Prueba 9: __str__ ---
    print(f"\n[9] Representación __str__:\n{paciente}")

    # --- Prueba 10: __repr__ ---
    print(f"\n[10] Representación __repr__:\n    {repr(paciente)}")

    # --- Prueba 11: Segundo paciente para ver IDs autoincrementales ---
    print("\n[11] Crear segundo paciente (ID automático):")
    paciente2 = PacientePrueba(
        nombre="Carlos Ruiz",
        edad=60,
        genero="Masculino",
        tipo_avatar="anciano",
    )
    print(f"    ID: {paciente2.id_paciente}")
    print(f"    Avatar: {paciente2.tipo_avatar}")
    print(f"    Ruta avatar: {paciente2.ruta_avatar}")

    print("\n[OK] Pruebas de Paciente completadas.\n")
