from datetime import time, datetime
from tkinter import messagebox

from interfaz.paginas.base import PaginaABM

from datos.turnos_dao import (
    listar_turnos,
    listar_mascotas,
    listar_peluqueros,
    listar_servicios,
    crear_turno,
    actualizar_turno,
    peluquero_disponible,
    eliminar_turno,
)


HORARIOS_DISPONIBLES = [
    f"{hora:02d}:{minuto:02d}"
    for hora in range(8, 20)
    for minuto in (0, 30)
]

ESTADOS_ACTIVOS = ("Pendiente", "Confirmado")




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
        mascotas = listar_mascotas()
        peluqueros = listar_peluqueros()
        servicios = listar_servicios()

   
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

   
        self.opciones_desplegables = {
            "mascota": self._opciones_mascotas_bd,
            "peluquero": self._opciones_peluqueros_bd,
            "servicio": self._opciones_servicios_bd,
            "estado": [
                "Pendiente",
                "Confirmado",
                "Completado",
                "Cancelado",
            ],
            "hora": HORARIOS_DISPONIBLES,
        }

        self.datos_iniciales = self._obtener_turnos_bd()

        super().__init__(contenedor)
    
    def _opciones_servicios_bd(self):
        servicios = listar_servicios()
        self.servicios_ids = {
            nombre: id_servicio
            for id_servicio, nombre, duracion, precio in servicios
        }
        return list(self.servicios_ids.keys())

    def _opciones_mascotas_bd(self):
        mascotas = listar_mascotas()

        self.mascotas_ids = {
        nombre: id_mascota
        for id_mascota, nombre in mascotas
    }

        return list(self.mascotas_ids.keys())   

    def _opciones_peluqueros_bd(self):
        """Vuelve a leer los peluqueros cada vez que se abre el formulario,
        así aparecen los que se cargaron en la página de Peluqueros."""
        peluqueros = listar_peluqueros()

        self.peluqueros_ids = {
            nombre: id_peluquero
            for id_peluquero, nombre in peluqueros
        }

        return list(self.peluqueros_ids.keys())

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

    
        try:
            fecha = datetime.strptime(
                valores["fecha"],
                "%d/%m/%Y"
            ).date()

            hora = time.fromisoformat(valores["hora"])

            id_mascota = self.mascotas_ids[valores["mascota"]]
            id_peluquero = self.peluqueros_ids[valores["peluquero"]]
            id_servicio = self.servicios_ids[valores["servicio"]]

            if self.fila_seleccionada is None:
                crear_turno(
                    fecha=fecha,
                    hora=hora,
                    estado=valores["estado"],
                    observaciones=valores["observaciones"],
                    id_mascota=id_mascota,
                    id_peluquero=id_peluquero,
                    id_servicio=id_servicio,
                )
                aviso = "El turno fue registrado correctamente."
            else:
                afectadas = actualizar_turno(
                    self.datos[self.fila_seleccionada]["id_turno"],
                    fecha=fecha,
                    hora=hora,
                    estado=valores["estado"],
                    observaciones=valores["observaciones"],
                    id_mascota=id_mascota,
                    id_peluquero=id_peluquero,
                    id_servicio=id_servicio,
                )
                if afectadas == 0:
                    messagebox.showwarning(
                        "Turno inexistente",
                        "El turno ya no existe (otra persona pudo haberlo eliminado).",
                    )
                    self._recargar_turnos()
                    self._mostrar_vista_listado()
                    return
                aviso = "El turno fue actualizado correctamente."

            messagebox.showinfo("Listo", aviso)

            self._recargar_turnos()
            self._mostrar_vista_listado()

        except Exception as error:
            messagebox.showerror(
                "Error al guardar turno",
                f"No se pudo guardar el turno.\n\n{error}",
            )
    def _al_presionar_eliminar(self):
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Nada seleccionado",
                "Elegí un turno del listado para eliminar.",
            )
            return

        indice = int(seleccion[0])
        turno = self.datos[indice]

        confirmar = messagebox.askyesno(
            "Eliminar turno",
            "¿Seguro que querés eliminar este turno?\n\n"
            "Esta acción no se puede deshacer.",
        )

        if not confirmar:
            return

        try:
            eliminar_turno(
                turno["id_turno"]
            )

            messagebox.showinfo(
                "Turno eliminado",
                "El turno fue eliminado correctamente.",
            )

            self._recargar_turnos()

        except Exception as error:
            messagebox.showerror(
                "Error al eliminar turno",
                f"No se pudo eliminar el turno.\n\n{error}",
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


        if (
            self.fila_seleccionada is None
            and datetime.combine(fecha, hora) < datetime.now()
        ):
            messagebox.showerror(
                "Fecha y hora pasadas",
                "No se puede agendar un turno en una fecha u hora que ya pasó.",
            )
            return False

        if valores["estado"] in ESTADOS_ACTIVOS:
            id_turno_actual = (
                self.datos[self.fila_seleccionada]["id_turno"]
                if self.fila_seleccionada is not None
                else None
            )
            id_peluquero = self.peluqueros_ids[valores["peluquero"]]
            id_servicio = self.servicios_ids[valores["servicio"]]

            disponible = peluquero_disponible(
                fecha=fecha,
                hora=hora,
                id_peluquero=id_peluquero,
                id_servicio=id_servicio,
                excluir_id=id_turno_actual,
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