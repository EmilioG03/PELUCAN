from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from tkinter import messagebox

import psycopg2
from psycopg2 import errors

from interfaz.paginas.base import PaginaABM
from datos import pago_dao


METODOS_PAGO = ("Efectivo", "Transferencia", "Tarjeta")


# =========================================================
# FUNCIONES AUXILIARES
# (las usan Inicio y los tests)
# =========================================================

def etiqueta_turno(turno, indice):
    """Devuelve una referencia legible y estable para seleccionar un turno."""
    return (
        f"Turno #{indice + 1} - {turno['fecha']} {turno['hora']} - "
        f"{turno['mascota']}"
    )


def convertir_monto(valor):
    """Convierte importes escritos con coma o punto a Decimal."""
    texto = str(valor).strip().replace(" ", "")

    if not texto:
        raise ValueError("El monto es obligatorio.")

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    else:
        texto = texto.replace(",", ".")

    try:
        monto = Decimal(texto)

    except InvalidOperation as error:
        raise ValueError(
            "El monto debe ser un número válido."
        ) from error

    if monto <= 0:
        raise ValueError(
            "El monto debe ser mayor que cero."
        )

    return monto.quantize(Decimal("0.01"))


def total_ingresos(pagos, fecha=None):
    """Suma pagos; si se indica una fecha, considera únicamente ese día."""
    fecha_objetivo = (
        fecha.strftime("%d/%m/%Y")
        if isinstance(fecha, date)
        else fecha
    )

    total = Decimal("0.00")

    for pago in pagos:
        if fecha_objetivo and pago.get("fecha_pago") != fecha_objetivo:
            continue

        total += convertir_monto(
            pago["monto"]
        )

    return total


def turno_ya_pagado(pagos, turno, ignorar_indice=None):
    return any(
        indice != ignorar_indice
        and pago.get("turno") == turno
        for indice, pago in enumerate(pagos)
    )


