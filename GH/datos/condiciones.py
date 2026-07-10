"""
Módulo: condiciones.py
Sprint 7 — Base de datos de condiciones clínicas coherentes.

Define CONDICIONES, un catálogo de escenarios clínicos que vinculan de forma
coherente: razón de ingreso, diagnóstico, exámenes, tratamientos, medicamentos
y rangos típicos de signos vitales. Cada condición respeta restricciones de
sexo y grupo etario para evitar inconsistencias clínicas.

Usado exclusivamente por GeneradorDatos para el área de hospitalización (sala).
"""

# ============================================================================
# ESTRUCTURA DE CADA CONDICIÓN
# ============================================================================
# Cada entrada es un dict con las siguientes claves:
#
#   razon_ingreso   (str)      Motivo de ingreso al hospital.
#   diagnostico     (str)      Diagnóstico médico.
#   examenes        (list)     Lista de tuplas (tipo, resultado).
#   tratamientos    (list)     Lista de strings con abordajes terapéuticos.
#   medicamentos    (list)     Lista de strings con fármacos y dosis reales.
#   signos          (dict)     Rangos (min, max) para cada signo vital.
#   edad_min        (int)      Edad mínima para esta condición.
#   edad_max        (int)      Edad máxima para esta condición.
#   sexo            (str)      "ambos", "masculino" o "femenino".
#
# Dosis de medicamentos basadas en presentaciones farmacéuticas reales:
#   Paracetamol 500 mg, Ibuprofeno 400/600 mg, Metformina 850 mg,
#   Enalapril 10/20 mg, Losartán 50 mg, Amlodipino 5 mg, etc.
# ============================================================================

