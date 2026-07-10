"""
Módulo: generador.py
Sprint 2 — Generador de datos aleatorios.

Genera pacientes ficticios con datos demográficos realistas y signos vitales
dentro de distribuciones fisiológicas. Simula la entrada de datos que en un
sistema real vendría de un monitor externo o de un registro de admisión.

Dependencias previas necesarias:
    - config.py                     (constantes, rangos normales)
    - modelos/paciente.py           (Paciente ABC)
    - modelos/paciente_sala.py      (PacienteSala)
    - modelos/paciente_emergencia.py (PacienteEmergencia)
    - modelos/signos_vitales.py     (SignosVitales)
    - modelos/historial.py          (HistorialMedico, Examen)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta

from config import (
    RANGOS_NORMALES,
    CANTIDAD_PACIENTES_SALA,
    CANTIDAD_PACIENTES_EMERGENCIA,
    SALAS_HOSPITAL,
    SALAS_GENERACION,
    PACIENTES_POR_SALA,
    VARIACION_MAXIMA_HR,
    VARIACION_MAXIMA_RR,
    VARIACION_MAXIMA_SPO,
    VARIACION_MAXIMA_PA,
    VARIACION_MAXIMA_TEMP,
)

from modelos.paciente_sala import PacienteSala
from modelos.paciente_emergencia import PacienteEmergencia
from modelos.signos_vitales import SignosVitales
from modelos.historial import HistorialMedico, Examen

from datos.condiciones import CONDICIONES

# ============================================================================
# DATOS BASE PARA GENERACIÓN DE PACIENTES FICTICIOS
# ============================================================================

# Nombres comunes en español para dar realismo a los pacientes generados
_NOMBRES_MASCULINOS = [
    "Carlos", "Miguel", "Alejandro", "José", "Francisco",
    "Juan", "Manuel", "Pedro", "Luis", "Jorge",
    "Ricardo", "Fernando", "Roberto", "Sergio", "Mario",
    "Alberto", "Rafael", "Antonio", "Eduardo", "Pablo",
    "Andrés", "Óscar", "Gabriel", "Héctor", "Daniel",
]

_NOMBRES_FEMENINOS = [
    "María", "Carmen", "Ana", "Isabel", "Laura",
    "Patricia", "Sofía", "Elena", "Marta", "Rosa",
    "Julia", "Valentina", "Lucía", "Adriana", "Natalia",
    "Beatriz", "Claudia", "Diana", "Gloria", "Paula",
    "Raquel", "Sara", "Teresa", "Verónica", "Silvia",
]

_APELLIDOS = [
    "García", "Rodríguez", "Martínez", "López", "Hernández",
    "González", "Pérez", "Sánchez", "Ramírez", "Torres",
    "Flores", "Rivera", "Morales", "Ortiz", "Cruz",
    "Vargas", "Mendoza", "Castillo", "Reyes", "Jiménez",
    "Silva", "Rojas", "Moreno", "Díaz", "Ruiz",
]

# Motivos de consulta típicos en emergencias
_MOTIVOS_CONSULTA = [
    "Dolor torácico",
    "Dificultad respiratoria",
    "Dolor abdominal agudo",
    "Traumatismo por caída",
    "Cefalea intensa",
    "Fiebre alta persistente",
    "Convulsiones",
    "Hemorragia",
    "Reacción alérgica severa",
    "Mareo y pérdida de conciencia",
    "Palpitaciones",
    "Dolor lumbar agudo",
    "Fractura sospechada",
    "Intoxicación alimentaria",
    "Quemadura",
    "Infección urinaria complicada",
    "Vómitos persistentes",
    "Descompensación diabética",
    "Crisis asmática",
    "Traumatismo craneoencefálico",
]

# Plantas / sectores del hospital para pacientes de sala
_PLANTAS = [
    "Medicina General",
    "Cardiología",
    "Neurología",
    "Traumatología",
    "Pediatría",
    "Oncología",
    "Cirugía General",
    "UCI",
    "Maternidad",
    "Nefrología",
]

# Tipos de exámenes comunes para poblar historiales
_TIPOS_EXAMENES = [
    "Hemograma completo",
    "Radiografía de tórax",
    "Electrocardiograma",
    "Tomografía computarizada",
    "Resonancia magnética",
    "Ecografía abdominal",
    "Prueba de función hepática",
    "Perfil lipídico",
    "Glicemia en ayunas",
    "Uroanálisis",
    "Gasometría arterial",
    "Prueba de coagulación",
    "Electrolitos séricos",
    "Radiografía de extremidades",
    "Ecocardiograma",
]

# Razones de ingreso típicas para pacientes de sala
_RAZONES_INGRESO_SALA = [
    "Postoperatorio de cirugía abdominal",
    "Neumonía adquirida en la comunidad",
    "Insuficiencia cardíaca congestiva",
    "Control de hipertensión arterial",
    "Enfermedad pulmonar obstructiva crónica",
    "Infección del tracto urinario complicada",
    "Accidente cerebrovascular en observación",
    "Diabetes mellitus descompensada",
    "Insuficiencia renal aguda",
    "Pancreatitis aguda",
    "Fractura de cadera postquirúrgica",
    "Endocarditis infecciosa",
    "Trombosis venosa profunda",
    "Anemia severa en estudio",
    "Síndrome coronario agudo",
]

# Doctores disponibles para asignación
_DOCTORES = [
    "Dr. Ricardo Fernandez",
    "Dra. Marta Silva",
    "Dr. Alejandro Torres",
    "Dra. Carmen Vega",
    "Dr. Luis Mendoza",
    "Dra. Patricia Rojas",
]


class GeneradorDatos:
    """
    Genera pacientes ficticios con datos demográficos y signos vitales
    realistas para alimentar la simulación del sistema hospitalario.

    Principio OOP — Encapsulamiento:
        Los datos base (listas de nombres, motivos, tipos de exámenes)
        y las funciones de generación están encapsulados dentro de esta
        clase. El resto del sistema solo llama a los métodos públicos
        sin conocer los detalles de la generación aleatoria.
    """

    def __init__(self, semilla: int = None):
        """
        Constructor del generador.

        Args:
            semilla: Semilla opcional para el generador aleatorio.
                     Si se proporciona, los datos generados serán
                     reproducibles (útil para pruebas).
        """
        if semilla is not None:
            random.seed(semilla)

    # ==================================================================
    # GENERACIÓN DE DATOS DEMOGRÁFICOS
    # ==================================================================

    def generar_nombre_completo(self) -> tuple[str, str, str]:
        """
        Genera un nombre, apellido y género aleatorios.

        Returns:
            Tupla (nombre, apellido, genero) donde genero es
            "Masculino" o "Femenino".
        """
        if random.choice([True, False]):
            nombre = random.choice(_NOMBRES_MASCULINOS)
            apellido = random.choice(_APELLIDOS)
            genero = "Masculino"
        else:
            nombre = random.choice(_NOMBRES_FEMENINOS)
            apellido = random.choice(_APELLIDOS)
            genero = "Femenino"

        # Posibilidad de apellido compuesto (30 % de probabilidad)
        if random.random() < 0.3:
            apellido += " " + random.choice(_APELLIDOS)

        nombre_completo = f"{nombre} {apellido}"
        return nombre_completo, genero, nombre

    def generar_edad(self) -> int:
        """
        Genera una edad aleatoria con distribución realista para un hospital.

        La distribución favorece a pacientes mayores de 40 años
        (más frecuentes en entornos hospitalarios), pero incluye
        todos los rangos etarios.

        Returns:
            Edad en años (entre 0 y 100).
        """
        # Usamos una distribución por rangos ponderados:
        #  - 0-12 (pediátrico): 10 %
        #  - 13-25 (joven):      10 %
        #  - 26-40 (adulto joven): 15 %
        #  - 41-60 (adulto):      25 %
        #  - 61-80 (adulto mayor): 30 %
        #  - 81-100 (anciano):    10 %
        rango = random.choices(
            population=[(0, 12), (13, 25), (26, 40), (41, 60), (61, 80), (81, 100)],
            weights=[10, 10, 15, 25, 30, 10],
            k=1,
        )[0]
        return random.randint(rango[0], rango[1])

    def _determinar_avatar(self, edad: int, genero: str) -> str:
        """
        Determina el tipo de avatar según la edad y el género del paciente.

        Reglas:
            -  0-12 años:  nino / nina
            - 13-59 años:  hombre / mujer
            - 60+ años:    anciano / anciana

        Args:
            edad:   Edad del paciente.
            genero: "Masculino" o "Femenino".

        Returns:
            Clave de avatar válida para ICONOS_AVATAR.
        """
        if edad < 13:
            return "nino" if genero == "Masculino" else "nina"
        elif edad < 60:
            return "hombre" if genero == "Masculino" else "mujer"
        else:
            return "anciano" if genero == "Masculino" else "anciana"

    # ==================================================================
    # GENERACIÓN DE SIGNOS VITALES ALEATORIOS
    # ==================================================================

    def generar_signos_vitales(
        self,
        nivel_alteracion: str = "aleatorio",
    ) -> SignosVitales:
        """
        Genera signos vitales aleatorios con distribución normal centrada
        en el punto medio de cada rango fisiológico.

        Args:
            nivel_alteracion: Controla el grado de anormalidad de los signos.
                - "aleatorio":  La mayoría serán normales, algunos alterados.
                - "normal":     Todos los signos dentro de rangos normales.
                - "basico":     Signos levemente fuera de rango.
                - "prudente":   Signos moderadamente fuera de rango.
                - "critico":    Signos severamente alterados.
                - "fallecido":  Todos los signos en cero.

        Returns:
            Instancia de SignosVitales con valores generados.
        """
        if nivel_alteracion == "fallecido":
            return SignosVitales()  # Todo en cero

        # Probabilidad base de que un signo esté alterado
        if nivel_alteracion == "normal":
            prob_alteracion = 0.0
            factor_desviacion = None
        elif nivel_alteracion == "basico":
            prob_alteracion = 1.0
            factor_desviacion = 1.0   # Desviación leve
        elif nivel_alteracion == "prudente":
            prob_alteracion = 1.0
            factor_desviacion = 2.0   # Desviación moderada
        elif nivel_alteracion == "critico":
            prob_alteracion = 1.0
            factor_desviacion = 3.5   # Desviación severa
        else:  # "aleatorio"
            prob_alteracion = 0.08   # 8 % por signo → la mayoría quedan ESTABLE
            factor_desviacion = None  # Se determina por signo

        return SignosVitales(
            frecuencia_cardiaca=self._generar_signo(
                "frecuencia_cardiaca", prob_alteracion, factor_desviacion
            ),
            frecuencia_respiratoria=self._generar_signo(
                "frecuencia_respiratoria", prob_alteracion, factor_desviacion
            ),
            saturacion_oxigeno=self._generar_signo(
                "saturacion_oxigeno", prob_alteracion, factor_desviacion
            ),
            presion_sistolica=self._generar_signo(
                "presion_sistolica", prob_alteracion, factor_desviacion
            ),
            presion_diastolica=self._generar_signo(
                "presion_diastolica", prob_alteracion, factor_desviacion
            ),
            temperatura=self._generar_signo(
                "temperatura", prob_alteracion, factor_desviacion
            ),
        )

    def _generar_signo(
        self,
        nombre_signo: str,
        prob_alteracion: float,
        factor_desviacion: float = None,
    ) -> float:
        """
        Genera un valor aleatorio para un signo vital específico usando
        distribución normal (gaussiana) centrada en el punto medio del
        rango normal.

        Args:
            nombre_signo:      Clave del signo vital (ej. "frecuencia_cardiaca").
            prob_alteracion:   Probabilidad de que el valor salga del rango normal.
            factor_desviacion: Cuántas desviaciones estándar forzar si está alterado.
                               None = aleatorio entre 1.0 y 3.5.

        Returns:
            Valor del signo vital redondeado a 1 decimal.
        """
        minimo, maximo = RANGOS_NORMALES[nombre_signo]
        media = (minimo + maximo) / 2.0

        # La desviación estándar es ~1/6 del rango para que el 99.7 %
        # de los valores caigan dentro del rango normal en una distribución
        # normal (regla 68-95-99.7 con sigma = rango/6).
        sigma = (maximo - minimo) / 6.0

        # Determinamos si este signo estará alterado
        alterado = random.random() < prob_alteracion

        if alterado:
            # Forzamos el valor fuera del rango normal
            if factor_desviacion is None:
                factor = random.uniform(0.5, 1.8)  # Desviación leve a moderada
            else:
                factor = factor_desviacion

            # Elegimos si el valor será anormalmente bajo o alto
            if random.choice([True, False]):
                valor = minimo - (sigma * factor)  # Por debajo del mínimo
            else:
                valor = maximo + (sigma * factor)  # Por encima del máximo
        else:
            # Valor dentro del rango normal (distribución gaussiana)
            valor = random.gauss(media, sigma)

        # Ajustamos a límites fisiológicos razonables
        valor = self._acotar_valor(nombre_signo, valor)

        if nombre_signo == "temperatura":
            return round(valor, 1)
        return round(valor)

    def _acotar_valor(self, nombre_signo: str, valor: float) -> float:
        """
        Acota un valor de signo vital a límites fisiológicos plausibles.
        Evita valores absurdos como HR = 800 o temperatura = -10.
        """
        limites_fisicos = {
            "frecuencia_cardiaca":     (0.0, 350.0),
            "frecuencia_respiratoria": (0.0, 80.0),
            "saturacion_oxigeno":      (0.0, 100.0),
            "presion_sistolica":       (0.0, 300.0),
            "presion_diastolica":      (0.0, 200.0),
            "temperatura":             (20.0, 45.0),
        }
        vmin, vmax = limites_fisicos[nombre_signo]
        return max(vmin, min(vmax, valor))

    # ==================================================================
    # SELECCIÓN DE CONDICIÓN CLÍNICA COHERENTE
    # ==================================================================

    def _seleccionar_condicion(self, edad: int, genero: str) -> dict:
        """
        Selecciona una condición clínica coherente del catálogo CONDICIONES,
        filtrando por edad y sexo del paciente.

        Args:
            edad:   Edad del paciente.
            genero: "Masculino" o "Femenino".

        Returns:
            Diccionario con la condición clínica seleccionada.
        """
        sexo_cond = "femenino" if genero == "Femenino" else "masculino"
        candidatas = [
            c for c in CONDICIONES
            if c["edad_min"] <= edad <= c["edad_max"]
            and c["sexo"] in ("ambos", sexo_cond)
        ]
        if not candidatas:
            candidatas = [c for c in CONDICIONES if c["sexo"] == "ambos"]
        return random.choice(candidatas)

    def generar_signos_condicion(self, condicion: dict) -> SignosVitales:
        """
        Genera signos vitales dentro de los rangos típicos de una condición
        clínica específica, usando distribución gaussiana centrada en el
        punto medio del rango de la condición. Los valores se acotan a los
        límites de variación de sala para que nunca partan en ATENCIÓN.

        Args:
            condicion: Diccionario de condición con clave "signos".

        Returns:
            Instancia de SignosVitales con valores coherentes a la condición.
        """
        from config import LIMITES_VARIACION_SALA
        rangos = condicion["signos"]
        limites = LIMITES_VARIACION_SALA
        return SignosVitales(
            frecuencia_cardiaca=self._generar_en_rango(
                *rangos["frecuencia_cardiaca"],
                vmin_lim=limites["frecuencia_cardiaca"][0],
                vmax_lim=limites["frecuencia_cardiaca"][1],
            ),
            frecuencia_respiratoria=self._generar_en_rango(
                *rangos["frecuencia_respiratoria"],
                vmin_lim=limites["frecuencia_respiratoria"][0],
                vmax_lim=limites["frecuencia_respiratoria"][1],
            ),
            saturacion_oxigeno=self._generar_en_rango(
                *rangos["saturacion_oxigeno"],
                vmin_lim=limites["saturacion_oxigeno"][0],
                vmax_lim=limites["saturacion_oxigeno"][1],
            ),
            presion_sistolica=self._generar_en_rango(
                *rangos["presion_sistolica"],
                vmin_lim=limites["presion_sistolica"][0],
                vmax_lim=limites["presion_sistolica"][1],
            ),
            presion_diastolica=self._generar_en_rango(
                *rangos["presion_diastolica"],
                vmin_lim=limites["presion_diastolica"][0],
                vmax_lim=limites["presion_diastolica"][1],
            ),
            temperatura=self._generar_en_rango(
                *rangos["temperatura"],
                vmin_lim=limites["temperatura"][0],
                vmax_lim=limites["temperatura"][1],
            ),
        )

    def _generar_en_rango(
        self, vmin: float, vmax: float,
        vmin_lim: float = None, vmax_lim: float = None,
    ) -> float:
        """
        Genera un valor aleatorio dentro de un rango usando distribución
        gaussiana centrada en el punto medio. Opcionalmente acota el
        resultado a límites externos.

        Args:
            vmin: Valor mínimo del rango.
            vmax: Valor máximo del rango.
            vmin_lim: Límite inferior de acotación (opcional).
            vmax_lim: Límite superior de acotación (opcional).

        Returns:
            Valor aleatorio dentro del rango.
        """
        media = (vmin + vmax) / 2.0
        sigma = (vmax - vmin) / 6.0
        valor = random.gauss(media, sigma)
        valor = max(vmin, min(vmax, valor))
        if vmin_lim is not None:
            valor = max(vmin_lim, valor)
        if vmax_lim is not None:
            valor = min(vmax_lim, valor)
        return round(valor, 1)

    # ==================================================================
    # GENERACIÓN DE HISTORIAL MÉDICO FICTICIO (LEGACY)
    # ==================================================================

    def generar_historial(
        self, id_paciente: str, condicion: dict = None
    ) -> HistorialMedico:
        """
        Genera un historial médico con datos coherentes.

        Si se proporciona 'condicion', los exámenes, diagnósticos,
        tratamientos y medicamentos serán tomados del catálogo de
        condiciones clínicas, garantizando coherencia diagnóstica.

        Si condicion es None, se usa el generador aleatorio legacy.

        Args:
            id_paciente: ID del paciente al que pertenece el historial.
            condicion:   Diccionario de condición clínica (opcional).

        Returns:
            Instancia de HistorialMedico poblada.
        """
        historial = HistorialMedico(id_paciente=id_paciente)

        if condicion is not None:
            autor = random.choice([
                "Dr. Ricardo Fernandez", "Dra. Marta Silva",
                "Dr. Alejandro Torres",
            ])
            # Exámenes coherentes con la condición
            for tipo_examen, resultado_examen in condicion["examenes"]:
                dias_atras = random.randint(1, 30)
                historial.agregar_examen(Examen(
                    tipo=tipo_examen,
                    resultado=resultado_examen,
                    fecha=datetime.now() - timedelta(days=dias_atras),
                ))
            # Diagnóstico coherente con la condición
            historial.agregar_diagnostico(
                descripcion=condicion["diagnostico"],
                autor=autor,
                fecha=datetime.now() - timedelta(days=random.randint(1, 10)),
            )
            # Tratamientos coherentes con la condición
            for tratamiento in condicion["tratamientos"]:
                historial.agregar_tratamiento(
                    descripcion=tratamiento,
                    autor=autor,
                    fecha=datetime.now() - timedelta(days=random.randint(1, 7)),
                )
            # Medicamentos coherentes con la condición
            for medicamento in condicion["medicamentos"]:
                historial.agregar_medicamento(
                    descripcion=medicamento,
                    autor=autor,
                    fecha=datetime.now() - timedelta(days=random.randint(1, 5)),
                )
            return historial

        # Fallback: generación aleatoria legacy
        num_examenes = random.randint(1, 4)
        for _ in range(num_examenes):
            tipo_examen = random.choice(_TIPOS_EXAMENES)
            resultado = random.choice(
                ["Normal", "Normal", "Normal", "Normal", "Leve alteración",
                 "Dentro de parámetros", "Sin hallazgos patológicos"]
            )
            dias_atras = random.randint(1, 90)
            historial.agregar_examen(Examen(
                tipo=tipo_examen, resultado=resultado,
                fecha=datetime.now() - timedelta(days=dias_atras),
            ))

        num_diag = random.randint(0, 2)
        diagnosticos_ficticios = [
            "Hipertensión arterial esencial",
            "Diabetes mellitus tipo 2",
            "Infección respiratoria alta",
            "Lumbalgia mecánica",
            "Gastritis crónica",
            "Colesterol elevado",
            "Asma bronquial",
            "Artrosis de rodilla",
        ]
        for _ in range(num_diag):
            dias_atras = random.randint(1, 365)
            historial.agregar_diagnostico(
                descripcion=random.choice(diagnosticos_ficticios),
                autor=random.choice([
                    "Dr. Ricardo Fernandez",
                    "Dra. Marta Silva",
                    "Dr. Alejandro Torres",
                ]),
                fecha=datetime.now() - timedelta(days=dias_atras),
            )

        num_trat = random.randint(0, 2)
        tratamientos_ficticios = [
            "Enalapril 10mg cada 24h",
            "Metformina 850mg cada 12h",
            "Paracetamol 500mg cada 8h por 5 días",
            "Ibuprofeno 400mg cada 8h",
            "Omeprazol 20mg en ayunas",
            "Amoxicilina 500mg cada 8h por 7 días",
            "Salbutamol inhalador 2 puff cada 6h",
            "Atorvastatina 20mg cada 24h",
        ]
        for _ in range(num_trat):
            dias_atras = random.randint(1, 365)
            historial.agregar_tratamiento(
                descripcion=random.choice(tratamientos_ficticios),
                autor=random.choice([
                    "Dr. Ricardo Fernandez",
                    "Dra. Marta Silva",
                ]),
                fecha=datetime.now() - timedelta(days=dias_atras),
            )

        return historial

    # ==================================================================
    # GENERACIÓN DE PACIENTES COMPLETOS
    # ==================================================================

    def generar_paciente_sala(
        self, sala_info: dict = None, num_cama: int = None
    ) -> PacienteSala:
        """
        Genera un paciente de sala completo con datos demográficos,
        signos vitales e historial médico coherentes entre sí, basados
        en una condición clínica seleccionada según edad y sexo.

        Args:
            sala_info: Diccionario con datos de la sala (nombre, camas_inicio, color).
                       Si es None, se asigna una sala y cama aleatoria.
            num_cama:  Número de cama específico. Si es None, se genera aleatorio.

        Returns:
            Instancia de PacienteSala lista para usar en la simulación.
        """
        nombre, genero, _ = self.generar_nombre_completo()
        edad = self.generar_edad()
        avatar = self._determinar_avatar(edad, genero)

        # Seleccionar condición clínica coherente con edad y sexo
        condicion = self._seleccionar_condicion(edad, genero)

        if sala_info is not None:
            planta = sala_info["nombre"]
            if num_cama is None:
                num_cama = random.randint(
                    sala_info["camas_inicio"],
                    sala_info["camas_inicio"] + 10,
                )
        else:
            planta = random.choice(_PLANTAS)
            if num_cama is None:
                num_cama = random.randint(100, 599)

        paciente = PacienteSala(
            nombre=nombre,
            edad=edad,
            genero=genero,
            numero_cama=num_cama,
            planta=planta,
            tipo_avatar=avatar,
            razon_ingreso=condicion["razon_ingreso"],
            doctor_asignado=random.choice(_DOCTORES),
        )

        # Simular que el paciente ya lleva tiempo internado (1 a 48 horas)
        # DEBE ir ANTES de asignar signos_vitales porque el setter de
        # signos_vitales llama a actualizar_estado(), que usa _fecha_ingreso.
        horas_atras = random.uniform(1, 48)
        paciente._fecha_ingreso = datetime.now() - timedelta(hours=horas_atras)

        # Asignar signos vitales coherentes con la condición
        paciente.signos_vitales = self.generar_signos_condicion(condicion)

        # Generar historial médico coherente con la condición
        paciente.historial = self.generar_historial(
            paciente.id_paciente, condicion
        )

        return paciente

    def generar_paciente_emergencia(self) -> PacienteEmergencia:
        """
        Genera un paciente de emergencias completo con datos demográficos,
        signos vitales, prioridad administrativa y motivo de consulta.

        Returns:
            Instancia de PacienteEmergencia lista para usar en la simulación.
        """
        nombre, genero, _ = self.generar_nombre_completo()
        edad = self.generar_edad()
        avatar = self._determinar_avatar(edad, genero)

        # La prioridad administrativa se asigna con distribución ponderada:
        # la mayoría son prioridades 2-4, pocos son 1 o 5.
        prioridad = random.choices(
            population=[1, 2, 3, 4, 5],
            weights=[5, 25, 40, 20, 10],  # 5 %, 25 %, 40 %, 20 %, 10 %
            k=1,
        )[0]

        motivo = random.choice(_MOTIVOS_CONSULTA)
        paciente = PacienteEmergencia(
            nombre=nombre,
            edad=edad,
            genero=genero,
            prioridad_administrativa=prioridad,
            motivo_consulta=motivo,
            tipo_avatar=avatar,
            razon_ingreso=motivo,
            doctor_asignado=random.choice(_DOCTORES),
        )

        # Asignar signos vitales con distribución aleatoria realista
        paciente.signos_vitales = self.generar_signos_vitales()

        # Los pacientes de emergencia también pueden tener historial previo
        paciente.historial = self.generar_historial(paciente.id_paciente)

        return paciente

    def generar_pacientes_sala(self, cantidad: int = None) -> list[PacienteSala]:
        """
        Genera pacientes de sala distribuidos equitativamente entre las
        salas de generación inicial (A, B, C, D). Las salas E y F quedan
        vacías para recibir transferidos desde emergencias.

        Args:
            cantidad: Número total de pacientes a generar.
                      Si no se especifica, usa CANTIDAD_PACIENTES_SALA de config
                      (24 pacientes = 4 salas × 6 pacientes).

        Returns:
            Lista de instancias de PacienteSala.
        """
        if cantidad is None:
            cantidad = CANTIDAD_PACIENTES_SALA

        pacientes = []
        pacientes_por_sala = cantidad // len(SALAS_GENERACION)

        for sala in SALAS_GENERACION:
            for i in range(pacientes_por_sala):
                num_cama = sala["camas_inicio"] + i
                paciente = self.generar_paciente_sala(
                    sala_info=sala, num_cama=num_cama
                )
                pacientes.append(paciente)

        # Si sobra algún paciente (cantidad no divisible), asignarlos a la última sala
        sobrantes = cantidad - len(pacientes)
        for i in range(sobrantes):
            sala = SALAS_GENERACION[-1]
            num_cama = sala["camas_inicio"] + pacientes_por_sala + i
            paciente = self.generar_paciente_sala(
                sala_info=sala, num_cama=num_cama
            )
            pacientes.append(paciente)

        return pacientes

    def generar_pacientes_emergencia(
        self, cantidad: int = None
    ) -> list[PacienteEmergencia]:
        """
        Genera una lista de pacientes de emergencias.

        Args:
            cantidad: Número de pacientes a generar.
                      Si no se especifica, usa CANTIDAD_PACIENTES_EMERGENCIA
                      de config.

        Returns:
            Lista de instancias de PacienteEmergencia.
        """
        if cantidad is None:
            cantidad = CANTIDAD_PACIENTES_EMERGENCIA
        return [self.generar_paciente_emergencia() for _ in range(cantidad)]


# ============================================================================
# BLOQUE DE PRUEBA DEL MÓDULO
# ============================================================================
if __name__ == "__main__":
    """
    Prueba aislada del módulo GeneradorDatos.
    Demuestra:
      1. Generación de datos demográficos (nombre, edad, género, avatar).
      2. Generación de signos vitales con distintos niveles de alteración.
      3. Generación de historial médico ficticio.
      4. Generación de un paciente de sala completo.
      5. Generación de un paciente de emergencias completo.
      6. Generación por lotes (listas de pacientes).
      7. Reproducibilidad con semilla fija.
      8. Distribución de estados en un lote de pacientes.
    """
    print("=" * 60)
    print("  PRUEBA DEL MÓDULO: GeneradorDatos")
    print("=" * 60)

    generador = GeneradorDatos(semilla=42)

    # --- Prueba 1: Generar datos demográficos ---
    print("\n[1] Generar 3 nombres, edades y avatares:")
    for i in range(3):
        nombre, genero, _ = generador.generar_nombre_completo()
        edad = generador.generar_edad()
        avatar = generador._determinar_avatar(edad, genero)
        print(f"    {nombre} | {edad} años | {genero} | avatar: {avatar}")

    # --- Prueba 2: Signos vitales con distintos niveles ---
    print("\n[2] Generar signos vitales con distintos niveles de alteración:")
    for nivel in ["normal", "basico", "prudente", "critico", "fallecido"]:
        signos = generador.generar_signos_vitales(nivel_alteracion=nivel)
        estado = signos.obtener_estado_global()
        print(f"    Nivel '{nivel}':")
        print(f"      HR={signos.frecuencia_cardiaca}, "
              f"RR={signos.frecuencia_respiratoria}, "
              f"SpO2={signos.saturacion_oxigeno}, "
              f"PA={signos.obtener_presion_arterial()}, "
              f"Temp={signos.temperatura}")
        print(f"      -> Estado global: {estado}")

    # --- Prueba 3: Signos aleatorios (el caso más usado) ---
    print("\n[3] Generar 3 conjuntos de signos aleatorios:")
    for i in range(3):
        signos = generador.generar_signos_vitales()
        print(f"    #{i+1} -> Estado: {signos.obtener_estado_global()}")

    # --- Prueba 4: Generar historial médico ---
    print("\n[4] Generar historial médico ficticio:")
    historial = generador.generar_historial("PAC-TEST")
    print(f"    Exámenes:     {historial.total_examenes()}")
    print(f"    Diagnósticos: {historial.total_diagnosticos()}")
    print(f"    Tratamientos: {historial.total_tratamientos()}")
    print(f"    Total:        {len(historial)} registros")

    # --- Prueba 5: Generar paciente de sala completo ---
    print("\n[5] Paciente de sala generado automáticamente:")
    paciente_sala = generador.generar_paciente_sala()
    print(paciente_sala)

    # --- Prueba 6: Generar paciente de emergencias completo ---
    print("\n[6] Paciente de emergencias generado automáticamente:")
    paciente_emerg = generador.generar_paciente_emergencia()
    print(paciente_emerg)

    # --- Prueba 7: Generar lote de pacientes de sala ---
    print("\n[7] Generar lote de 8 pacientes de sala:")
    pacientes_sala = generador.generar_pacientes_sala(cantidad=8)
    print(f"    Total generados: {len(pacientes_sala)}")
    for p in pacientes_sala:
        print(f"    {p.id_paciente} | {p.nombre:<30} | {p.estado} | Cama {p.numero_cama}")

    # --- Prueba 8: Distribución de estados en un lote grande ---
    print("\n[8] Distribución de estados en lote de 50 pacientes de emergencias:")
    generador2 = GeneradorDatos(semilla=123)
    pacientes_emerg = generador2.generar_pacientes_emergencia(cantidad=50)
    conteo_estados = {}
    for p in pacientes_emerg:
        conteo_estados[p.estado] = conteo_estados.get(p.estado, 0) + 1
    for estado, cantidad in sorted(conteo_estados.items()):
        barra = "#" * cantidad
        print(f"    {estado:<15} {cantidad:>2} {barra}")

    # --- Prueba 9: Reproducibilidad con semilla ---
    print("\n[9] Reproducibilidad (misma semilla = mismos datos):")
    # Reiniciamos la semilla antes de cada generación para garantizar
    # que la secuencia aleatoria sea idéntica.
    generador_a = GeneradorDatos(semilla=777)
    p_a = generador_a.generar_paciente_sala()
    print(f"    Semilla 777 - primera generacion: {p_a.nombre} | {p_a.edad} años | {p_a.estado}")

    # Volvemos a fijar la semilla al mismo valor para repetir la secuencia
    generador_b = GeneradorDatos(semilla=777)
    p_b = generador_b.generar_paciente_sala()
    print(f"    Semilla 777 - segunda generacion: {p_b.nombre} | {p_b.edad} años | {p_b.estado}")
    print(f"    Nombre identico: {'Si' if p_a.nombre == p_b.nombre else 'No'}")
    print(f"    Edad identica:   {'Si' if p_a.edad == p_b.edad else 'No'}")
    print(f"    Estado identico: {'Si' if p_a.estado == p_b.estado else 'No'}")

    # --- Prueba 10: Resumen de un paciente generado ---
    print(f"\n[10] Resumen (dict) de paciente generado:")
    resumen = paciente_emerg.resumen()
    for clave, valor in resumen.items():
        if clave == "signos":
            print(f"    {clave}: (dict con {len(valor)} signos)")
        else:
            print(f"    {clave}: {valor}")

    print("\n[OK] Pruebas de GeneradorDatos completadas.\n")
