from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from tkinter import messagebox

from interfaz.paginas.base import PaginaABM
from interfaz.paginas.turnos import TURNOS_EJEMPLO


METODOS_PAGO = ("Efectivo", "Transferencia", "Tarjeta")


def etiqueta_turno(turno, indice):
    """Devuelve una referencia legible y estable para seleccionar un turno."""
    return (
        f"Turno #{indice + 1} - {turno['fecha']} {turno['hora']} - "
        f"{turno['mascota']}"
    )


def opciones_turnos():
    return [etiqueta_turno(turno, indice) for indice, turno in enumerate(TURNOS_EJEMPLO)]


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
        raise ValueError("El monto debe ser un número válido.") from error

    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero.")
    return monto.quantize(Decimal("0.01"))


def total_ingresos(pagos, fecha=None):
    """Suma pagos; si se indica una fecha, considera únicamente ese día."""
    fecha_objetivo = fecha.strftime("%d/%m/%Y") if isinstance(fecha, date) else fecha
    total = Decimal("0.00")
    for pago in pagos:
        if fecha_objetivo and pago.get("fecha_pago") != fecha_objetivo:
            continue
        total += convertir_monto(pago["monto"])
    return total


def turno_ya_pagado(pagos, turno, ignorar_indice=None):
    return any(
        indice != ignorar_indice and pago.get("turno") == turno
        for indice, pago in enumerate(pagos)
    )


PAGOS_EJEMPLO = [
    {
        "turno": etiqueta_turno(TURNOS_EJEMPLO[0], 0),
        "monto": "12000.00",
        "fecha_pago": "31/08/2026",
        "metodo_pago": "Efectivo",
    },
    {
        "turno": etiqueta_turno(TURNOS_EJEMPLO[1], 1),
        "monto": "18000.00",
        "fecha_pago": "31/08/2026",
        "metodo_pago": "Transferencia",
    },
    {
        "turno": etiqueta_turno(TURNOS_EJEMPLO[8], 8),
        "monto": "7000.00",
        "fecha_pago": "31/08/2026",
        "metodo_pago": "Tarjeta",
    },
]


class PaginaPagos(PaginaABM):
    titulo = "Gestión de Pagos"
    subtitulo = "Registro de cobros asociados de manera única a cada turno."
    columnas = [
        ("turno", "Turno"),
        ("monto", "Monto"),
        ("fecha_pago", "Fecha de pago"),
        ("metodo_pago", "Método de pago"),
    ]
    datos_iniciales = PAGOS_EJEMPLO
    campo_busqueda = "turno"
    campos_fecha = ["fecha_pago"]
    opciones_desplegables = {
        "turno": opciones_turnos,
        "metodo_pago": METODOS_PAGO,
    }

    def _al_presionar_nuevo(self):
        super()._al_presionar_nuevo()
        self.variables["fecha_pago"].set(datetime.now().strftime("%d/%m/%Y"))

    def _validar_datos(self, valores):
        if not super()._validar_datos(valores):
            return False

        try:
            monto = convertir_monto(valores["monto"])
        except ValueError as error:
            messagebox.showerror("Monto inválido", str(error))
            return False

        if turno_ya_pagado(self.datos, valores["turno"], self.fila_seleccionada):
            messagebox.showerror(
                "Turno ya abonado",
                "Ese turno ya tiene un pago registrado. La relación es 1 a 1.",
            )
            return False

        valores["monto"] = f"{monto:.2f}"
        return True