class PaginaPagos(PaginaABM):
    titulo = "Gestión de Pagos"
    subtitulo = "Registro de cobros asociados de manera única a cada turno."

    columnas = [
        ("turno", "Turno"),
        ("monto", "Monto"),
        ("fecha_pago", "Fecha de pago"),
        ("metodo_pago", "Método de pago"),
    ]

    datos_iniciales = []
    campo_busqueda = "turno"
    campos_fecha = ["fecha_pago"]

    def __init__(self, contenedor):
        self.turnos_ids = {}

        self.opciones_desplegables = {
            "turno": self._opciones_turnos_bd,
            "metodo_pago": METODOS_PAGO,
        }

        try:
            self.datos_iniciales = self._obtener_pagos_bd()

        except psycopg2.Error as error:
            self.datos_iniciales = []

            messagebox.showerror(
                "Error de conexión",
                (
                    "No se pudieron cargar los pagos desde PostgreSQL.\n\n"
                    f"{error}"
                ),
            )

        super().__init__(contenedor)

    def _crear_etiqueta_turno(
        self,
        id_turno,
        mascota,
        fecha,
        hora
    ):
        return (
            f"Turno #{id_turno} - "
            f"{fecha.strftime('%d/%m/%Y')} "
            f"{hora.strftime('%H:%M')} - "
            f"{mascota}"
        )

    def _opciones_turnos_bd(self):
        """
        Obtiene de PostgreSQL solamente los turnos
        que todavía no tienen un pago asociado.
        """
        turnos = pago_dao.listar_turnos_sin_pago()

        self.turnos_ids = {}

        for id_turno, mascota, fecha, hora in turnos:

            etiqueta = self._crear_etiqueta_turno(
                id_turno,
                mascota,
                fecha,
                hora
            )

            self.turnos_ids[etiqueta] = id_turno

        if (
            self.fila_seleccionada is not None
            and self.fila_seleccionada < len(self.datos)
        ):
            pago_actual = self.datos[
                self.fila_seleccionada
            ]

            self.turnos_ids[
                pago_actual["turno"]
            ] = pago_actual["id_turno"]

        return list(
            self.turnos_ids.keys()
        )

    def _obtener_pagos_bd(self):
        pagos = []

        for fila in pago_dao.listar():

            (
                id_pago,
                id_turno,
                mascota,
                fecha_turno,
                hora_turno,
                monto,
                fecha_pago,
                metodo_pago,
            ) = fila

            etiqueta = self._crear_etiqueta_turno(
                id_turno,
                mascota,
                fecha_turno,
                hora_turno
            )

            pagos.append(
                {
                    "id_pago": id_pago,
                    "id_turno": id_turno,
                    "turno": etiqueta,
                    "monto": f"{monto:.2f}",
                    "fecha_pago": fecha_pago.strftime("%d/%m/%Y"),
                    "metodo_pago": metodo_pago,
                }
            )

        return pagos

    def _recargar_pagos(self):
        """
        Vuelve a consultar PostgreSQL para actualizar
        los datos mostrados en pantalla.
        """
        self.datos = self._obtener_pagos_bd()
        self._refrescar_listado()

    def _al_presionar_nuevo(self):
        super()._al_presionar_nuevo()

        self.variables["fecha_pago"].set(
            datetime.now().strftime("%d/%m/%Y")
        )

    def _validar_datos(self, valores):
        if not super()._validar_datos(valores):
            return False

        try:
            monto = convertir_monto(
                valores["monto"]
            )

        except ValueError as error:
            messagebox.showerror(
                "Monto inválido",
                str(error),
            )
            return False

        valores["monto"] = f"{monto:.2f}"

        return True

    def _al_presionar_guardar(self):
        valores = {
            clave: variable.get().strip()
            for clave, variable in self.variables.items()
        }

        if not self._validar_datos(valores):
            return

        try:
       
            self._opciones_turnos_bd()

            id_turno = self.turnos_ids[
                valores["turno"]
            ]

            monto = convertir_monto(
                valores["monto"]
            )

            fecha_pago = datetime.strptime(
                valores["fecha_pago"],
                "%d/%m/%Y"
            )

          
            if self.fila_seleccionada is None:

                pago_dao.insertar(
                    monto=monto,
                    fecha_pago=fecha_pago,
                    metodo_pago=valores["metodo_pago"],
                    id_turno=id_turno,
                )

                mensaje = "Pago registrado correctamente."

    
            else:
                pago = self.datos[
                    self.fila_seleccionada
                ]

                pago_dao.actualizar(
                    id_pago=pago["id_pago"],
                    monto=monto,
                    fecha_pago=fecha_pago,
                    metodo_pago=valores["metodo_pago"],
                    id_turno=id_turno,
                )

                mensaje = "Pago actualizado correctamente."

            messagebox.showinfo(
                "Listo",
                mensaje,
            )

            self._recargar_pagos()
            self._mostrar_vista_listado()

        except errors.UniqueViolation:
            messagebox.showerror(
                "Turno ya abonado",
                (
                    "Ese turno ya tiene un pago registrado. "
                    "La relación entre Turno y Pago es 1 a 1."
                ),
            )

        except psycopg2.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                (
                    "No se pudo guardar el pago.\n\n"
                    f"{error}"
                ),
            )

    def _al_presionar_eliminar(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Nada seleccionado",
                "Elegí un pago del listado para eliminar.",
            )
            return

        indice = int(
            seleccion[0]
        )

        pago = self.datos[
            indice
        ]

        confirmar = messagebox.askyesno(
            "Eliminar pago",
            (
                "¿Seguro que querés eliminar este pago?\n\n"
                "Esta acción no se puede deshacer."
            ),
        )

        if not confirmar:
            return

        try:
            pago_dao.eliminar(
                pago["id_pago"]
            )

            messagebox.showinfo(
                "Pago eliminado",
                "El pago fue eliminado correctamente.",
            )

            self._recargar_pagos()

        except psycopg2.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                (
                    "No se pudo eliminar el pago.\n\n"
                    f"{error}"
                ),
            )