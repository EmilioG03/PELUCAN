import psycopg2
from psycopg2 import errors
from tkinter import messagebox

from interfaz.paginas.base import PaginaABM
from datos import mascota_dao


def etiqueta_mascota(mascota):
    """Texto con el que se muestra una mascota en los desplegables."""
    return f"{mascota['nombre']} ({mascota['raza']})"


class PaginaMascotas(PaginaABM):
    titulo = "Listado de Mascotas"
    subtitulo = "Administración y búsqueda general de mascotas registradas."

    columnas = [
        ("nombre", "Nombre"),
        ("raza", "Raza"),
        ("edad", "Edad"),
        ("tamano", "Tamaño"),
        ("dueno", "Dueño/a"),
        ("observaciones", "Observaciones"),
    ]

    datos_iniciales = []
    campo_busqueda = "nombre"

    def __init__(self, contenedor):
        self.clientes_ids = {}

        self.opciones_desplegables = {
            "tamano": [
                "Pequeño",
                "Mediano",
                "Grande",
            ],
            "dueno": self._opciones_clientes,
        }

        try:
            self.datos_iniciales = self._obtener_mascotas_bd()
        except psycopg2.Error as error:
            self.datos_iniciales = []

            messagebox.showerror(
                "Error de conexión",
                (
                    "No se pudieron cargar las mascotas desde PostgreSQL.\n\n"
                    f"{error}"
                ),
            )

        super().__init__(contenedor)

    def _opciones_clientes(self):
        """
        Obtiene los clientes reales desde PostgreSQL
        para mostrarlos en el desplegable Dueño/a.
        """
        clientes = mascota_dao.listar_clientes()

        self.clientes_ids = {
            nombre: id_cliente
            for id_cliente, nombre in clientes
        }

        return list(self.clientes_ids.keys())

    def _obtener_mascotas_bd(self):
        """
        Obtiene las mascotas desde PostgreSQL y las transforma
        al formato utilizado por PaginaABM.
        """
        mascotas = []

        for fila in mascota_dao.listar():
            (
                id_mascota,
                nombre,
                raza,
                edad,
                tamano,
                dueno,
                observaciones,
                id_cliente,
            ) = fila

            mascotas.append(
                {
                    "id_mascota": id_mascota,
                    "nombre": nombre,
                    "raza": raza,
                    "edad": str(edad) if edad is not None else "",
                    "tamano": tamano,
                    "dueno": dueno,
                    "observaciones": observaciones,
                    "id_cliente": id_cliente,
                }
            )

        return mascotas

    def _recargar_mascotas(self):
        """
        Vuelve a consultar PostgreSQL y actualiza el listado.
        """
        self.datos = self._obtener_mascotas_bd()
        self._refrescar_listado()

    def _validar_datos(self, valores):
        if not super()._validar_datos(valores):
            return False

        try:
            edad = int(valores["edad"])

        except ValueError:
            messagebox.showerror(
                "Edad inválida",
                "La edad debe ser un número entero.",
            )
            return False

        if edad < 0:
            messagebox.showerror(
                "Edad inválida",
                "La edad de la mascota no puede ser negativa.",
            )
            return False

        return True

    def _al_presionar_guardar(self):
        """
        Inserta o actualiza una mascota en PostgreSQL.
        """
        valores = {
            clave: variable.get().strip()
            for clave, variable in self.variables.items()
        }

        if not self._validar_datos(valores):
            return

        try:
          
            self._opciones_clientes()

            id_cliente = self.clientes_ids[valores["dueno"]]

         
            if self.fila_seleccionada is None:
                mascota_dao.insertar(
                    nombre=valores["nombre"],
                    raza=valores["raza"],
                    edad=int(valores["edad"]),
                    tamano=valores["tamano"],
                    observaciones=valores["observaciones"],
                    id_cliente=id_cliente,
                )

                mensaje = "Mascota registrada correctamente."

         
            else:
                mascota = self.datos[self.fila_seleccionada]

                mascota_dao.actualizar(
                    id_mascota=mascota["id_mascota"],
                    nombre=valores["nombre"],
                    raza=valores["raza"],
                    edad=int(valores["edad"]),
                    tamano=valores["tamano"],
                    observaciones=valores["observaciones"],
                    id_cliente=id_cliente,
                )

                mensaje = "Mascota actualizada correctamente."

            messagebox.showinfo(
                "Listo",
                mensaje,
            )

            self._recargar_mascotas()
            self._mostrar_vista_listado()

        except psycopg2.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                (
                    "No se pudo guardar la mascota.\n\n"
                    f"{error}"
                ),
            )

    def _al_presionar_eliminar(self):
        """
        Elimina una mascota de PostgreSQL.
        Si tiene turnos asociados, la FK impide eliminarla.
        """
        seleccion = self.tabla.selection()

        if not seleccion:
            messagebox.showwarning(
                "Nada seleccionado",
                "Elegí una mascota del listado para eliminar.",
            )
            return

        indice = int(seleccion[0])
        mascota = self.datos[indice]

        confirmar = messagebox.askyesno(
            "Eliminar mascota",
            (
                f"¿Seguro que querés eliminar a {mascota['nombre']}?\n\n"
                "Esta acción no se puede deshacer."
            ),
        )

        if not confirmar:
            return

        try:
            mascota_dao.eliminar(
                mascota["id_mascota"]
            )

            messagebox.showinfo(
                "Mascota eliminada",
                "La mascota fue eliminada correctamente.",
            )

            self._recargar_mascotas()

        except (
            errors.ForeignKeyViolation,
            errors.RestrictViolation,
        ):
            messagebox.showwarning(
                "No se puede eliminar",
                (
                    f"{mascota['nombre']} tiene turnos registrados.\n"
                    "No puede eliminarse mientras tenga turnos asociados."
                ),
            )

        except psycopg2.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                (
                    "No se pudo eliminar la mascota.\n\n"
                    f"{error}"
                ),
            )