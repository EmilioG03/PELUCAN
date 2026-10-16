from datetime import time, datetime
from tkinter import messagebox

from interfaz.paginas.base import PaginaABM

from datos.turnos_dao import (
    listar_turnos,
    listar_mascotas,
    listar_peluqueros,
    listar_servicios,
    crear_turno,
    peluquero_disponible,
)


HORARIOS_DISPONIBLES = [
    f"{hora:02d}:{minuto:02d}"
    for hora in range(8, 20)
    for minuto in (0, 30)
]

ESTADOS_ACTIVOS = ("Pendiente", "Confirmado")


# -------------------------------------------------------------------
# DATOS DE EJEMPLO
# Se mantienen temporalmente porque pagos.py todavía depende de ellos.
# PaginaTurnos NO usa estos datos.
# -------------------------------------------------------------------

TURNOS_EJEMPLO = [
    {
        "mascota": "Luna (Caniche)",
        "servicio": "Baño completo",
        "fecha": "31/08/2026",
        "hora": "09:00",
        "estado": "Pendiente",
        "observaciones": "",
    },
    {
        "mascota": "Bruno (Labrador)",
        "servicio": "Corte + Baño",
        "fecha": "31/08/2026",
        "hora": "10:30",
        "estado": "Confirmado",
        "observaciones": "Cuidado con piel sensible",
    },
    {
        "mascota": "Toby (Cocker)",
        "servicio": "Corte de uñas",
        "fecha": "31/08/2026",
        "hora": "11:45",
        "estado": "Confirmado",
        "observaciones": "Enojo fácil",
    },
    {
        "mascota": "Milo (Beagle)",
        "servicio": "Baño sanitario",
        "fecha": "31/08/2026",
        "hora": "11:15",
        "estado": "Pendiente",
        "observaciones": "Traer toalla propia",
    },
    {
        "mascota": "Simón (Bulldog Francés)",
        "servicio": "Baño completo",
        "fecha": "31/08/2026",
        "hora": "12:00",
        "estado": "Cancelado",
        "observaciones": "Avisó por WhatsApp",
    },
    {
        "mascota": "Kira (Ovejero Alemán)",
        "servicio": "Deslanado + Baño",
        "fecha": "31/08/2026",
        "hora": "13:30",
        "estado": "Confirmado",
        "observaciones": "Trabajo de 2 horas",
    },
    {
        "mascota": "Rocco (Boxer)",
        "servicio": "Baño completo",
        "fecha": "31/08/2026",
        "hora": "14:15",
        "estado": "Pendiente",
        "observaciones": "Usar shampoo neutro",
    },
    {
        "mascota": "Lola (Golden Retriever)",
        "servicio": "Corte + Baño",
        "fecha": "31/08/2026",
        "hora": "15:00",
        "estado": "Confirmado",
        "observaciones": "Desenredo profundo",
    },
    {
        "mascota": "Bobi (Mestizo)",
        "servicio": "Baño express",
        "fecha": "31/08/2026",
        "hora": "15:45",
        "estado": "Completado",
        "observaciones": "Secador a temperatura tibia",
    },
    {
        "mascota": "Mia (Shih Tzu)",
        "servicio": "Corte higiénico",
        "fecha": "31/08/2026",
        "hora": "16:30",
        "estado": "Confirmado",
        "observaciones": "Moño rojo al terminar",
    },
    {
        "mascota": "Thor (Rottweiler)",
        "servicio": "Baño completo",
        "fecha": "31/08/2026",
        "hora": "17:15",
        "estado": "Pendiente",
        "observaciones": "Manejar con cuidado",
    },
    {
        "mascota": "Bella (Pug)",
        "servicio": "Limpieza de pliegues + Baño",
        "fecha": "31/08/2026",
        "hora": "18:00",
        "estado": "Confirmado",
        "observaciones": "",
    },
    {
        "mascota": "Zeus (Husky)",
        "servicio": "Cepillado profundo",
        "fecha": "31/08/2026",
        "hora": "18:45",
        "estado": "Pendiente",
        "observaciones": "Mucha paciencia con la cola",
    },
    {
        "mascota": "Ciro (Dachshund)",
        "servicio": "Corte de uñas + Oídos",
        "fecha": "31/08/2026",
        "hora": "19:15",
        "estado": "Completado",
        "observaciones": "Control veterinario al día",
    },
    {
        "mascota": "Nina (Schnauzer Mini)",
        "servicio": "Corte estándar",
        "fecha": "31/08/2026",
        "hora": "19:45",
        "estado": "Pendiente",
        "observaciones": "Mantener barba larga",
    },
]


# -------------------------------------------------------------------
# PÁGINA DE TURNOS
# Esta parte sí trabaja con PostgreSQL.
# -------------------------------------------------------------------

