from datetime import date
from decimal import Decimal
import tkinter as tk
from tkinter import ttk

from interfaz.paginas.base import PaginaBase
from interfaz.paginas.clientes import CLIENTES_EJEMPLO
from interfaz.paginas.mascotas import MASCOTAS_EJEMPLO
from interfaz.paginas.pagos import PAGOS_EJEMPLO, total_ingresos
from interfaz.paginas.turnos import TURNOS_EJEMPLO


def formatear_pesos(monto):
    valor = Decimal(monto)
    entero, decimales = f"{valor:,.2f}".split(".")
    entero = entero.replace(",", ".")
    return f"$ {entero},{decimales}"


def turnos_de_fecha(fecha=None):
    fecha_objetivo = (fecha or date.today()).strftime("%d/%m/%Y")
    turnos = [
        turno
        for turno in TURNOS_EJEMPLO
        if turno["fecha"] == fecha_objetivo and turno["estado"] != "Cancelado"
    ]
    return sorted(turnos, key=lambda turno: turno["hora"])


def calcular_metricas(fecha=None):
    fecha_consulta = fecha or date.today()
    return {
        "turnos": len(turnos_de_fecha(fecha_consulta)),
        "clientes": len(CLIENTES_EJEMPLO),
        "mascotas": len(MASCOTAS_EJEMPLO),
        "ingresos": total_ingresos(PAGOS_EJEMPLO, fecha_consulta),
    }


class PaginaInicio(PaginaBase):
    titulo = "Inicio – Panel General"
    subtitulo = "Resumen dinámico de la actividad del día."

    def construir_contenido(self):
        marco_tarjetas = ttk.Frame(self, style="Contenido.TFrame")
        marco_tarjetas.pack(fill="x", padx=24, pady=(5, 10))

        for indice in range(4):
            marco_tarjetas.grid_columnconfigure(indice, weight=1, uniform="tarjetas")

        self.etiquetas_resumen = {}
        config_tarjetas = [
            ("turnos", "Turnos del día"),
            ("clientes", "Clientes registrados"),
            ("mascotas", "Mascotas registradas"),
            ("ingresos", "Ingresos del día"),
        ]

        for columna, (clave, texto) in enumerate(config_tarjetas):
            tarjeta = ttk.Frame(marco_tarjetas, style="Card.TFrame", padding=(16, 14))
            tarjeta.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=(0, 12 if columna < len(config_tarjetas) - 1 else 0),
            )
            ttk.Label(tarjeta, text=texto, style="CardTitulo.TLabel").pack(anchor="w")
            etiqueta_valor = ttk.Label(tarjeta, text="0", style="CardNumero.TLabel")
            etiqueta_valor.pack(anchor="w", pady=(6, 0))
            self.etiquetas_resumen[clave] = etiqueta_valor

        ttk.Label(
            self,
            text="Turnos del día",
            style="Seccion.TLabel",
        ).pack(anchor="w", padx=24, pady=(15, 8))

        marco_tabla = ttk.Frame(self, style="Contenido.TFrame")
        marco_tabla.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        columnas = ("mascota", "servicio", "fecha", "hora", "estado")
        self.tabla_turnos = ttk.Treeview(
            marco_tabla,
            columns=columnas,
            show="headings",
            height=6,
            selectmode="browse",
        )
        encabezados = {
            "mascota": "Mascota",
            "servicio": "Servicio",
            "fecha": "Fecha",
            "hora": "Hora",
            "estado": "Estado",
        }
        anchos = {"mascota": 140, "servicio": 160, "fecha": 100, "hora": 80, "estado": 100}
        for clave in columnas:
            self.tabla_turnos.heading(clave, text=encabezados[clave])
            self.tabla_turnos.column(
                clave,
                width=anchos[clave],
                anchor="w" if clave in ("mascota", "servicio") else "center",
            )

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_turnos.yview)
        self.tabla_turnos.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tabla_turnos.pack(side="left", fill="both", expand=True)

        self.actualizar_metricas()

    def _cargar_turnos_tabla(self):
        self.tabla_turnos.delete(*self.tabla_turnos.get_children())
        for turno in turnos_de_fecha():
            self.tabla_turnos.insert(
                "",
                tk.END,
                values=tuple(turno.get(clave, "") for clave in (
                    "mascota", "servicio", "fecha", "hora", "estado"
                )),
            )

    def actualizar_metricas(self):
        metricas = calcular_metricas()
        self.etiquetas_resumen["turnos"].config(text=str(metricas["turnos"]))
        self.etiquetas_resumen["clientes"].config(text=str(metricas["clientes"]))
        self.etiquetas_resumen["mascotas"].config(text=str(metricas["mascotas"]))
        self.etiquetas_resumen["ingresos"].config(text=formatear_pesos(metricas["ingresos"]))
        self._cargar_turnos_tabla()
