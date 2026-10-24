# pyright: reportOptionalMemberAccess=false
from tkinter import messagebox, ttk

from interfaz.paginas.base import PaginaABM
try:
    import psycopg2
    from psycopg2 import errors
    from datos import cliente_dao
except ImportError:
    cliente_dao = None

# Datos de ejemplo en memoria
CLIENTES_EJEMPLO = [
    {"nombre": "Carlos", "apellido": "Gómez", "telefono": "351-555-0110", "email": "carlos.gomez@mail.com"},
    {"nombre": "Ana", "apellido": "Ferreyra", "telefono": "351-555-0142", "email": "ana.ferreyra@mail.com"},
    {"nombre": "Marcos", "apellido": "Díaz", "telefono": "351-555-0198", "email": "marcos.diaz@mail.com"},
    {"nombre": "Lucía", "apellido": "Romero", "telefono": "351-555-0233", "email": "lucia.romero@mail.com"},
    {"nombre": "Martín", "apellido": "Sosa", "telefono": "351-555-0371", "email": "martin.sosa@mail.com"},
    {"nombre": "Valeria", "apellido": "Benítez", "telefono": "351-555-0455", "email": "valeria.benitez@mail.com"},
    {"nombre": "Esteban", "apellido": "Torres", "telefono": "351-555-0512", "email": "esteban.torres@mail.com"},
    {"nombre": "Camila", "apellido": "Navarro", "telefono": "351-555-0689", "email": "camila.navarro@mail.com"},
    {"nombre": "Federico", "apellido": "Castro", "telefono": "351-555-0744", "email": "federico.castro@mail.com"},
    {"nombre": "Mariana", "apellido": "Herrera", "telefono": "351-555-0820", "email": "mariana.herrera@mail.com"},
    {"nombre": "Gonzalo", "apellido": "Paz", "telefono": "351-555-0911", "email": "gonzalo.paz@mail.com"},
    {"nombre": "Florencia", "apellido": "Medina", "telefono": "351-555-1033", "email": "flor.medina@mail.com"},
    {"nombre": "Agustín", "apellido": "Vega", "telefono": "351-555-1178", "email": "agustin.vega@mail.com"},
    {"nombre": "Sofía", "apellido": "Ríos", "telefono": "351-555-1240", "email": "sofia.rios@mail.com"},
    {"nombre": "Joaquín", "apellido": "Molina", "telefono": "351-555-1399", "email": "joaquin.molina@mail.com"},
]
def etiqueta_cliente(cliente):
    """Texto con el que se muestra un cliente en los desplegables"""
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
    datos_iniciales = CLIENTES_EJEMPLO
    campo_busqueda = "apellido"

    usa_base = False  # True cuando los datos vienen de PostgreSQL; False = datos de ejemplo en memoria

    # carga desde la base
    def _cargar_datos(self):
        """Lee los clientes de la base (con el texto de búsqueda, si hay). Si no hay conexión, usa los de ejemplo."""
        if cliente_dao is not None:
            texto = self.texto_busqueda.get().strip()
            try:
                filas = cliente_dao.buscar(texto) if texto else cliente_dao.listar()
            except psycopg2.Error:
                filas = None
            if filas is not None:
                claves = ("id", "nombre", "apellido", "telefono", "email")
                self.datos = [dict(zip(claves, fila)) for fila in filas]
                self.usa_base = True
                return
        self.datos = self.datos_iniciales
        self.usa_base = False

    def _mostrar_estado_conexion(self):
        """Cartelito que avisa de dónde salen los datos."""
        if not hasattr(self, "lbl_estado"):
            self.lbl_estado = ttk.Label(self.marco_listado, style="Subtitulo.TLabel")
            self.lbl_estado.pack(anchor="w", padx=24, pady=(0, 6), before=self.marco_listado.winfo_children()[0])
        self.lbl_estado.configure(
            text="● Conectado a la base de datos PostgreSQL."
            if self.usa_base
            else "● Sin conexión a la base: se muestran datos de ejemplo y los cambios no se guardan."
        )

    def _refrescar_listado(self):
        self._cargar_datos()
        self._mostrar_estado_conexion()
        super()._refrescar_listado()

    # validaciones
    def _validar_datos(self, valores):
        if not super()._validar_datos(valores):
            return False
        if "@" not in valores["email"]:
            messagebox.showwarning("Email inválido", "Revisá el email ingresado.")
            return False
        return True

    # guardar (INSERT / UPDATE)
    def _al_presionar_guardar(self):
        if not self.usa_base:
            return super()._al_presionar_guardar()

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
        self._mostrar_vista_listado()

    # eliminar (DELETE)
    def _al_presionar_eliminar(self):
        if not self.usa_base:
            return self._eliminar_de_ejemplo()

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

        self._refrescar_listado()

    def _eliminar_de_ejemplo(self):
        """Eliminar en modo sin base (datos de ejemplo): se controla contra las mascotas de ejemplo."""
        seleccion = self.tabla.selection()
        if seleccion:
            from interfaz.paginas.mascotas import MASCOTAS_EJEMPLO
            etiqueta = etiqueta_cliente(self.datos[int(seleccion[0])])
            if any(m["dueno"] == etiqueta for m in MASCOTAS_EJEMPLO):
                messagebox.showwarning("No se puede eliminar", f"{etiqueta} tiene mascotas registradas. Eliminá o reasigná sus mascotas primero.")
                return
        super()._al_presionar_eliminar()
