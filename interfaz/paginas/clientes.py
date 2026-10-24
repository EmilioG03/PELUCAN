import psycopg2
from psycopg2 import errors
from tkinter import messagebox, ttk

from interfaz.paginas.base import PaginaABM
from datos import cliente_dao


def etiqueta_cliente(cliente):
    """Texto con el que se muestra un cliente (igual que en los desplegables)."""
    return f"{cliente['nombre']} {cliente['apellido']}"


class PaginaClientes(PaginaABM):
    titulo = "Listado de Clientes"
    subtitulo = "Administración y búsqueda de clientes registrados en el sistema."

    columnas = [
        ("nombre", "Nombre"),
        ("apellido", "Apellido"),
        ("telefono", "Teléfono"),
        ("email", "Email"),
    ]

    datos_iniciales = []
    campo_busqueda = "apellido"

    # True si la última consulta a PostgreSQL funcionó
    conectado = False

    def __init__(self, contenedor):
        # Se leen los datos ANTES de armar la pantalla (igual que Peluqueros).
        self._cargar_datos(avisar=True)
        super().__init__(contenedor)

    # ------------------------------------------------------------------
    # Carga de datos: solo desde PostgreSQL, nunca datos inventados
    # ------------------------------------------------------------------
    def _cargar_datos(self, avisar=False):
        claves = ("id", "nombre", "apellido", "telefono", "email")
        try:
            self.datos = [dict(zip(claves, fila)) for fila in cliente_dao.listar()]
            self.conectado = True
        except psycopg2.Error as error:
            self.datos = []
            self.conectado = False
            if avisar:
                messagebox.showerror(
                    "Sin conexión a la base de datos",
                    "No se pudieron cargar los clientes desde PostgreSQL.\n"
                    "Verificá que el servidor esté encendido y que los datos del "
                    f"archivo .env sean correctos.\n\n{error}",
                )
        self.datos_iniciales = self.datos

    def _recargar(self):
        """Vuelve a consultar PostgreSQL y actualiza listado y cartel de estado."""
        self._cargar_datos(avisar=True)
        self._mostrar_estado_conexion()
        self._refrescar_listado()

    def construir_contenido(self):
        super().construir_contenido()
        self._mostrar_estado_conexion()

    def _mostrar_estado_conexion(self):
        """Cartelito que avisa si hay conexión con la base."""
        if not hasattr(self, "lbl_estado"):
            self.lbl_estado = ttk.Label(self.marco_listado, style="Subtitulo.TLabel")
            self.lbl_estado.pack(
                anchor="w", padx=24, pady=(0, 6),
                before=self.marco_listado.winfo_children()[0],
            )
        self.lbl_estado.configure(
            text="● Conectado a la base de datos PostgreSQL."
            if self.conectado
            else "● Sin conexión a la base de datos PostgreSQL. No hay datos para mostrar."
        )

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------
    def _validar_datos(self, valores):
        if not super()._validar_datos(valores):
            return False
        if "@" not in valores["email"]:
            messagebox.showwarning("Email inválido", "Revisá el email ingresado.")
            return False
        return True

    # ------------------------------------------------------------------
    # Guardar (INSERT / UPDATE)
    # ------------------------------------------------------------------
    def _al_presionar_guardar(self):
        valores = {clave: var.get().strip() for clave, var in self.variables.items()}
        if not self._validar_datos(valores):
            return

        datos = (valores["nombre"], valores["apellido"], valores["telefono"], valores["email"])
        try:
            if self.fila_seleccionada is None:
                cliente_dao.insertar(*datos)
                aviso = "Registro agregado correctamente."
            else:
                cliente_dao.actualizar(self.datos[self.fila_seleccionada]["id"], *datos)
                aviso = "Registro actualizado correctamente."
        except errors.UniqueViolation as error:
            if "correo" in (error.diag.constraint_name or ""):
                messagebox.showerror("Email duplicado", f"Ya existe un cliente con el email {valores['email']}.")
            else:
                messagebox.showerror("Teléfono duplicado", f"Ya existe un cliente con el teléfono {valores['telefono']}.")
            return
        except psycopg2.Error as error:
            messagebox.showerror("Error de base de datos", f"No se pudo guardar el cliente:\n{error}")
            return

        messagebox.showinfo("Listo", aviso)
        self._recargar()
        self._mostrar_vista_listado()

    # ------------------------------------------------------------------
    # Eliminar (DELETE)
    # ------------------------------------------------------------------
    def _al_presionar_eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Nada seleccionado", "Elegí un registro del listado para eliminar.")
            return

        cliente = self.datos[int(seleccion[0])]
        if not messagebox.askyesno(
            "Eliminar",
            "¿Seguro que querés eliminar este registro? Esta acción no se puede deshacer.",
        ):
            return

        try:
            cliente_dao.eliminar(cliente["id"])
        except (errors.ForeignKeyViolation, errors.RestrictViolation):
            messagebox.showwarning(
                "No se puede eliminar",
                f"{etiqueta_cliente(cliente)} tiene mascotas registradas. Eliminá o reasigná sus mascotas primero.",
            )
            return
        except psycopg2.Error as error:
            messagebox.showerror("Error de base de datos", f"No se pudo eliminar el cliente:\n{error}")
            return

        self._recargar()
