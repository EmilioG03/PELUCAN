import tkinter as tk
from tkinter import ttk

from interfaz.paginas import (
    PaginaInicio,
    PaginaClientes,
    PaginaMascotas,
    PaginaTurnos,
    PaginaServicios,
)

#Colores y medidas de la internaz
COLOR_HEADER = "#1a5c4a"
COLOR_SIDEBAR = "#e7f5ee"
COLOR_SIDEBAR_ACTIVO = "#1a5c4a"
COLOR_TEXTO = "#26312d"
COLOR_MUTED = "#6b7a74"
COLOR_BLANCO = "#ffffff"
ANCHO_SIDEBAR = 170


class VentanaPrincipal(tk.Tk):
    """Ventana principal que gestiona el layout general y el cambio de pantalla.
    """
    def __init__(self):
        super().__init__()
        self.title("PeluCan – Sistema de Gestión")
        self.geometry("1000x800")
        self.minsize(820, 520)
        self.configure(bg=COLOR_BLANCO)
#Inicializacion de la interfaz
        self._configurar_estilos()
        self._crear_header()
        self._crear_cuerpo() 
        self._crear_paginas()
#Pagina inicial por defecto
        self.mostrar_pagina("Inicio")

    def _configurar_estilos(self):
        """Configuracion de estilos ttk para botones, marcos y etiquetas
        """
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Header.TFrame", background=COLOR_HEADER)
        estilo.configure(
            "Header.TLabel",
            background=COLOR_HEADER,
            foreground=COLOR_BLANCO,
            font=("Segoe UI", 13, "bold"),
        )

        estilo.configure("Sidebar.TFrame", background=COLOR_SIDEBAR)
        estilo.configure(
            "Sidebar.TButton",
            background=COLOR_SIDEBAR,
            foreground=COLOR_TEXTO,
            borderwidth=0,
            anchor="w",
            font=("Segoe UI", 10),
            padding=(18, 10),
        )
        estilo.map(
            "Sidebar.TButton",
            background=[("active", "#d7ede1")],
        )

        estilo.configure(
            "SidebarActivo.TButton",
            background=COLOR_SIDEBAR_ACTIVO,
            foreground=COLOR_BLANCO,
            borderwidth=0,
            anchor="w",
            font=("Segoe UI", 10, "bold"),
            padding=(18, 10),
        )
        estilo.map(
            "SidebarActivo.TButton",
            background=[("active", COLOR_SIDEBAR_ACTIVO)],
        )

        estilo.configure("Contenido.TFrame", background=COLOR_BLANCO)
        estilo.configure(
            "TituloPagina.TLabel",
            background=COLOR_BLANCO,
            foreground=COLOR_TEXTO,
            font=("Segoe UI", 15, "bold"),
        )
        estilo.configure(
            "Subtitulo.TLabel",
            background=COLOR_BLANCO,
            foreground=COLOR_MUTED,
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "Placeholder.TLabel",
            background=COLOR_BLANCO,
            foreground=COLOR_MUTED,
            font=("Segoe UI", 9, "italic"),
        )

    def _crear_header(self):
        """Barra superior con el nombre del sistema
        """
        header = ttk.Frame(self, style="Header.TFrame", height=48)
        header.pack(side="top", fill="x")

        ttk.Label(
            header, text="PeluCan – Sistema de Gestión", style="Header.TLabel"
        ).pack(side="left", padx=18, pady=12)

    def _crear_cuerpo(self):
        """Estructura principal -> menu lateral a la izquierda y contenedor de vistas a la derecha
        """
        cuerpo = ttk.Frame(self, style="Contenido.TFrame")
        cuerpo.pack(side="top", fill="both", expand=True)

        #Menu lateral
        self.sidebar = ttk.Frame(cuerpo, style="Sidebar.TFrame", width=ANCHO_SIDEBAR)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.secciones = ["Inicio", "Clientes", "Mascotas", "Turnos", "Servicios"]
        self.botones_sidebar = {}

        for nombre_seccion in self.secciones:
            boton = ttk.Button(
                self.sidebar,
                text=nombre_seccion,
                style="Sidebar.TButton",
                command=lambda s=nombre_seccion: self.mostrar_pagina(s),
            )
            boton.pack(fill="x")
            self.botones_sidebar[nombre_seccion] = boton

        #Contenedor para las paginas
        self.contenedor_paginas = ttk.Frame(cuerpo, style="Contenido.TFrame")
        self.contenedor_paginas.pack(side="left", fill="both", expand=True)

        self.contenedor_paginas.grid_rowconfigure(0, weight=1)
        self.contenedor_paginas.grid_columnconfigure(0, weight=1)

    def _crear_paginas(self):
        """Instancia todas las vistas superpuestas en la misma celda de la grilla
        """
        clases_de_pagina = {
            "Inicio": PaginaInicio,
            "Clientes": PaginaClientes,
            "Mascotas": PaginaMascotas,
            "Turnos": PaginaTurnos,
            "Servicios": PaginaServicios,
        }

        self.paginas = {}
        for nombre_seccion, clase_pagina in clases_de_pagina.items():
            pagina = clase_pagina(self.contenedor_paginas)
            pagina.grid(row=0, column=0, sticky="nsew")
            self.paginas[nombre_seccion] = pagina

    def mostrar_pagina(self, nombre_seccion):
        """
        Pone al frente la pantalla solicitada y actualiza el boton activo del menu
        """
        if nombre_seccion not in self.paginas:
            return 

        self.paginas[nombre_seccion].tkraise()

        for nombre, boton in self.botones_sidebar.items():
            if nombre == nombre_seccion:
                boton.configure(style="SidebarActivo.TButton")
            else:
                boton.configure(style="Sidebar.TButton")
