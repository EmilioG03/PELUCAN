import psycopg2
from psycopg2 import errors
from tkinter import messagebox

from interfaz.paginas.base import PaginaABM
from datos import peluquero_dao

LIMITES = {
    "nombre": 60,
    "apellido": 60,
    "telefono": 20,
    "especialidad": 50,
}


def etiqueta_peluquero(peluquero):
    """Texto con el que se muestra un peluquero (igual que en el desplegable de Turnos)."""
    return f"{peluquero['nombre']} {peluquero['apellido']}"


class PaginaPeluqueros(PaginaABM):
    titulo = "Listado de Peluqueros"
    subtitulo = "Administración y búsqueda del personal que atiende los turnos."

    columnas = [
        ("nombre", "Nombre"),
        ("apellido", "Apellido"),
        ("telefono", "Teléfono"),
        ("especialidad", "Especialidad"),
    ]

    datos_iniciales = []
    campo_busqueda = "apellido"

    def __init__(self, contenedor):
        try:
            self.datos_iniciales = self._obtener_peluqueros_bd()
        except psycopg2.Error as error:
            self.datos_iniciales = []
            messagebox.showerror(
                "Error de conexión",
                f"No se pudieron cargar los peluqueros desde PostgreSQL.\n\n{error}",
            )

        super().__init__(contenedor)

    # Carga de datos
    def _obtener_peluqueros_bd(self):
        """Lee los peluqueros de la base y los pasa al formato de PaginaABM."""
        claves = ("id_peluquero", "nombre", "apellido", "telefono", "especialidad")
        return [dict(zip(claves, fila)) for fila in peluquero_dao.listar()]

    def _recargar_peluqueros(self):
        """Vuelve a consultar PostgreSQL y actualiza el listado."""
        self.datos = self._obtener_peluqueros_bd()
        self._refrescar_listado()

    # Validaciones
    def _validar_datos(self, valores):
        obligatorios = [
            (clave, etiqueta)
            for clave, etiqueta in self.columnas
            if clave != "especialidad"
        ]
        faltantes = [etiqueta for clave, etiqueta in obligatorios if not valores[clave]]
        if faltantes:
            messagebox.showwarning(
                "Campo incompleto",
                "Completá los siguientes campos obligatorios:\n- " + "\n- ".join(faltantes),
            )
            return False

        for clave, etiqueta in self.columnas:
            if len(valores[clave]) > LIMITES[clave]:
                messagebox.showwarning(
                    "Dato demasiado largo",
                    f"{etiqueta} admite como máximo {LIMITES[clave]} caracteres.",
                )
                return False

        if not any(caracter.isdigit() for caracter in valores["telefono"]):
            messagebox.showwarning("Teléfono inválido", "Revisá el teléfono ingresado.")
            return False

        # Turnos identifica a cada peluquero por "nombre apellido": no puede repetirse.
        nuevo = f"{valores['nombre']} {valores['apellido']}".lower()
        for indice, existente in enumerate(self.datos):
            if indice == self.fila_seleccionada:
                continue
            if etiqueta_peluquero(existente).lower() == nuevo:
                messagebox.showerror(
                    "Peluquero duplicado",
                    f"Ya existe un peluquero llamado {valores['nombre']} {valores['apellido']}.",
                )
                return False

        return True


    # Guardar (INSERT / UPDATE)
    def _al_presionar_guardar(self):
        valores = {clave: variable.get().strip() for clave, variable in self.variables.items()}
        if not self._validar_datos(valores):
            return

        datos = (
            valores["nombre"],
            valores["apellido"],
            valores["telefono"],
            valores["especialidad"],
        )

        try:
            if self.fila_seleccionada is None:
                peluquero_dao.insertar(*datos)
                aviso = "Peluquero registrado correctamente."
            else:
                id_peluquero = self.datos[self.fila_seleccionada]["id_peluquero"]
                peluquero_dao.actualizar(id_peluquero, *datos)
                aviso = "Peluquero actualizado correctamente."
        except psycopg2.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudo guardar el peluquero.\n\n{error}",
            )
            return

        messagebox.showinfo("Listo", aviso)
        self._recargar_peluqueros()
        self._mostrar_vista_listado()

    # Eliminar (DELETE)
    def _al_presionar_eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Nada seleccionado", "Elegí un peluquero del listado para eliminar.")
            return

        peluquero = self.datos[int(seleccion[0])]
        nombre = etiqueta_peluquero(peluquero)

        if not messagebox.askyesno(
            "Eliminar peluquero",
            f"¿Seguro que querés eliminar a {nombre}?\n\nEsta acción no se puede deshacer.",
        ):
            return

        try:
            peluquero_dao.eliminar(peluquero["id_peluquero"])
        except (errors.ForeignKeyViolation, errors.RestrictViolation):
            messagebox.showwarning(
                "No se puede eliminar",
                f"{nombre} tiene turnos asignados.\n"
                "No puede eliminarse mientras tenga turnos asociados.",
            )
            return
        except psycopg2.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudo eliminar el peluquero.\n\n{error}",
            )
            return

        messagebox.showinfo("Peluquero eliminado", "El peluquero fue eliminado correctamente.")
        self._recargar_peluqueros()

    # Doble clic: ficha del peluquero
    def _mostrar_detalle(self, evento):
        item_id = self.tabla.identify_row(evento.y)
        if not item_id:
            return
        peluquero = self.datos[int(item_id)]
        messagebox.showinfo(
            f"Peluquero - {etiqueta_peluquero(peluquero)}",
            f"Teléfono: {peluquero['telefono']}\n"
            f"Especialidad: {peluquero['especialidad'] or 'No especificada'}",
        )
