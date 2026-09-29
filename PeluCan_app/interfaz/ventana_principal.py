import tkinter as tk
from tkinter import ttk

from interfaz.estilos import (
    ANCHO_SIDEBAR,
    COLOR_BLANCO,
    configurar_estilos,
)
from interfaz.header import HeaderPeluCan
from interfaz.navegador import NavegadorPaginas
from interfaz.paginas import (
    PaginaClientes,
    PaginaInicio,
    PaginaMascotas,
    PaginaServicios,
    PaginaTurnos,
)
from interfaz.sidebar import Sidebar


class VentanaPrincipal(tk.Tk):
    """Ventana principal del sistema de gestión PeluCan."""

    SECCIONES = (
        "Inicio",
        "Clientes",
        "Mascotas",
        "Turnos",
        "Servicios",
    )

    CLASES_DE_PAGINA = {
        "Inicio": PaginaInicio,
        "Clientes": PaginaClientes,
        "Mascotas": PaginaMascotas,
        "Turnos": PaginaTurnos,
        "Servicios": PaginaServicios,
    }

    def __init__(self):
        super().__init__()

        self.title("PeluCan – Sistema de Gestión")
        self.geometry("1000x800")
        self.minsize(820, 520)
        self.configure(bg=COLOR_BLANCO)

        configurar_estilos(self)
        self._crear_layout()
        self._registrar_paginas()
        self.mostrar_pagina("Inicio")

    def _crear_layout(self):
        """Crea la cabecera, el menú lateral y el área de páginas."""

        header = HeaderPeluCan(self)
        header.pack(side="top", fill="x")

        cuerpo = ttk.Frame(self, style="Contenido.TFrame")
        cuerpo.pack(side="top", fill="both", expand=True)

        self.sidebar = Sidebar(
            contenedor=cuerpo,
            secciones=self.SECCIONES,
            on_seleccionar=self.mostrar_pagina,
            ancho=ANCHO_SIDEBAR,
        )
        self.sidebar.pack(side="left", fill="y")

        self.navegador = NavegadorPaginas(cuerpo)
        self.navegador.pack(side="left", fill="both", expand=True)

    def _registrar_paginas(self):
        """Crea las páginas y las registra en el navegador."""

        for nombre, clase_pagina in self.CLASES_DE_PAGINA.items():
            pagina = clase_pagina(self.navegador.area)
            self.navegador.registrar_pagina(nombre, pagina)

    def mostrar_pagina(self, nombre):
        """Muestra una página y actualiza el botón activo del menú."""

        if nombre not in self.CLASES_DE_PAGINA:
            return

        self.navegador.mostrar(nombre)
        self.sidebar.marcar_activo(nombre)