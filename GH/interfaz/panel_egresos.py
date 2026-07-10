"""
Módulo: panel_egresos.py
Sprint 7 — Panel del área de egresos.

Define la clase PanelEgresos, que muestra la lista de pacientes que han
sido dados de alta o marcados como fugados. Cada fila muestra nombre,
edad, tipo de egreso y fecha/hora del egreso.

Dependencias previas necesarias:
    - config.py                  (COLORES_EGRESO, TIPO_EGRESO_ALTA, TIPO_EGRESO_FUGA)

Librería externa requerida:
    - customtkinter  (pip install customtkinter)
"""

import sys
import os

if __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk

from config import (
    COLORES_EGRESO,
    TIPO_EGRESO_ALTA,
    TIPO_EGRESO_FUGA,
    COLOR_ESTABLE,
)


class TarjetaEgreso(ctk.CTkFrame):
    """
    Fila individual que representa a un paciente egresado.
    Muestra nombre, edad, tipo de egreso y fecha/hora.
    """

    def __init__(self, parent, paciente, on_ver_mas_callback=None, **kwargs):
        super().__init__(
            parent,
            fg_color="#1E1E1E",
            corner_radius=8,
            height=50,
            **kwargs,
        )
        self.pack_propagate(False)
        self._paciente = paciente
        self._on_ver_mas = on_ver_mas_callback

        tipo = paciente.tipo_egreso
        color_tipo = COLORES_EGRESO.get(tipo, "#757575")
        etiqueta_tipo = "ALTA" if tipo == TIPO_EGRESO_ALTA else "FUGA"

        # Barra de color lateral
        barra = ctk.CTkFrame(self, width=5, fg_color=color_tipo, corner_radius=2)
        barra.pack(side="left", fill="y", padx=(0, 10))

        # Nombre
        nombre_lbl = ctk.CTkLabel(
            self,
            text=paciente.nombre[:28] + ("..." if len(paciente.nombre) > 28 else ""),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#FFFFFF",
            anchor="w",
        )
        nombre_lbl.pack(side="left", padx=5, pady=5)

        # Edad
        edad_lbl = ctk.CTkLabel(
            self,
            text=f"{paciente.edad} años",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#AAAAAA",
        )
        edad_lbl.pack(side="left", padx=5, pady=5)

        # Badge de tipo de egreso
        badge = ctk.CTkFrame(
            self, fg_color=color_tipo, corner_radius=6, width=80, height=28
        )
        badge.pack(side="right", padx=10, pady=5)
        badge.pack_propagate(False)
        ctk.CTkLabel(
            badge,
            text=etiqueta_tipo,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#FFFFFF",
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Fecha de egreso
        if paciente.fecha_egreso:
            fecha_str = paciente.fecha_egreso.strftime("%d/%m/%Y %H:%M")
        else:
            fecha_str = "--"
        fecha_lbl = ctk.CTkLabel(
            self,
            text=fecha_str,
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#888888",
        )
        fecha_lbl.pack(side="right", padx=10, pady=5)

        # Botón "Ver más" (solo para DADO_DE_ALTA, no para FUGADO)
        if self._on_ver_mas and tipo == TIPO_EGRESO_ALTA:
            btn_ver_mas = ctk.CTkButton(
                self,
                text="Ver mas",
                font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                width=55,
                height=22,
                corner_radius=4,
                fg_color="#444444",
                hover_color="#666666",
                text_color="#CCCCCC",
                command=self._on_click_ver_mas,
            )
            btn_ver_mas.pack(side="right", padx=4, pady=5)

    def _on_click_ver_mas(self) -> None:
        """Maneja el evento del botón 'Ver más'."""
        if self._on_ver_mas:
            self._on_ver_mas(self._paciente)


class PanelEgresos(ctk.CTkFrame):
    """
    Panel del área de egresos. Lista los pacientes que han sido dados
    de alta o marcados como fugados.

    Se compone de:
      - Barra superior con título y controles.
      - Área desplazable con las filas de pacientes egresados.
    """

    def __init__(
        self,
        parent,
        on_volver_callback=None,
        on_ver_mas_callback=None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)

        self._on_volver = on_volver_callback
        self._on_ver_mas = on_ver_mas_callback
        self._pacientes: list = []

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._crear_barra_superior()
        self._crear_area_contenido()

    def _crear_barra_superior(self) -> None:
        barra = ctk.CTkFrame(self, fg_color="#1A1A1A", height=55)
        barra.grid(row=0, column=0, sticky="ew")
        barra.pack_propagate(False)

        titulo = ctk.CTkLabel(
            barra,
            text="Área de Egresos",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#FFFFFF",
        )
        titulo.pack(side="left", padx=20, pady=10)

        subtitulo = ctk.CTkLabel(
            barra,
            text="Pacientes dados de alta y fugados",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#888888",
        )
        subtitulo.pack(side="left", padx=(5, 20), pady=10)

        if self._on_volver:
            btn_volver = ctk.CTkButton(
                barra,
                text="Volver",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                width=90,
                height=32,
                corner_radius=8,
                fg_color="#444444",
                hover_color="#555555",
                command=self._on_volver,
            )
            btn_volver.pack(side="right", padx=20, pady=10)


    def _crear_area_contenido(self) -> None:
        self._frame_scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self._frame_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self._contenedor_filas = ctk.CTkFrame(
            self._frame_scroll, fg_color="transparent"
        )
        self._contenedor_filas.pack(fill="x", padx=10, pady=5)

    def cargar_pacientes(self, pacientes: list) -> None:
        """
        Carga la lista de pacientes egresados y reconstruye la vista.

        Args:
            pacientes: Lista de instancias de Paciente con tipo_egreso != None.
        """
        self._pacientes = list(pacientes)
        self._reconstruir_filas()

    def refrescar(self) -> None:
        if not self._pacientes:
            return
        self._reconstruir_filas()

    def _reconstruir_filas(self) -> None:
        for widget in self._contenedor_filas.winfo_children():
            widget.destroy()

        if not self._pacientes:
            ctk.CTkLabel(
                self._contenedor_filas,
                text="No hay pacientes egresados.",
                font=ctk.CTkFont(family="Segoe UI", size=16),
                text_color="#666666",
            ).pack(pady=60)
            return

        # Ordenar por fecha de egreso (más reciente primero)
        pacientes_ordenados = sorted(
            self._pacientes,
            key=lambda p: p.fecha_egreso if p.fecha_egreso else p.fecha_ingreso,
            reverse=True,
        )

        alto_total = 0
        con_alta = sum(1 for p in pacientes_ordenados if p.tipo_egreso == TIPO_EGRESO_ALTA)
        con_fuga = sum(1 for p in pacientes_ordenados if p.tipo_egreso == TIPO_EGRESO_FUGA)

        # Encabezado de resumen
        resumen = ctk.CTkFrame(
            self._contenedor_filas, fg_color="#252525", corner_radius=8, height=38
        )
        resumen.pack(fill="x", pady=(0, 8))
        resumen.pack_propagate(False)

        ctk.CTkLabel(
            resumen,
            text=f"Total: {len(pacientes_ordenados)} egresos",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#FFFFFF",
        ).pack(side="left", padx=15, pady=8)

        ctk.CTkLabel(
            resumen,
            text=f"Altas: {con_alta}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORES_EGRESO.get(TIPO_EGRESO_ALTA, "#4CAF50"),
        ).pack(side="left", padx=10, pady=8)

        ctk.CTkLabel(
            resumen,
            text=f"Fugas: {con_fuga}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORES_EGRESO.get(TIPO_EGRESO_FUGA, "#FF9800"),
        ).pack(side="left", padx=10, pady=8)

        for paciente in pacientes_ordenados:
            fila = TarjetaEgreso(
                self._contenedor_filas, paciente,
                on_ver_mas_callback=self._on_ver_mas,
            )
            fila.pack(fill="x", pady=3)

    @property
    def pacientes(self) -> list:
        return list(self._pacientes)
