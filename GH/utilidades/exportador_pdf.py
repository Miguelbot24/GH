"""
Módulo: exportador_pdf.py
Sprint 7 — Exportador de reportes PDF por paciente.

Genera un archivo PDF descargable con la ficha completa del paciente:
datos demográficos, signos vitales, exámenes, diagnósticos, tratamientos,
razón de ingreso y médico asignado.

Dependencias previas necesarias:
    - config.py              (NOMBRES_SIGNOS, UNIDADES_SIGNOS, RANGOS_NORMALES)
    - modelos/paciente.py    (Paciente)

Librerías externas requeridas:
    - fpdf2  (pip install fpdf2)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from fpdf import FPDF

from config import (
    NOMBRES_SIGNOS,
    UNIDADES_SIGNOS,
    RANGOS_NORMALES,
)


class ExportadorPDF:
    """
    Genera reportes PDF individuales por paciente con toda su información
    clínica consolidada.
    """

    def __init__(self):
        pass

    def exportar_paciente(self, paciente, ruta_salida: str) -> str:
        """
        Genera un PDF con la ficha completa del paciente y lo guarda
        en la ruta especificada.

        Args:
            paciente:    Instancia de Paciente (o subclase).
            ruta_salida: Ruta donde se guardará el PDF.

        Returns:
            La ruta del archivo generado.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)

        # ── Encabezado ──
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, "GESTION HOSPITALARIA - GH", ln=True, align="C")
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, "Reporte de Paciente", ln=True, align="C")
        pdf.ln(4)

        # Línea separadora
        pdf.set_draw_color(56, 142, 60)
        pdf.set_line_width(0.6)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

        # ── Datos del paciente ──
        self._escribir_seccion(pdf, "DATOS DEL PACIENTE")
        self._escribir_campo(pdf, "ID", paciente.id_paciente)
        self._escribir_campo(pdf, "Nombre", paciente.nombre)
        self._escribir_campo(pdf, "Edad", f"{paciente.edad} años")
        self._escribir_campo(pdf, "Genero", paciente.genero)

        tipo = paciente.__class__.__name__
        if tipo == "PacienteSala":
            ubicacion = f"Cama {paciente.numero_cama} - Planta: {paciente.planta}"
            self._escribir_campo(pdf, "Ubicacion", ubicacion)
        elif tipo == "PacienteEmergencia":
            self._escribir_campo(pdf, "Area", "Emergencias")
            self._escribir_campo(pdf, "Prioridad adm.",
                                f"{paciente.prioridad_administrativa}/5")
            self._escribir_campo(pdf, "Espera", paciente.tiempo_espera_legible())

        estado_str = paciente.estado
        if paciente.tipo_egreso:
            estado_str += f" ({paciente.tipo_egreso})"
        self._escribir_campo(pdf, "Estado", estado_str)

        if paciente.fecha_ingreso:
            self._escribir_campo(
                pdf, "Fecha de ingreso",
                paciente.fecha_ingreso.strftime("%d/%m/%Y %H:%M")
            )
        if paciente.fecha_egreso:
            self._escribir_campo(
                pdf, "Fecha de egreso",
                paciente.fecha_egreso.strftime("%d/%m/%Y %H:%M")
            )

        # Razón de ingreso
        razon = paciente.razon_ingreso
        if tipo == "PacienteEmergencia" and hasattr(paciente, "motivo_consulta"):
            if not razon:
                razon = paciente.motivo_consulta
        self._escribir_campo(pdf, "Razon de ingreso", razon or "No especificada")

        # Médico asignado
        self._escribir_campo(pdf, "Medico asignado",
                            paciente.doctor_asignado or "No asignado")

        pdf.ln(4)

        # ── Signos vitales ──
        self._escribir_seccion(pdf, "SIGNOS VITALES")
        signos = paciente.signos_vitales
        for nombre in [
            "frecuencia_cardiaca",
            "frecuencia_respiratoria",
            "saturacion_oxigeno",
            "presion_sistolica",
            "presion_diastolica",
            "temperatura",
        ]:
            valor = signos._obtener_valor(nombre)
            nombre_legible = NOMBRES_SIGNOS.get(nombre, nombre)
            unidad = UNIDADES_SIGNOS.get(nombre, "")
            vmin, vmax = RANGOS_NORMALES.get(nombre, (0, 0))

            texto = (f"{nombre_legible}: {self._fmt(valor, nombre)} {unidad}"
                     f"  (rango {vmin}-{vmax} {unidad})")
            self._escribir_linea(pdf, texto)

        pdf.ln(4)

        # ── Historial medico (solo para pacientes de sala; emergencias
        #     aún no han sido atendidos y no tienen historial relevante)
        if paciente.__class__.__name__ != "PacienteEmergencia":
            historial = paciente.historial
            if historial:
                self._escribir_seccion(pdf, "HISTORIAL MEDICO")

                # Exámenes
                self._escribir_subseccion(pdf, "Examenes")
                if historial.examenes:
                    for ex in historial.examenes:
                        fecha_str = ex.fecha.strftime("%d/%m/%Y %H:%M") if ex.fecha else "--"
                        self._escribir_linea(
                            pdf, f"[{fecha_str}] {ex.tipo}: {ex.resultado}"
                        )
                        if ex.notas:
                            self._escribir_linea(pdf, f"  Notas: {ex.notas}", size=9)
                else:
                    self._escribir_linea(pdf, "(Sin examenes registrados)")

                pdf.ln(2)

                # Diagnósticos
                self._escribir_subseccion(pdf, "Diagnosticos")
                if historial.diagnosticos:
                    for d in historial.diagnosticos:
                        fecha_str = d["fecha"].strftime("%d/%m/%Y") if d.get("fecha") else "--"
                        autor = d.get("autor", "")
                        texto = f"[{fecha_str}] {d['descripcion']}"
                        if autor:
                            texto += f" (Dr/a. {autor})"
                        self._escribir_linea(pdf, texto)
                else:
                    self._escribir_linea(pdf, "(Sin diagnosticos registrados)")

                pdf.ln(2)

                # Tratamientos
                self._escribir_subseccion(pdf, "Tratamientos")
                if historial.tratamientos:
                    for t in historial.tratamientos:
                        fecha_str = t["fecha"].strftime("%d/%m/%Y") if t.get("fecha") else "--"
                        autor = t.get("autor", "")
                        texto = f"[{fecha_str}] {t['descripcion']}"
                        if autor:
                            texto += f" (Dr/a. {autor})"
                        self._escribir_linea(pdf, texto)
                else:
                    self._escribir_linea(pdf, "(Sin tratamientos registrados)")

                pdf.ln(2)

                self._escribir_subseccion(pdf, "Medicamentos administrados")
                if historial.medicamentos:
                    for m in historial.medicamentos:
                        fecha_str = m["fecha"].strftime("%d/%m/%Y") if m.get("fecha") else "--"
                        autor = m.get("autor", "")
                        texto = f"[{fecha_str}] {m['descripcion']}"
                        if autor:
                            texto += f" (Dr/a. {autor})"
                        self._escribir_linea(pdf, texto)
                else:
                    self._escribir_linea(pdf, "(Sin medicamentos registrados)")
            else:
                self._escribir_seccion(pdf, "HISTORIAL MEDICO")
                self._escribir_linea(pdf, "(Historial no disponible)")

        # ── Pie de página ──
        pdf.ln(6)
        pdf.set_draw_color(56, 142, 60)
        pdf.set_line_width(0.4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 6,
                 f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                 f" - Sistema GH v1.0",
                 ln=True, align="C")

        pdf.output(ruta_salida)
        return ruta_salida

    # ==================================================================
    # MÉTODOS AUXILIARES DE FORMATEO
    # ==================================================================
    def _escribir_seccion(self, pdf: FPDF, titulo: str) -> None:
        """Escribe un título de sección con fondo verde y texto blanco."""
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_fill_color(56, 142, 60)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 9, f"  {titulo}", ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

    def _escribir_subseccion(self, pdf: FPDF, titulo: str) -> None:
        """Escribe un subtítulo de subsección."""
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, titulo, ln=True)
        pdf.set_font("Helvetica", "", 10)

    def _escribir_campo(self, pdf: FPDF, etiqueta: str, valor: str) -> None:
        """Escribe un campo etiqueta: valor."""
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(42, 6, f"{etiqueta}:", ln=0)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, str(valor), ln=True)

    def _escribir_linea(self, pdf: FPDF, texto: str, size: int = 10) -> None:
        """Escribe una línea de texto simple."""
        pdf.set_font("Helvetica", "", size)
        pdf.cell(0, 6, texto, ln=True)

    @staticmethod
    def _fmt(valor, nombre_signo: str = "") -> str:
        """Formatea un valor numérico: entero salvo temperatura."""
        if isinstance(valor, float):
            if valor == 0.0:
                return "--"
            if nombre_signo == "temperatura":
                return f"{valor:.1f}"
            if valor == int(valor):
                return str(int(valor))
            return str(int(round(valor)))
        return str(valor)
