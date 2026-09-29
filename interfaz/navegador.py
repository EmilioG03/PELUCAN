from tkinter import ttk


class NavegadorPaginas(ttk.Frame):
    """
    Contenedor que apila páginas (Frames) y muestra una por vez.
    """

    def __init__(self, contenedor):
        super().__init__(contenedor, style="Contenido.TFrame")

        self.area = ttk.Frame(self, style="Contenido.TFrame")
        self.area.pack(fill="both", expand=True)
        self.area.grid_rowconfigure(0, weight=1)
        self.area.grid_columnconfigure(0, weight=1)

        self._paginas = {}

    def registrar_pagina(self, nombre, instancia_pagina):
        instancia_pagina.grid(row=0, column=0, sticky="nsew")
        self._paginas[nombre] = instancia_pagina

    def mostrar(self, nombre):
        """Trae al frente la página registrada con ese nombre."""
        if nombre in self._paginas:
            self._paginas[nombre].tkraise()
