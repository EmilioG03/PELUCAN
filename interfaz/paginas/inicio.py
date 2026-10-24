# pyright: reportOptionalMemberAccess=false
from datetime import date
from decimal import Decimal
import tkinter as tk
from tkinter import ttk

from interfaz.paginas.base import PaginaBase

try:
    import psycopg2
    from datos import inicio_dao
except ImportError:
    psycopg2 = None
    inicio_dao = None


def formatear_pesos(monto):
    valor = Decimal(monto)
    entero, decimales = f"{valor:,.2f}".split(".")
    entero = entero.replace(",", ".")
    return f"$ {entero},{decimales}"


def turnos_de_fecha(fecha=None, dao=None):
    """Turnos de la fecha (sin cancelados) leídos de la base, como dicts para la tabla."""
    dao = dao or inicio_dao
    fecha_consulta = fecha or date.today()
    return [
        {
            "mascota": mascota,
            "servicio": servicio,
            "fecha": fecha_turno.strftime("%d/%m/%Y"),
            "hora": hora.strftime("%H:%M"),
            "estado": estado,
        }
        for mascota, servicio, fecha_turno, hora, estado
        in dao.listar_turnos_del_dia(fecha_consulta)
    ]


def calcular_metricas(fecha=None, dao=None):
    """Métricas del panel leídas de la base para la fecha indicada (por defecto, hoy)."""
    dao = dao or inicio_dao
    return dao.obtener_metricas(fecha or date.today())


class PaginaInicio(PaginaBase):
    titulo = "Inicio – Panel General"
    subtitulo = "Resumen dinámico de la actividad del día."

    def construir_contenido(self):
        # Cartelito que avisa si el panel se está leyendo bien de la base
        self.lbl_estado = ttk.Label(self, style="Subtitulo.TLabel")
        self.lbl_estado.pack(anchor="w", padx=24, pady=(0, 4))

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

    def _cargar_turnos_tabla(self, turnos):
        self.tabla_turnos.delete(*self.tabla_turnos.get_children())
        for turno in turnos:
            self.tabla_turnos.insert(
                "",
                tk.END,
                values=tuple(turno.get(clave, "") for clave in (
                    "mascota", "servicio", "fecha", "hora", "estado"
                )),
            )

    def _mostrar_sin_conexion(self, detalle):
        """Si no se puede leer la base, no se inventan datos: se avisa y se vacía el panel."""
        for etiqueta in self.etiquetas_resumen.values():
            etiqueta.config(text="–")
        self._cargar_turnos_tabla([])
        self.lbl_estado.config(text=f"● Sin conexión a la base de datos: {detalle}")

    def actualizar_metricas(self):
        if inicio_dao is None:
            self._mostrar_sin_conexion(
                "faltan instalar psycopg2 o python-dotenv (pip install psycopg2-binary python-dotenv)."
            )
            return

        try:
            metricas = calcular_metricas()
            turnos = turnos_de_fecha()
        except psycopg2.Error as error:
            lineas = str(error).strip().splitlines()
            self._mostrar_sin_conexion(lineas[0] if lineas else "error de base de datos.")
            return

        self.etiquetas_resumen["turnos"].config(text=str(metricas["turnos"]))
        self.etiquetas_resumen["clientes"].config(text=str(metricas["clientes"]))
        self.etiquetas_resumen["mascotas"].config(text=str(metricas["mascotas"]))
        self.etiquetas_resumen["ingresos"].config(text=formatear_pesos(metricas["ingresos"]))
        self._cargar_turnos_tabla(turnos)
        self.lbl_estado.config(text="● Conectado a la base de datos PostgreSQL.")
