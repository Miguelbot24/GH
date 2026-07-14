# Gestión Hospitalaria (GH)

Sistema de simulación y monitoreo hospitalario desarrollado en Python como proyecto universitario de Programación Orientada a Objetos. Simula el flujo completo de pacientes en un entorno clínico: admisión, triaje, monitoreo continuo de signos vitales, atención en emergencias, hospitalización en salas, egresos y exportación de fichas clínicas.

## Características

- **Monitoreo continuo de signos vitales** (FC, FR, SpO₂, PA, temperatura) con clasificación automática en 3 estados clínicos: ESTABLE, PRUDENTE y ATENCIÓN
- **Triaje inteligente en emergencias** con cola de prioridad CRITICO-first y tiempos de espera
- **Panel de hospitalización** con 4 salas (A-D) de 6 pacientes cada una, tarjetas coloreadas por estado clínico e indicadores en tiempo real
- **Área de Egresos** con registro de altas médicas y fugas
- **Simulador de emergencias** con 6 escenarios críticos (paro cardíaco, shock séptico, fallo respiratorio, etc.)
- **Sistema de alertas** visuales (círculo rojo parpadeante) y sonoras (alarma en bucle) para pacientes en estado crítico
- **Generación de datos coherentes** con 26 condiciones clínicas que vinculan razón de ingreso → diagnóstico → exámenes → tratamientos → medicamentos, respetando restricciones de sexo y grupo etario
- **Exportación de fichas clínicas a PDF** con signos vitales, exámenes de laboratorio, diagnósticos, tratamientos y medicamentos administrados
- **Interfaz gráfica** moderna con `customtkinter` en modo oscuro, navegación por pestañas y paneles con scroll

## Arquitectura

```
GH/
├── modelos/         # Capa de dominio (Paciente, SignosVitales, HistorialMedico)
├── datos/           # Capa de datos (GeneradorDatos, RepositorioPacientes, Condiciones)
├── alertas/         # Capa de negocio (MonitorSignos, Notificador, SimuladorEmergencia)
├── interfaz/        # Capa de presentación (Paneles, Componentes, DetallePaciente)
├── utilidades/      # Exportador de PDF
├── config.py        # Constantes globales (umbrales clínicos, colores, parámetros)
└── main.py          # Orquestador principal
```

### Patrones de diseño

**Observer:** `MonitorSignos` evalúa signos vitales periódicamente y notifica a `Notificador` y a la GUI sobre cambios de estado.

**4 pilares de POO:**

| Pilar           | Implementación                                                               |
| --------------- | ---------------------------------------------------------------------------- |
| Abstracción     | `Paciente` y `PersonalHospital` como clases base abstractas (ABC)            |
| Encapsulamiento | `SignosVitales` con atributos privados mediante name mangling (`__attr`)     |
| Herencia        | `PacienteSala` y `PacienteEmergencia` heredan de `Paciente`                  |
| Polimorfismo    | Cada subclase implementa `calcular_estado()` con lógica propia según el área |

## Flujo del sistema

```
INICIAR SISTEMA
  → Generar 24 pacientes de sala + 10 de emergencia (datos coherentes)
  → MonitorSignos evalúa estados clínicos cada 5 segundos
  → Panel de Selección: Hospitalización | Emergencias | Egresos

HOSPITALIZACIÓN
  → 4 salas × 6 pacientes en tarjetas con indicadores de signos vitales
  → Estados: ESTABLE (verde) → PRUDENTE (naranja) → ATENCIÓN (rojo)
  → ATENCIÓN solo se alcanza con SIMULAR EMERGENCIA
  → Botón "Atender en Sala" estabiliza al paciente
  → Botón "Ver más" exporta ficha clínica a PDF

EMERGENCIAS
  → Cola de espera con prioridad CRITICO-first
  → "Atender Siguiente" transfiere paciente a sala de recuperación (E o F)
  → "Marcar Fuga" envía paciente a Egresos sin atención
  → "Ver más" exporta PDF con signos vitales y plan de atención pendiente

EGRESOS
  → Lista de altas médicas y fugas con fecha de egreso
  → "Ver más" disponible solo para DADO_DE_ALTA
```

## Tecnologías

| Dependencia     | Uso                                                 |
| --------------- | --------------------------------------------------- |
| `customtkinter` | Interfaz gráfica moderna con tema oscuro            |
| `Pillow` (PIL)  | Carga de imágenes de avatar                         |
| `fpdf2`         | Generación de reportes PDF                          |
| `winsound`      | Reproducción de alertas sonoras (nativo de Windows) |

## Instalación y ejecución

```bash
# Clonar repositorio
git clone https://github.com/Miguelbot24/GH.git
cd GH

# Instalar dependencias
pip install customtkinter pillow fpdf2

# Ejecutar
python GH/main.py
```

## Umbrales clínicos — Área de Hospitalización

| Signo                   | ESTABLE        | PRUDENTE             | ATENCIÓN      |
| ----------------------- | -------------- | -------------------- | ------------- |
| Frecuencia cardíaca     | 60 – 100 bpm   | 57-59, 101-103       | <57 o >103    |
| Frecuencia respiratoria | 12 – 20 rpm    | 9-11, 21-23          | <9 o >23      |
| Saturación O₂           | 95 – 100 %     | 92-94                | <92           |
| Presión sistólica       | 100 – 140 mmHg | 97-99, 141-143       | <97 o >143    |
| Presión diastólica      | 60 – 80 mmHg   | 57-59, 81-83         | <57 o >83     |
| Temperatura             | 36.5 – 37.5 °C | 36.2-36.4, 37.6-37.8 | <36.2 o >37.8 |

## Licencia

Proyecto académico — Facultad de Ingeniería Electrica y Electrónica, 2026.
