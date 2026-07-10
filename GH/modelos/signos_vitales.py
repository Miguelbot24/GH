"""
Módulo: signos_vitales.py
Sprint 0 — Modelo de Signos Vitales.

Define la clase SignosVitales, que encapsula los seis parámetros biomédicos
monitoreados de un paciente. Demuestra el pilar de Encapsulamiento de la POO:
todos los atributos son privados (doble guion bajo) y solo se accede mediante
getters y setters, que incluyen validaciones de rango fisiológico.

Dependencias previas necesarias:
    - config.py (constantes de rangos normales y umbrales)
"""

import sys
import os

# Permite ejecutar este archivo directamente (python modelos/signos_vitales.py)
# encontrando config.py en el directorio raíz del proyecto.
if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    RANGOS_NORMALES,
    UMBRALES_SALA,
    ORDEN_SEVERIDAD_SALA,
    ESTADO_ESTABLE,
    ESTADO_SIN_DATOS,
    ESTADO_FALLECIDO,
    ESTADOS_SALA,
    NOMBRES_SIGNOS,
    UNIDADES_SIGNOS,
)


class SignosVitales:
    """
    Encapsula los seis signos vitales de un paciente:
      - Frecuencia cardíaca (HR)
      - Frecuencia respiratoria (RR)
      - Saturación de oxígeno (SpO2)
      - Presión arterial sistólica
      - Presión arterial diastólica
      - Temperatura corporal

    Principio OOP — Encapsulamiento:
        Cada atributo se almacena con doble guion bajo (name mangling),
        lo que impide el acceso directo desde fuera de la clase.
        Toda lectura y escritura pasa por properties que validan los valores.
    """

    # ------------------------------------------------------------------
    # Límites fisiológicos absolutos (más allá de estos valores, los
    # datos se consideran inválidos para un ser humano vivo).
    # ------------------------------------------------------------------
    _LIMITES_FISIOLOGICOS = {
        "frecuencia_cardiaca":     (0, 350),
        "frecuencia_respiratoria": (0, 80),
        "saturacion_oxigeno":      (0, 100),
        "presion_sistolica":       (0, 300),
        "presion_diastolica":      (0, 200),
        "temperatura":             (20.0, 45.0),
    }

    def __init__(
        self,
        frecuencia_cardiaca:     float = 0.0,
        frecuencia_respiratoria: float = 0.0,
        saturacion_oxigeno:      float = 0.0,
        presion_sistolica:       float = 0.0,
        presion_diastolica:      float = 0.0,
        temperatura:             float = 0.0,
    ):
        """
        Constructor.
        Recibe los seis signos vitales. Si no se proporcionan, se inicializan
        en 0.0 (lo que el sistema interpretará como SIN_DATOS o FALLECIDO
        según el contexto).
        """
        # Atributos privados: la convención __nombre activa el name mangling
        # de Python, renombrándolos internamente a _SignosVitales__nombre.
        self.__frecuencia_cardiaca     = 0.0
        self.__frecuencia_respiratoria = 0.0
        self.__saturacion_oxigeno      = 0.0
        self.__presion_sistolica       = 0.0
        self.__presion_diastolica      = 0.0
        self.__temperatura             = 0.0

        # Usamos los setters para que apliquen la validación automáticamente
        self.frecuencia_cardiaca     = frecuencia_cardiaca
        self.frecuencia_respiratoria = frecuencia_respiratoria
        self.saturacion_oxigeno      = saturacion_oxigeno
        self.presion_sistolica       = presion_sistolica
        self.presion_diastolica      = presion_diastolica
        self.temperatura             = temperatura

    # ==================================================================
    # PROPIEDADES (GETTERS Y SETTERS)
    # ==================================================================
    # Cada property permite leer y escribir el atributo privado,
    # aplicando validación al escribir.

    # --- Frecuencia Cardíaca ---
    @property
    def frecuencia_cardiaca(self) -> float:
        """Devuelve la frecuencia cardíaca en bpm."""
        return self.__frecuencia_cardiaca

    @frecuencia_cardiaca.setter
    def frecuencia_cardiaca(self, valor: float) -> None:
        """Asigna la frecuencia cardíaca validando que esté en rango fisiológico."""
        self._validar_rango("frecuencia_cardiaca", valor)
        self.__frecuencia_cardiaca = float(valor)

    # --- Frecuencia Respiratoria ---
    @property
    def frecuencia_respiratoria(self) -> float:
        """Devuelve la frecuencia respiratoria en rpm."""
        return self.__frecuencia_respiratoria

    @frecuencia_respiratoria.setter
    def frecuencia_respiratoria(self, valor: float) -> None:
        """Asigna la frecuencia respiratoria validando que esté en rango fisiológico."""
        self._validar_rango("frecuencia_respiratoria", valor)
        self.__frecuencia_respiratoria = float(valor)

    # --- Saturación de Oxígeno ---
    @property
    def saturacion_oxigeno(self) -> float:
        """Devuelve la saturación de oxígeno en porcentaje (0–100)."""
        return self.__saturacion_oxigeno

    @saturacion_oxigeno.setter
    def saturacion_oxigeno(self, valor: float) -> None:
        """Asigna la SpO2 validando que esté en rango fisiológico."""
        self._validar_rango("saturacion_oxigeno", valor)
        self.__saturacion_oxigeno = float(valor)

    # --- Presión Sistólica ---
    @property
    def presion_sistolica(self) -> float:
        """Devuelve la presión arterial sistólica en mmHg."""
        return self.__presion_sistolica

    @presion_sistolica.setter
    def presion_sistolica(self, valor: float) -> None:
        """Asigna la presión sistólica validando que esté en rango fisiológico."""
        self._validar_rango("presion_sistolica", valor)
        self.__presion_sistolica = float(valor)

    # --- Presión Diastólica ---
    @property
    def presion_diastolica(self) -> float:
        """Devuelve la presión arterial diastólica en mmHg."""
        return self.__presion_diastolica

    @presion_diastolica.setter
    def presion_diastolica(self, valor: float) -> None:
        """Asigna la presión diastólica validando que esté en rango fisiológico."""
        self._validar_rango("presion_diastolica", valor)
        self.__presion_diastolica = float(valor)

    # --- Temperatura ---
    @property
    def temperatura(self) -> float:
        """Devuelve la temperatura corporal en grados Celsius."""
        return self.__temperatura

    @temperatura.setter
    def temperatura(self, valor: float) -> None:
        """Asigna la temperatura validando que esté en rango fisiológico."""
        self._validar_rango("temperatura", valor)
        self.__temperatura = float(valor)

    # ==================================================================
    # MÉTODO PRIVADO DE VALIDACIÓN
    # ==================================================================

    def _validar_rango(self, nombre_signo: str, valor: float) -> None:
        """
        Verifica que el valor esté dentro de los límites fisiológicos absolutos
        definidos en _LIMITES_FISIOLOGICOS.

        Si el valor es 0, se permite siempre (representa "sin datos" o
        "fallecido" en el contexto de la simulación).

        Lanza ValueError si el valor está fuera del rango permitido.
        """
        if valor == 0.0:
            return  # 0 es válido: significa ausencia de señal o fallecido

        minimo, maximo = self._LIMITES_FISIOLOGICOS[nombre_signo]
        if not (minimo <= valor <= maximo):
            nombre_legible = NOMBRES_SIGNOS.get(nombre_signo, nombre_signo)
            raise ValueError(
                f"{nombre_legible}: valor {valor} fuera del rango "
                f"fisiológico [{minimo}, {maximo}]"
            )

    # ==================================================================
    # MÉTODOS DE CLASIFICACIÓN DE ESTADO
    # ==================================================================

    def clasificar_signo(
        self,
        nombre_signo: str,
        umbrales: dict = None,
        orden:    list = None,
    ) -> str:
        """
        Evalúa un signo vital individual contra los umbrales dados y
        devuelve el estado clínico resultante.

        Recorre los umbrales en orden de severidad (de más grave a más leve).
        El primer rango que contenga el valor del signo determina el estado.

        Args:
            nombre_signo: clave del signo (ej. "frecuencia_cardiaca").
            umbrales:     Diccionario de umbrales por área (UMBRALES_SALA
                          o UMBRALES_EMERGENCIA). Por defecto UMBRALES_SALA.
            orden:        Lista de estados en orden de severidad. Por
                          defecto ORDEN_SEVERIDAD_SALA.

        Returns:
            Una de las constantes de estado del área correspondiente.
        """
        if umbrales is None:
            umbrales = UMBRALES_SALA
        if orden is None:
            orden = ORDEN_SEVERIDAD_SALA

        valor = self._obtener_valor(nombre_signo)

        if valor == 0.0:
            if self._todos_en_cero():
                return ESTADO_FALLECIDO
            return ESTADO_SIN_DATOS

        umbrales_signo = umbrales.get(nombre_signo, {})
        for estado in orden:
            if estado not in umbrales_signo:
                continue
            for vmin, vmax in umbrales_signo[estado]:
                if vmin <= valor <= vmax:
                    return estado

        return ESTADO_SIN_DATOS

    def obtener_estado_global(
        self,
        umbrales: dict = None,
        orden:    list = None,
    ) -> str:
        """
        Evalúa todos los signos vitales y devuelve el estado clínico global
        del paciente: el peor estado entre todos sus signos.

        Args:
            umbrales: Umbrales del área (UMBRALES_SALA o UMBRALES_EMERGENCIA).
            orden:    Orden de severidad del área.

        Returns:
            El estado más severo encontrado entre los seis signos vitales.
        """
        if umbrales is None:
            umbrales = UMBRALES_SALA
        if orden is None:
            orden = ORDEN_SEVERIDAD_SALA

        if self._todos_en_cero():
            return ESTADO_FALLECIDO

        # Empezamos asumiendo el estado menos grave del área
        peor_estado = orden[-1]

        for nombre_signo in umbrales.keys():
            estado_signo = self.clasificar_signo(nombre_signo, umbrales, orden)
            if orden.index(estado_signo) < orden.index(peor_estado):
                peor_estado = estado_signo

        return peor_estado

    def _todos_en_cero(self) -> bool:
        """Verifica si los seis signos vitales tienen valor 0.0."""
        return all(
            self._obtener_valor(signo) == 0.0
            for signo in UMBRALES_SALA.keys()
        )

    def _obtener_valor(self, nombre_signo: str) -> float:
        """
        Devuelve el valor actual del signo vital solicitado por su nombre clave.
        Útil para iterar sobre todos los signos sin escribir condicionales.
        """
        # Mapeo de claves de signo a atributos privados
        mapeo = {
            "frecuencia_cardiaca":     self.__frecuencia_cardiaca,
            "frecuencia_respiratoria": self.__frecuencia_respiratoria,
            "saturacion_oxigeno":      self.__saturacion_oxigeno,
            "presion_sistolica":       self.__presion_sistolica,
            "presion_diastolica":      self.__presion_diastolica,
            "temperatura":             self.__temperatura,
        }
        return mapeo.get(nombre_signo, 0.0)

    # ==================================================================
    # MÉTODOS DE CONVENIENCIA
    # ==================================================================

    def esta_en_rango_normal(self, nombre_signo: str) -> bool:
        """
        Indica si un signo vital está dentro de su rango normal fisiológico.
        Útil para reportes rápidos sin necesidad de clasificar el estado.
        """
        valor = self._obtener_valor(nombre_signo)
        minimo, maximo = RANGOS_NORMALES.get(nombre_signo, (0, 0))
        return minimo <= valor <= maximo

    def a_diccionario(self) -> dict:
        """
        Devuelve todos los signos vitales como un diccionario.
        Las claves son los nombres internos de los signos.
        Útil para serialización, depuración o paso de datos a la interfaz.
        """
        return {
            "frecuencia_cardiaca":     self.__frecuencia_cardiaca,
            "frecuencia_respiratoria": self.__frecuencia_respiratoria,
            "saturacion_oxigeno":      self.__saturacion_oxigeno,
            "presion_sistolica":       self.__presion_sistolica,
            "presion_diastolica":      self.__presion_diastolica,
            "temperatura":             self.__temperatura,
        }

    def obtener_presion_arterial(self) -> str:
        """
        Devuelve la presión arterial formateada como 'sistólica/diastólica'.
        Ejemplo: '120/80 mmHg'.
        """
        return f"{self.__presion_sistolica:.0f}/{self.__presion_diastolica:.0f} mmHg"

    def copiar(self) -> "SignosVitales":
        """
        Crea y devuelve una copia independiente de estos signos vitales.
        Evita efectos colaterales al modificar signos sin afectar el original.
        """
        return SignosVitales(
            frecuencia_cardiaca     = self.__frecuencia_cardiaca,
            frecuencia_respiratoria = self.__frecuencia_respiratoria,
            saturacion_oxigeno      = self.__saturacion_oxigeno,
            presion_sistolica       = self.__presion_sistolica,
            presion_diastolica      = self.__presion_diastolica,
            temperatura             = self.__temperatura,
        )

    # ==================================================================
    # MÉTODOS ESPECIALES (DUNDERS)
    # ==================================================================

    def __str__(self) -> str:
        """
        Representación legible en consola.
        Muestra cada signo con su valor, unidad y el estado clínico que
        le corresponde según los umbrales.
        """
        lineas = ["-- Signos Vitales --"]
        for signo in [
            "frecuencia_cardiaca",
            "frecuencia_respiratoria",
            "saturacion_oxigeno",
            "presion_sistolica",
            "presion_diastolica",
            "temperatura",
        ]:
            valor  = self._obtener_valor(signo)
            unidad = UNIDADES_SIGNOS.get(signo, "")
            estado = self.clasificar_signo(signo)
            nombre = NOMBRES_SIGNOS.get(signo, signo)
            lineas.append(
                f"  {nombre:<35} {valor:>6.1f} {unidad:<5} [{estado}]"
            )
        lineas.append(f"  {'ESTADO GLOBAL':<35} {'':>6} {'':<5} [{self.obtener_estado_global()}]")
        return "\n".join(lineas)

    def __repr__(self) -> str:
        """
        Representación técnica para depuración.
        Muestra el constructor con todos los valores.
        """
        return (
            f"SignosVitales("
            f"HR={self.__frecuencia_cardiaca:.1f}, "
            f"RR={self.__frecuencia_respiratoria:.1f}, "
            f"SpO2={self.__saturacion_oxigeno:.1f}, "
            f"PS={self.__presion_sistolica:.1f}, "
            f"PD={self.__presion_diastolica:.1f}, "
            f"Temp={self.__temperatura:.1f})"
        )


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo SignosVitales.
    Demuestra:
      1. Instanciación con valores normales y lectura de getters.
      2. Clasificación individual de cada signo contra los umbrales.
      3. Cálculo del estado global.
      4. Uso de setters con validación.
      5. Manejo de error al asignar un valor fuera de rango fisiológico.
      6. Representación con __str__ y __repr__.
      7. Copia de la instancia.
    """
    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: SignosVitales")
    print("=" * 60)

    # --- Prueba 1: Instanciar con valores normales ---
    print("\n[1] Crear SignosVitales con valores normales:")
    signos = SignosVitales(
        frecuencia_cardiaca=72.0,
        frecuencia_respiratoria=16.0,
        saturacion_oxigeno=98.0,
        presion_sistolica=118.0,
        presion_diastolica=76.0,
        temperatura=36.5,
    )
    print(signos)

    # --- Prueba 2: Leer valores individuales con getters ---
    print("\n[2] Lectura de atributos individuales (getters):")
    print(f"    HR    = {signos.frecuencia_cardiaca} bpm")
    print(f"    RR    = {signos.frecuencia_respiratoria} rpm")
    print(f"    SpO2  = {signos.saturacion_oxigeno} %")
    print(f"    PA    = {signos.obtener_presion_arterial()}")
    print(f"    Temp  = {signos.temperatura} °C")

    # --- Prueba 3: Clasificar cada signo individualmente ---
    print("\n[3] Clasificación individual de cada signo:")
    for signo in [
        "frecuencia_cardiaca",
        "frecuencia_respiratoria",
        "saturacion_oxigeno",
        "presion_sistolica",
        "presion_diastolica",
        "temperatura",
    ]:
        estado = signos.clasificar_signo(signo)
        nombre = NOMBRES_SIGNOS.get(signo, signo)
        print(f"    {nombre:<35} -> {estado}")

    # --- Prueba 4: Estado global ---
    print(f"\n[4] Estado global del paciente: {signos.obtener_estado_global()}")

    # --- Prueba 5: Usar setters para modificar un signo ---
    print("\n[5] Modificar SpO2 a 82% (zona ATENCION) con setter:")
    signos.saturacion_oxigeno = 82.0
    print(f"    Nuevo SpO2 = {signos.saturacion_oxigeno} %")
    print(f"    Clasificación SpO2 = {signos.clasificar_signo('saturacion_oxigeno')}")
    print(f"    Nuevo estado global = {signos.obtener_estado_global()}")

    # --- Prueba 6: Verificar rango normal ---
    print("\n[6] ¿Está cada signo en rango normal?")
    for signo in [
        "frecuencia_cardiaca",
        "frecuencia_respiratoria",
        "saturacion_oxigeno",
        "presion_sistolica",
        "presion_diastolica",
        "temperatura",
    ]:
        nombre = NOMBRES_SIGNOS.get(signo, signo)
        normal = signos.esta_en_rango_normal(signo)
        print(f"    {nombre:<35} -> {'Si' if normal else 'NO (alterado)'}")

    # --- Prueba 7: Diccionario ---
    print("\n[7] Representación como diccionario:")
    datos = signos.a_diccionario()
    for clave, valor in datos.items():
        print(f"    {clave}: {valor}")

    # --- Prueba 8: Copia independiente ---
    print("\n[8] Crear copia y modificar la copia sin afectar el original:")
    copia = signos.copiar()
    copia.frecuencia_cardiaca = 45.0
    print(f"    Original HR = {signos.frecuencia_cardiaca} bpm (no cambió)")
    print(f"    Copia    HR = {copia.frecuencia_cardiaca} bpm (sí cambió)")

    # --- Prueba 9: Paciente con signos en cero (FALLECIDO) ---
    print("\n[9] SignosVitales con todos los valores en 0 (FALLECIDO):")
    signos_fallecido = SignosVitales()
    print(f"    Estado global: {signos_fallecido.obtener_estado_global()}")

    # --- Prueba 10: Validación de rango fisiológico ---
    print("\n[10] Intento de asignar HR = 500 bpm (debe lanzar ValueError):")
    try:
        signos.frecuencia_cardiaca = 500.0
        print("    ERROR: No se lanzó la excepción esperada.")
    except ValueError as e:
        print(f"    ValueError capturado: {e}")

    # --- Prueba 11: __repr__ ---
    print("\n[11] Representación técnica (repr):")
    print(f"    {repr(signos)}")

    print("\n[OK] Pruebas de SignosVitales completadas.\n")