class PaginaTurnos(PaginaABM):
    titulo = "Listado de Turnos"
    subtitulo = "Administración y búsqueda general de citas programadas en el sistema."

    columnas = [
        ("mascota", "Mascota"),
        ("peluquero", "Peluquero"),
        ("servicio", "Servicio"),
        ("fecha", "Fecha"),
        ("hora", "Hora"),
        ("estado", "Estado"),
        ("observaciones", "Observaciones"),
    ]

    datos_iniciales = []
    campo_busqueda = "mascota"
    campos_fecha = ["fecha"]

    def __init__(self, contenedor):
        # Traer datos reales desde PostgreSQL
        mascotas = listar_mascotas()
        peluqueros = listar_peluqueros()
        servicios = listar_servicios()

        # Asociar lo que ve el usuario con el ID de la base
        self.mascotas_ids = {
            nombre: id_mascota
            for id_mascota, nombre in mascotas
        }

        self.peluqueros_ids = {
            nombre: id_peluquero
            for id_peluquero, nombre in peluqueros
        }

        self.servicios_ids = {
            nombre: id_servicio
            for id_servicio, nombre, duracion, precio in servicios
        }

        # Opciones de los Combobox
        self.opciones_desplegables = {
            "mascota": list(self.mascotas_ids.keys()),
            "peluquero": list(self.peluqueros_ids.keys()),
            "servicio": list(self.servicios_ids.keys()),
            "estado": [
                "Pendiente",
                "Confirmado",
                "Completado",
                "Cancelado",
            ],
            "hora": HORARIOS_DISPONIBLES,
        }

        # Cargar turnos reales
        self.datos_iniciales = self._obtener_turnos_bd()

        super().__init__(contenedor)

    def _obtener_turnos_bd(self):
        registros = []

        for turno in listar_turnos():
            (
                id_turno,
                mascota,
                peluquero,
                servicio,
                fecha,
                hora,
                estado,
                observaciones,
            ) = turno

            registros.append(
                {
                    "id_turno": id_turno,
                    "mascota": mascota,
                    "peluquero": peluquero,
                    "servicio": servicio,
                    "fecha": fecha.strftime("%d/%m/%Y"),
                    "hora": hora.strftime("%H:%M"),
                    "estado": estado,
                    "observaciones": observaciones or "",
                }
            )

        return registros

    def _recargar_turnos(self):
        self.datos = self._obtener_turnos_bd()
        self._refrescar_listado()

    def _al_presionar_guardar(self):
        valores = {
            clave: variable.get().strip()
            for clave, variable in self.variables.items()
        }

        if not self._validar_datos(valores):
            return

        # Por ahora esta evidencia integra el alta.
        if self.fila_seleccionada is not None:
            messagebox.showinfo(
                "Edición de turnos",
                "La edición de turnos todavía no está conectada a la base de datos.",
            )
            return

        try:
            fecha = datetime.strptime(
                valores["fecha"],
                "%d/%m/%Y"
            ).date()

            hora = time.fromisoformat(valores["hora"])

            id_mascota = self.mascotas_ids[valores["mascota"]]
            id_peluquero = self.peluqueros_ids[valores["peluquero"]]
            id_servicio = self.servicios_ids[valores["servicio"]]

            crear_turno(
                fecha=fecha,
                hora=hora,
                estado=valores["estado"],
                observaciones=valores["observaciones"],
                id_mascota=id_mascota,
                id_peluquero=id_peluquero,
                id_servicio=id_servicio,
            )

            messagebox.showinfo(
                "Turno registrado",
                "El turno fue registrado correctamente.",
            )

            self._recargar_turnos()
            self._mostrar_vista_listado()

        except Exception as error:
            messagebox.showerror(
                "Error al registrar turno",
                f"No se pudo guardar el turno.\n\n{error}",
            )
def _validar_datos(self, valores):
    if not super()._validar_datos(valores):
        return False

    try:
        fecha = datetime.strptime(
            valores["fecha"],
            "%d/%m/%Y"
        ).date()

        hora = time.fromisoformat(valores["hora"])

    except ValueError:
        messagebox.showerror(
            "Fecha u hora inválida",
            "Verificá la fecha y la hora ingresadas.",
        )
        return False

    # No permitir turnos nuevos en el pasado
    if (
        self.fila_seleccionada is None
        and datetime.combine(fecha, hora) < datetime.now()
    ):
        messagebox.showerror(
            "Fecha y hora pasadas",
            "No se puede agendar un turno en una fecha u hora que ya pasó.",
        )
        return False

    # Validar disponibilidad del peluquero teniendo en cuenta
    # la duración del servicio
    if (
        self.fila_seleccionada is None
        and valores["estado"] in ESTADOS_ACTIVOS
    ):
        id_peluquero = self.peluqueros_ids[valores["peluquero"]]
        id_servicio = self.servicios_ids[valores["servicio"]]

        disponible = peluquero_disponible(
            fecha=fecha,
            hora=hora,
            id_peluquero=id_peluquero,
            id_servicio=id_servicio,
        )

        if not disponible:
            messagebox.showerror(
                "Peluquero no disponible",
                (
                    f"{valores['peluquero']} ya tiene un turno "
                    "que se superpone con ese horario."
                ),
            )
            return False

    # Validar que la misma mascota no tenga otro turno
    # exactamente a la misma fecha y hora
    if valores["estado"] in ESTADOS_ACTIVOS:

        for i, turno in enumerate(self.datos):

            if (
                i == self.fila_seleccionada
                or turno["estado"] not in ESTADOS_ACTIVOS
            ):
                continue

            misma_fecha = turno["fecha"] == valores["fecha"]
            misma_hora = turno["hora"] == valores["hora"]

            if not (misma_fecha and misma_hora):
                continue

            if turno["mascota"] == valores["mascota"]:
                messagebox.showerror(
                    "Mascota con turno ocupado",
                    (
                        f"{valores['mascota']} ya tiene un turno "
                        f"el {valores['fecha']} a las {valores['hora']}."
                    ),
                )
                return False

    return True