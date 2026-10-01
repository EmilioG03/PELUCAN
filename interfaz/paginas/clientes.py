from tkinter import messagebox
from interfaz.paginas.base import PaginaABM

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

    def _al_presionar_eliminar(self):
        seleccion = self.tabla.selection()
        if seleccion:
            from interfaz.paginas.mascotas import MASCOTAS_EJEMPLO
            etiqueta = etiqueta_cliente(self.datos[int(seleccion[0])])
            if any(m["dueno"] == etiqueta for m in MASCOTAS_EJEMPLO):
                messagebox.showwarning("No se puede eliminar", f"{etiqueta} tiene mascotas registradas. Eliminá o reasigná sus mascotas primero.")
                return
        super()._al_presionar_eliminar()