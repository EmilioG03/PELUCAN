import tkinter as tk
from tkinter import ttk
from datetime import datetime
from interfaz.paginas.base import PaginaBase
from interfaz.paginas.clientes import CLIENTES_EJEMPLO
from interfaz.paginas.mascotas import MASCOTAS_EJEMPLO
from interfaz.paginas.turnos import TURNOS_EJEMPLO


class PaginaInicio(PaginaBase):
    titulo = "Inicio – Panel General"
    subtitulo = "Resumen de actividad y próximos turnos programados."

    def construir_contenido(self):
        #Contenedor de las tres tarjetas metricas
        marco_tarjetas = ttk.Frame(self, style="Contenido.TFrame")
        marco_tarjetas.pack(fill="x", padx=24, pady=(5, 10))

        for i in range(3):
            marco_tarjetas.grid_columnconfigure(i, weight=1, uniform="tarjetas")

        self.etiquetas_resumen = {}

        config_tarjetas = [
            ("turnos", "Turnos del dia", len(TURNOS_EJEMPLO)),
            ("clientes", "Clientes registrados", len(CLIENTES_EJEMPLO)),
            ("mascotas", "Mascotas registradas", len(MASCOTAS_EJEMPLO)),
        ]

        for columna, (clave, texto, valor) in enumerate(config_tarjetas):
            tarjeta = ttk.Frame(marco_tarjetas, style="Card.TFrame", padding=(16, 14))
            tarjeta.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=(0, 16 if columna < len(config_tarjetas) - 1 else 0),
            )

            ttk.Label(
                tarjeta,
                text=texto,
                style="CardTitulo.TLabel",
            ).pack(anchor="w")

            lbl_numero = ttk.Label(
                tarjeta,
                text=str(valor),
                style="CardNumero.TLabel",
            )
            lbl_numero.pack(anchor="w", pady=(6, 0))
            self.etiquetas_resumen[clave] = lbl_numero

        #Seccion proximos turnos
        ttk.Label(
            self,
            text="Próximos turnos del día",
            style="Seccion.TLabel"
        ).pack(anchor="w", padx=24, pady=(15, 8))

        #Contenedor del listado de turnos
        marco_tabla = ttk.Frame(self, style="Contenido.TFrame")
        marco_tabla.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        columnas = ("mascota", "servicio", "fecha", "hora", "estado")
        self.tabla_turnos = ttk.Treeview(
            marco_tabla,
            columns=columnas,
            show="headings",
            height=6,
            selectmode="browse"
        )
        # Encabezados
        self.tabla_turnos.heading("mascota", text="Mascota")
        self.tabla_turnos.heading("servicio", text="Servicio")
        self.tabla_turnos.heading("fecha", text="Fecha")
        self.tabla_turnos.heading("hora", text="Hora")
        self.tabla_turnos.heading("estado", text="Estado")

        # Configuración de anchos y alineación
        self.tabla_turnos.column("mascota", width=140, anchor="w")
        self.tabla_turnos.column("servicio", width=140, anchor="w")
        self.tabla_turnos.column("fecha", width=100, anchor="center")
        self.tabla_turnos.column("hora", width=80, anchor="center")
        self.tabla_turnos.column("estado", width=100, anchor="center")

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_turnos.yview)
        self.tabla_turnos.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")
        self.tabla_turnos.pack(side="left", fill="both", expand=True)

        self._cargar_turnos_tabla()

    def _cargar_turnos_tabla(self):
        """Carga o recarga las filas de la tabla de turnos."""
        self.tabla_turnos.delete(*self.tabla_turnos.get_children())
        for turno in TURNOS_EJEMPLO:
            self.tabla_turnos.insert(
                "",
                tk.END,
                values=(
                    turno.get("mascota", ""),
                    turno.get("servicio", ""),
                    turno.get("fecha", ""),
                    turno.get("hora", ""),
                    turno.get("estado", ""),
                ),
            )

    def actualizar_metricas(self):
        """Actualiza los números de las tarjetas y la tabla cada vez que se entra a Inicio."""
        self.etiquetas_resumen["turnos"].config(text=str(len(TURNOS_EJEMPLO)))
        self.etiquetas_resumen["clientes"].config(text=str(len(CLIENTES_EJEMPLO)))
        self.etiquetas_resumen["mascotas"].config(text=str(len(MASCOTAS_EJEMPLO)))
        self._cargar_turnos_tabla()