CONDICIONES = [
    # ========================================================================
    # 1. NEUMONÍA
    # ========================================================================
    {
        "razon_ingreso": "Neumonía adquirida en la comunidad",
        "diagnostico": "Neumonía bacteriana",
        "examenes": [
            ("Hemograma completo", "Leucocitosis con desviación a la izquierda"),
            ("Proteína C reactiva", "Elevada: 120 mg/L"),
            ("Radiografía de tórax", "Consolidación en lóbulo inferior derecho"),
            ("Cultivo de esputo", "Streptococcus pneumoniae aislado"),
        ],
        "tratamientos": [
            "Antibioticoterapia intravenosa",
            "Hidratación parenteral con solución salina",
            "Oxigenoterapia por cánula nasal a 2 L/min",
        ],
        "medicamentos": [
            "Ceftriaxona 1 g IV cada 12 horas",
            "Azitromicina 500 mg VO cada 24 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (90, 110),
            "frecuencia_respiratoria": (20, 28),
            "saturacion_oxigeno": (88, 94),
            "presion_sistolica": (100, 130),
            "presion_diastolica": (60, 80),
            "temperatura": (37.8, 39.0),
        },
        "edad_min": 18,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 2. PIELONEFRITIS AGUDA
    # ========================================================================
    {
        "razon_ingreso": "Infección urinaria febril",
        "diagnostico": "Pielonefritis aguda",
        "examenes": [
            ("Hemograma completo", "Leucocitosis marcada"),
            ("Uroanálisis", "Piuria, bacteriuria, nitritos positivos"),
            ("Urocultivo", "Escherichia coli >100,000 UFC/mL"),
            ("Creatinina sérica", "1.1 mg/dL, dentro de parámetros"),
        ],
        "tratamientos": [
            "Antibioticoterapia intravenosa",
            "Hidratación parenteral con solución salina 0.9%",
        ],
        "medicamentos": [
            "Ceftriaxona 1 g IV cada 12 horas",
            "Ciprofloxacino 500 mg VO cada 12 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (95, 115),
            "frecuencia_respiratoria": (18, 24),
            "saturacion_oxigeno": (94, 99),
            "presion_sistolica": (100, 125),
            "presion_diastolica": (60, 78),
            "temperatura": (38.0, 39.5),
        },
        "edad_min": 18,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 3. DIABETES TIPO 2 DESCOMPENSADA
    # ========================================================================
    {
        "razon_ingreso": "Hiperglicemia persistente",
        "diagnostico": "Diabetes mellitus tipo 2 descompensada",
        "examenes": [
            ("Glucosa sérica", "285 mg/dL en ayunas"),
            ("Hemoglobina glicosilada (HbA1c)", "9.8%"),
            ("Electrolitos séricos", "Sodio 138, Potasio 4.1, dentro de parámetros"),
            ("Creatinina sérica", "1.0 mg/dL"),
        ],
        "tratamientos": [
            "Control glucémico con insulina de acción rápida",
            "Hidratación parenteral",
            "Plan de educación diabetológica",
        ],
        "medicamentos": [
            "Insulina regular según esquema móvil",
            "Metformina 850 mg VO cada 12 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (75, 95),
            "frecuencia_respiratoria": (16, 22),
            "saturacion_oxigeno": (95, 99),
            "presion_sistolica": (110, 140),
            "presion_diastolica": (65, 85),
            "temperatura": (36.5, 37.3),
        },
        "edad_min": 30,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 4. APENDICITIS POSTOPERATORIA
    # ========================================================================
    {
        "razon_ingreso": "Dolor abdominal postoperatorio",
        "diagnostico": "Apendicitis aguda postoperatoria",
        "examenes": [
            ("Hemograma completo", "Leucocitos en descenso, evolución favorable"),
            ("Proteína C reactiva", "En descenso: 45 mg/L"),
            ("Ecografía abdominal", "Sin líquido libre, lecho quirúrgico normal"),
        ],
        "tratamientos": [
            "Control postquirúrgico y analgesia",
            "Deambulación temprana",
            "Dieta líquida progresiva a blanda",
        ],
        "medicamentos": [
            "Cefazolina 1 g IV cada 8 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (70, 90),
            "frecuencia_respiratoria": (14, 20),
            "saturacion_oxigeno": (96, 100),
            "presion_sistolica": (105, 125),
            "presion_diastolica": (65, 80),
            "temperatura": (36.5, 37.5),
        },
        "edad_min": 10,
        "edad_max": 60,
        "sexo": "ambos",
    },

    # ========================================================================
    # 5. HIPERTENSIÓN ARTERIAL NO CONTROLADA
    # ========================================================================
    {
        "razon_ingreso": "Crisis hipertensiva controlada",
        "diagnostico": "Hipertensión arterial no controlada",
        "examenes": [
            ("Electrocardiograma", "Ritmo sinusal, sin signos de isquemia aguda"),
            ("Creatinina sérica", "1.2 mg/dL"),
            ("Electrolitos séricos", "Sodio 140, Potasio 3.9, dentro de parámetros"),
        ],
        "tratamientos": [
            "Ajuste de antihipertensivos",
            "Monitorización de presión arterial cada 4 horas",
            "Restricción de sodio en dieta",
        ],
        "medicamentos": [
            "Losartán 50 mg VO cada 12 horas",
            "Amlodipino 5 mg VO cada 24 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (70, 88),
            "frecuencia_respiratoria": (14, 20),
            "saturacion_oxigeno": (96, 100),
            "presion_sistolica": (140, 165),
            "presion_diastolica": (85, 100),
            "temperatura": (36.5, 37.2),
        },
        "edad_min": 40,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 6. ANGINA ESTABLE
    # ========================================================================
    {
        "razon_ingreso": "Dolor torácico estable",
        "diagnostico": "Angina estable",
        "examenes": [
            ("Electrocardiograma", "Ritmo sinusal, sin elevación del segmento ST"),
            ("Troponinas", "Negativas, dentro de rango normal"),
            ("Perfil lipídico", "Colesterol total 240, LDL 160, HDL 38"),
        ],
        "tratamientos": [
            "Observación y tratamiento médico",
            "Reposo relativo en cama",
            "Control de factores de riesgo cardiovascular",
        ],
        "medicamentos": [
            "Ácido acetilsalicílico 100 mg VO cada 24 horas",
            "Atorvastatina 20 mg VO cada 24 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (65, 85),
            "frecuencia_respiratoria": (14, 18),
            "saturacion_oxigeno": (96, 100),
            "presion_sistolica": (120, 145),
            "presion_diastolica": (70, 88),
            "temperatura": (36.5, 37.0),
        },
        "edad_min": 45,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 7. EPOC EXACERBADO
    # ========================================================================
    {
        "razon_ingreso": "Exacerbación respiratoria",
        "diagnostico": "EPOC exacerbado",
        "examenes": [
            ("Hemograma completo", "Leucocitosis leve, sin anemia"),
            ("Gasometría arterial", "PaO2 58 mmHg, PaCO2 48 mmHg, acidosis respiratoria leve"),
            ("Radiografía de tórax", "Hiperinsuflación pulmonar, sin condensación"),
        ],
        "tratamientos": [
            "Broncodilatadores y corticoides",
            "Oxigenoterapia controlada a 1-2 L/min",
            "Fisioterapia respiratoria",
        ],
        "medicamentos": [
            "Salbutamol 100 mcg/dosis inhalador cada 6 horas",
            "Ipratropio 20 mcg/dosis inhalador cada 6 horas",
            "Prednisona 20 mg VO cada 12 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (88, 105),
            "frecuencia_respiratoria": (20, 28),
            "saturacion_oxigeno": (87, 93),
            "presion_sistolica": (110, 135),
            "presion_diastolica": (65, 82),
            "temperatura": (36.8, 38.0),
        },
        "edad_min": 50,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 8. ASMA BRONQUIAL
    # ========================================================================
    {
        "razon_ingreso": "Crisis asmática controlada",
        "diagnostico": "Asma bronquial",
        "examenes": [
            ("Hemograma completo", "Eosinofilia leve, resto normal"),
            ("Gasometría arterial", "PaO2 65 mmHg, PaCO2 35 mmHg"),
            ("Espirometría", "VEF1 65% del predicho, reversible con broncodilatador"),
        ],
        "tratamientos": [
            "Nebulizaciones con broncodilatadores",
            "Corticoides inhalados",
            "Oxigenoterapia suplementaria si requiere",
        ],
        "medicamentos": [
            "Salbutamol 100 mcg/dosis inhalador cada 6 horas",
            "Budesonida 200 mcg/dosis inhalador cada 12 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (85, 105),
            "frecuencia_respiratoria": (18, 26),
            "saturacion_oxigeno": (90, 95),
            "presion_sistolica": (105, 125),
            "presion_diastolica": (65, 80),
            "temperatura": (36.5, 37.2),
        },
        "edad_min": 5,
        "edad_max": 55,
        "sexo": "ambos",
    },

    # ========================================================================
    # 9. CELULITIS BACTERIANA
    # ========================================================================
    {
        "razon_ingreso": "Celulitis de miembro inferior",
        "diagnostico": "Celulitis bacteriana",
        "examenes": [
            ("Hemograma completo", "Leucocitosis con neutrofilia"),
            ("Proteína C reactiva", "Elevada: 85 mg/L"),
            ("Cultivo de secreción", "Staphylococcus aureus meticilino-sensible"),
        ],
        "tratamientos": [
            "Antibioticoterapia intravenosa",
            "Curaciones diarias de la zona afectada",
            "Elevación del miembro afectado",
        ],
        "medicamentos": [
            "Cefazolina 1 g IV cada 8 horas",
            "Clindamicina 600 mg IV cada 8 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (80, 100),
            "frecuencia_respiratoria": (16, 22),
            "saturacion_oxigeno": (95, 99),
            "presion_sistolica": (108, 130),
            "presion_diastolica": (65, 80),
            "temperatura": (37.5, 38.5),
        },
        "edad_min": 18,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 10. GASTROENTERITIS AGUDA
    # ========================================================================
    {
        "razon_ingreso": "Gastroenteritis con deshidratación",
        "diagnostico": "Gastroenteritis aguda",
        "examenes": [
            ("Hemograma completo", "Hemoconcentración leve, leucocitos normales"),
            ("Electrolitos séricos", "Sodio 133, Potasio 3.3, hiponatremia e hipocalemia leves"),
            ("Coprocultivo", "Negativo para bacterias patógenas"),
        ],
        "tratamientos": [
            "Rehidratación intravenosa con solución salina",
            "Dieta líquida progresiva a blanda",
            "Reposición de electrolitos",
        ],
        "medicamentos": [
            "Ondansetrón 4 mg IV cada 8 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (88, 108),
            "frecuencia_respiratoria": (16, 22),
            "saturacion_oxigeno": (95, 99),
            "presion_sistolica": (100, 118),
            "presion_diastolica": (58, 72),
            "temperatura": (36.8, 38.2),
        },
        "edad_min": 0,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 11. LUMBALGIA MECÁNICA
    # ========================================================================
    {
        "razon_ingreso": "Dolor lumbar agudo",
        "diagnostico": "Lumbalgia mecánica",
        "examenes": [
            ("Radiografía de columna lumbar", "Rectificación de lordosis, sin lesiones óseas"),
            ("Hemograma completo", "Dentro de parámetros normales"),
        ],
        "tratamientos": [
            "Analgesia y antiinflamatorios",
            "Fisioterapia y ejercicios de rehabilitación",
            "Reposo relativo con calor local",
        ],
        "medicamentos": [
            "Diclofenaco 50 mg VO cada 8 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (68, 85),
            "frecuencia_respiratoria": (14, 18),
            "saturacion_oxigeno": (97, 100),
            "presion_sistolica": (110, 130),
            "presion_diastolica": (68, 82),
            "temperatura": (36.5, 37.0),
        },
        "edad_min": 25,
        "edad_max": 75,
        "sexo": "ambos",
    },

    # ========================================================================
    # 12. FRACTURA DE RADIO EN RECUPERACIÓN
    # ========================================================================
    {
        "razon_ingreso": "Fractura operada de radio",
        "diagnostico": "Fractura de radio en recuperación postquirúrgica",
        "examenes": [
            ("Hemograma completo", "Dentro de parámetros normales"),
            ("Radiografía de muñeca", "Osteosíntesis estable, alineación conservada"),
        ],
        "tratamientos": [
            "Control postoperatorio",
            "Inmovilización con férula",
            "Rehabilitación progresiva",
        ],
        "medicamentos": [
            "Ketorolaco 30 mg IV cada 8 horas por 48 horas",
            "Cefazolina 1 g IV cada 8 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (68, 88),
            "frecuencia_respiratoria": (14, 18),
            "saturacion_oxigeno": (97, 100),
            "presion_sistolica": (108, 128),
            "presion_diastolica": (65, 80),
            "temperatura": (36.5, 37.3),
        },
        "edad_min": 6,
        "edad_max": 80,
        "sexo": "ambos",
    },

    # ========================================================================
    # 13. GONARTROSIS
    # ========================================================================
    {
        "razon_ingreso": "Artrosis incapacitante de rodilla",
        "diagnostico": "Gonartrosis",
        "examenes": [
            ("Radiografía de rodilla", "Disminución del espacio articular, osteofitos marginales"),
        ],
        "tratamientos": [
            "Analgesia y antiinflamatorios",
            "Fisioterapia y ejercicios de fortalecimiento",
            "Aplicación de frío/calor local",
        ],
        "medicamentos": [
            "Celecoxib 200 mg VO cada 12 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (68, 82),
            "frecuencia_respiratoria": (14, 18),
            "saturacion_oxigeno": (97, 100),
            "presion_sistolica": (110, 135),
            "presion_diastolica": (68, 82),
            "temperatura": (36.5, 37.0),
        },
        "edad_min": 50,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 14. INSUFICIENCIA CARDÍACA CONGESTIVA
    # ========================================================================
    {
        "razon_ingreso": "Insuficiencia cardíaca compensada",
        "diagnostico": "Insuficiencia cardíaca congestiva",
        "examenes": [
            ("Péptido natriurético cerebral (BNP)", "480 pg/mL, elevado"),
            ("Creatinina sérica", "1.3 mg/dL"),
            ("Electrolitos séricos", "Sodio 136, Potasio 4.3"),
            ("Ecocardiograma", "Fracción de eyección 40%, hipoquinesia difusa"),
        ],
        "tratamientos": [
            "Diuréticos y control hídrico estricto",
            "Restricción de sodio en dieta",
            "Monitorización de balance hídrico",
        ],
        "medicamentos": [
            "Furosemida 40 mg VO cada 12 horas",
            "Enalapril 10 mg VO cada 12 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (72, 95),
            "frecuencia_respiratoria": (16, 22),
            "saturacion_oxigeno": (92, 97),
            "presion_sistolica": (100, 130),
            "presion_diastolica": (60, 78),
            "temperatura": (36.5, 37.2),
        },
        "edad_min": 60,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 15. ACV ISQUÉMICO EN RECUPERACIÓN
    # ========================================================================
    {
        "razon_ingreso": "ACV isquémico en recuperación",
        "diagnostico": "Enfermedad cerebrovascular isquémica",
        "examenes": [
            ("Tomografía axial computarizada (TAC)", "Lesión isquémica en territorio de arteria cerebral media"),
            ("Perfil lipídico", "Colesterol total 220, LDL 150, HDL 40"),
            ("Glucosa sérica", "110 mg/dL en ayunas"),
        ],
        "tratamientos": [
            "Rehabilitación neurológica y fisioterapia",
            "Prevención secundaria de evento cerebrovascular",
            "Terapia ocupacional",
        ],
        "medicamentos": [
            "Ácido acetilsalicílico 100 mg VO cada 24 horas",
            "Atorvastatina 40 mg VO cada 24 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (65, 85),
            "frecuencia_respiratoria": (14, 20),
            "saturacion_oxigeno": (95, 99),
            "presion_sistolica": (115, 140),
            "presion_diastolica": (68, 85),
            "temperatura": (36.5, 37.0),
        },
        "edad_min": 55,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 16. ANEMIA FERROPÉNICA
    # ========================================================================
    {
        "razon_ingreso": "Anemia sintomática",
        "diagnostico": "Anemia ferropénica",
        "examenes": [
            ("Hemograma completo", "Hemoglobina 8.2 g/dL, VCM 72 fL, microcítica hipocrómica"),
            ("Ferritina sérica", "8 ng/mL, severamente disminuida"),
            ("Hierro sérico", "25 mcg/dL, bajo"),
        ],
        "tratamientos": [
            "Suplementación de hierro oral",
            "Dieta rica en hierro y vitamina C",
            "Control de hemograma semanal",
        ],
        "medicamentos": [
            "Sulfato ferroso 200 mg VO cada 12 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (82, 100),
            "frecuencia_respiratoria": (16, 22),
            "saturacion_oxigeno": (95, 99),
            "presion_sistolica": (100, 118),
            "presion_diastolica": (58, 72),
            "temperatura": (36.3, 37.0),
        },
        "edad_min": 15,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 17. COLECISTECTOMÍA POSTOPERATORIA
    # ========================================================================
    {
        "razon_ingreso": "Colecistitis operada",
        "diagnostico": "Colecistectomía laparoscópica postoperatoria",
        "examenes": [
            ("Hemograma completo", "Leucocitos en rango normal, evolución favorable"),
            ("Perfil hepático", "Transaminasas en descenso, dentro de parámetros"),
        ],
        "tratamientos": [
            "Analgesia postoperatoria",
            "Dieta líquida progresiva a blanda",
            "Deambulación temprana",
        ],
        "medicamentos": [
            "Cefazolina 1 g IV cada 8 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (70, 88),
            "frecuencia_respiratoria": (14, 18),
            "saturacion_oxigeno": (97, 100),
            "presion_sistolica": (108, 125),
            "presion_diastolica": (65, 78),
            "temperatura": (36.5, 37.5),
        },
        "edad_min": 20,
        "edad_max": 70,
        "sexo": "ambos",
    },

    # ========================================================================
    # 18. ÚLCERA VENOSA INFECTADA
    # ========================================================================
    {
        "razon_ingreso": "Insuficiencia venosa con úlcera",
        "diagnostico": "Úlcera venosa infectada",
        "examenes": [
            ("Hemograma completo", "Leucocitosis leve"),
            ("Cultivo de herida", "Staphylococcus aureus y flora mixta"),
        ],
        "tratamientos": [
            "Curaciones diarias con apósito especial",
            "Antibioticoterapia",
            "Compresión elástica y elevación del miembro",
        ],
        "medicamentos": [
            "Amoxicilina/Ácido clavulánico 875/125 mg VO cada 12 horas",
            "Paracetamol 500 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (72, 90),
            "frecuencia_respiratoria": (14, 20),
            "saturacion_oxigeno": (96, 100),
            "presion_sistolica": (110, 132),
            "presion_diastolica": (65, 80),
            "temperatura": (36.8, 37.8),
        },
        "edad_min": 40,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 19. EPILEPSIA (CONVULSIÓN CONTROLADA)
    # ========================================================================
    {
        "razon_ingreso": "Convulsión controlada",
        "diagnostico": "Epilepsia",
        "examenes": [
            ("Hemograma completo", "Dentro de parámetros normales"),
            ("Electrolitos séricos", "Sodio 139, Potasio 4.0, dentro de parámetros"),
            ("Electroencefalograma (EEG)", "Actividad epileptiforme focal en región temporal"),
        ],
        "tratamientos": [
            "Ajuste de anticonvulsivantes",
            "Monitorización neurológica",
            "Precauciones para evitar nuevas crisis",
        ],
        "medicamentos": [
            "Levetiracetam 500 mg VO cada 12 horas",
            "Ácido valproico 500 mg VO cada 12 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (68, 85),
            "frecuencia_respiratoria": (14, 18),
            "saturacion_oxigeno": (97, 100),
            "presion_sistolica": (108, 128),
            "presion_diastolica": (65, 80),
            "temperatura": (36.5, 37.0),
        },
        "edad_min": 5,
        "edad_max": 80,
        "sexo": "ambos",
    },

    # ========================================================================
    # 20. HIPOTIROIDISMO
    # ========================================================================
    {
        "razon_ingreso": "Hipotiroidismo descompensado",
        "diagnostico": "Hipotiroidismo",
        "examenes": [
            ("TSH", "18.5 mUI/L, severamente elevada"),
            ("T4 libre", "0.5 ng/dL, disminuida"),
            ("Hemograma completo", "Anemia normocítica leve"),
        ],
        "tratamientos": [
            "Ajuste hormonal con levotiroxina",
            "Control de TSH en 6 semanas",
            "Evaluación de función tiroidea periódica",
        ],
        "medicamentos": [
            "Levotiroxina 50 mcg VO cada 24 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (55, 68),
            "frecuencia_respiratoria": (12, 18),
            "saturacion_oxigeno": (96, 100),
            "presion_sistolica": (100, 120),
            "presion_diastolica": (60, 75),
            "temperatura": (35.8, 36.5),
        },
        "edad_min": 25,
        "edad_max": 100,
        "sexo": "ambos",
    },

    # ========================================================================
    # 21. ENFERMEDAD INFLAMATORIA PÉLVICA (FEMENINO, 18-45)
    # ========================================================================
    {
        "razon_ingreso": "Dolor pélvico agudo",
        "diagnostico": "Enfermedad inflamatoria pélvica",
        "examenes": [
            ("Hemograma completo", "Leucocitosis moderada"),
            ("Proteína C reactiva", "Elevada: 65 mg/L"),
            ("Ecografía pélvica", "Engrosamiento tubárico bilateral, líquido libre en Douglas"),
        ],
        "tratamientos": [
            "Antibioticoterapia combinada",
            "Reposo relativo",
            "Control ginecológico de seguimiento",
        ],
        "medicamentos": [
            "Ceftriaxona 1 g IV cada 12 horas",
            "Doxiciclina 100 mg VO cada 12 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (85, 105),
            "frecuencia_respiratoria": (16, 22),
            "saturacion_oxigeno": (96, 100),
            "presion_sistolica": (105, 122),
            "presion_diastolica": (62, 78),
            "temperatura": (37.5, 38.8),
        },
        "edad_min": 18,
        "edad_max": 45,
        "sexo": "femenino",
    },

    # ========================================================================
    # 22. MIOMATOSIS UTERINA (FEMENINO, 18-50)
    # ========================================================================
    {
        "razon_ingreso": "Miomatosis uterina sintomática",
        "diagnostico": "Leiomiomas uterinos",
        "examenes": [
            ("Hemograma completo", "Anemia ferropénica leve asociada"),
            ("Ecografía pélvica", "Múltiples miomas intramurales, el mayor de 5 cm"),
        ],
        "tratamientos": [
            "Control de sangrado y analgesia",
            "Evaluación para manejo quirúrgico diferido",
            "Suplementación de hierro",
        ],
        "medicamentos": [
            "Ácido tranexámico 500 mg VO cada 8 horas",
            "Ibuprofeno 600 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (75, 92),
            "frecuencia_respiratoria": (14, 20),
            "saturacion_oxigeno": (96, 100),
            "presion_sistolica": (105, 120),
            "presion_diastolica": (62, 78),
            "temperatura": (36.5, 37.2),
        },
        "edad_min": 18,
        "edad_max": 50,
        "sexo": "femenino",
    },

    # ========================================================================
    # 23. AMENAZA DE PARTO PRETÉRMINO (FEMENINO, 18-45)
    # ========================================================================
    {
        "razon_ingreso": "Embarazo con contracciones",
        "diagnostico": "Amenaza de parto pretérmino",
        "examenes": [
            ("Hemograma completo", "Dentro de parámetros, anemia fisiológica del embarazo"),
            ("Ecografía obstétrica", "Feto único, biometría acorde a edad gestacional de 32 semanas"),
            ("Monitoreo fetal", "Frecuencia cardíaca fetal reactiva, contracciones irregulares"),
        ],
        "tratamientos": [
            "Reposo absoluto en cama",
            "Tocolíticos para inhibir contracciones",
            "Maduración pulmonar fetal con corticoides",
            "Monitorización fetal continua",
        ],
        "medicamentos": [
            "Nifedipino 10 mg VO cada 8 horas",
            "Betametasona 12 mg IM cada 24 horas por 2 dosis",
        ],
        "signos": {
            "frecuencia_cardiaca": (78, 95),
            "frecuencia_respiratoria": (16, 22),
            "saturacion_oxigeno": (97, 100),
            "presion_sistolica": (100, 120),
            "presion_diastolica": (60, 75),
            "temperatura": (36.5, 37.2),
        },
        "edad_min": 18,
        "edad_max": 45,
        "sexo": "femenino",
    },

    # ========================================================================
    # 24. MASTITIS (FEMENINO, 20-55)
    # ========================================================================
    {
        "razon_ingreso": "Dolor mamario e inflamación",
        "diagnostico": "Mastitis",
        "examenes": [
            ("Hemograma completo", "Leucocitosis con neutrofilia"),
            ("Ecografía mamaria", "Signos inflamatorios difusos, sin abscesos definidos"),
        ],
        "tratamientos": [
            "Antibioticoterapia oral",
            "Compresas tibias locales",
            "Extracción frecuente de leche si aplica",
        ],
        "medicamentos": [
            "Dicloxacilina 500 mg VO cada 6 horas",
            "Ibuprofeno 400 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (80, 98),
            "frecuencia_respiratoria": (16, 20),
            "saturacion_oxigeno": (96, 100),
            "presion_sistolica": (108, 125),
            "presion_diastolica": (65, 78),
            "temperatura": (37.8, 39.0),
        },
        "edad_min": 20,
        "edad_max": 55,
        "sexo": "femenino",
    },

    # ========================================================================
    # 25. HIPERPLASIA PROSTÁTICA BENIGNA (MASCULINO, >50)
    # ========================================================================
    {
        "razon_ingreso": "Retención urinaria aguda",
        "diagnostico": "Hiperplasia prostática benigna",
        "examenes": [
            ("Uroanálisis", "Sin signos de infección"),
            ("Creatinina sérica", "1.2 mg/dL"),
            ("Ecografía prostática", "Próstata de 55 g, sin nódulos sospechosos"),
        ],
        "tratamientos": [
            "Sondaje vesical de alivio",
            "Tratamiento farmacológico con alfa-bloqueante",
            "Evaluación urológica para cirugía diferida",
        ],
        "medicamentos": [
            "Tamsulosina 0.4 mg VO cada 24 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (68, 85),
            "frecuencia_respiratoria": (14, 18),
            "saturacion_oxigeno": (97, 100),
            "presion_sistolica": (110, 135),
            "presion_diastolica": (68, 82),
            "temperatura": (36.5, 37.0),
        },
        "edad_min": 50,
        "edad_max": 100,
        "sexo": "masculino",
    },

    # ========================================================================
    # 26. PROSTATITIS BACTERIANA (MASCULINO, >60)
    # ========================================================================
    {
        "razon_ingreso": "Infección urinaria con fiebre",
        "diagnostico": "Prostatitis bacteriana",
        "examenes": [
            ("Hemograma completo", "Leucocitosis marcada"),
            ("Uroanálisis", "Piuria, bacteriuria, nitritos positivos"),
            ("Urocultivo", "Escherichia coli >100,000 UFC/mL"),
            ("Antígeno prostático específico (PSA)", "8.5 ng/mL, elevado por inflamación"),
        ],
        "tratamientos": [
            "Antibioticoterapia prolongada",
            "Hidratación parenteral",
            "Antiinflamatorios",
        ],
        "medicamentos": [
            "Ciprofloxacino 500 mg VO cada 12 horas",
            "Ibuprofeno 400 mg VO cada 8 horas",
        ],
        "signos": {
            "frecuencia_cardiaca": (88, 105),
            "frecuencia_respiratoria": (16, 22),
            "saturacion_oxigeno": (95, 99),
            "presion_sistolica": (105, 128),
            "presion_diastolica": (62, 80),
            "temperatura": (38.0, 39.2),
        },
        "edad_min": 60,
        "edad_max": 100,
        "sexo": "masculino",
    },
]
