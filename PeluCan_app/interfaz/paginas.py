from tkinter import ttk

class PaginaBase(ttk.Frame):
    """
    Clase base con la estructura comun de titulo y subtitulo para las vistas
    """

    titulo = "Página"
    subtitulo = ""

    def __init__(self, contenedor):
        super().__init__(contenedor, style="Contenido.TFrame")
        self._armar_encabezado()
        self.construir_contenido()

    def _armar_encabezado(self):
        ttk.Label(
            self, text=self.titulo, style="TituloPagina.TLabel"
        ).pack(anchor="w", padx=24, pady=(20, 2))

        if self.subtitulo:
            ttk.Label(
                self, text=self.subtitulo, style="Subtitulo.TLabel"
            ).pack(anchor="w", padx=24, pady=(0, 16))

    def construir_contenido(self):
        """
        Método para sobreescribir en cada subclase con formularios o tablas
        """
        ttk.Label(
            self,
            text="¡Bienvenido al sistema de PeluCan!",
            style="Placeholder.TLabel",
        ).pack(anchor="w", padx=24, pady=10)


#Subclases especificas para cada seccion del sistema
class PaginaInicio(PaginaBase):
    titulo = "Inicio – Panel General"
    subtitulo = "Resumen de actividad y próximos turnos programados."


class PaginaClientes(PaginaBase):
    titulo = "Listado de Clientes"
    subtitulo = "Administración y búsqueda de clientes registrados en el sistema."


class PaginaMascotas(PaginaBase):
    titulo = "Listado de Mascotas"
    subtitulo = "Administración y búsqueda general de mascotas registradas."


class PaginaTurnos(PaginaBase):
    titulo = "Listado de Turnos"
    subtitulo = "Administración y búsqueda general de citas programadas en el sistema."


class PaginaServicios(PaginaBase):
    titulo = "Servicios"
    subtitulo = "Servicios ofrecidos por la peluquería."
