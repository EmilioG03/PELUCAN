import tkinter as tk

from interfaz.estilos import configurar_estilos, ANCHO_SIDEBAR
from interfaz.header import HeaderPeluCan
from interfaz.sidebar import Sidebar
from interfaz.navegador import NavegadorPaginas
from interfaz.paginas import PaginaInicio, PaginaClientes, PaginaMascotas, PaginaTurnos

SECCIONES = {
    "Inicio": PaginaInicio,
    "Clientes": PaginaClientes,
    "Mascotas": PaginaMascotas,
    "Turnos": PaginaTurnos,
}

class VentanaPrincipal(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("PeluCan – Sistema de Gestión")
        self.geometry("1000x600")
        self.minsize(820, 520)

        configurar_estilos(self)

        self._crear_header()
        self._crear_cuerpo()

        self.mostrar_pagina("Inicio")

    def _crear_header(self):
        header = HeaderPeluCan(self)
        header.pack(side="top", fill="x")

    def _crear_cuerpo(self):
        """Arma el sidebar y el navegador y los conecta entre si"""
        cuerpo = tk.Frame(self)
        cuerpo.pack(side="top", fill="both", expand=True)

        self.navegador = NavegadorPaginas(cuerpo)
        self.sidebar = Sidebar(
            cuerpo,
            secciones=list(SECCIONES.keys()),
            on_seleccionar=self.mostrar_pagina,
            ancho=ANCHO_SIDEBAR,
        )

        self.sidebar.pack(side="left", fill="y")
        self.navegador.pack(side="left", fill="both", expand=True)

        self._registrar_paginas()

    def _registrar_paginas(self):
        """Crea una instancia de cada página y la registra en el navegador."""
        for nombre_seccion, clase_pagina in SECCIONES.items():
            pagina = clase_pagina(self.navegador.area)
            self.navegador.registrar_pagina(nombre_seccion, pagina)

    def mostrar_pagina(self, nombre_seccion):
        self.navegador.mostrar(nombre_seccion)
        self.sidebar.marcar_activo(nombre_seccion)
        
        pagina = self.navegador._paginas.get(nombre_seccion)
        if pagina and hasattr(pagina, "actualizar_metricas"):
            pagina.actualizar_metricas()
