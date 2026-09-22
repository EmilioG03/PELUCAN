from tkinter import ttk

class Sidebar(ttk.Frame):
    """
    Menú lateral con botones de acceso a cada seccion
    """

    def __init__(self, contenedor, secciones, on_seleccionar, ancho):
        super().__init__(contenedor, style="Sidebar.TFrame", width=ancho)
        self.pack_propagate(False)

        self._on_seleccionar = on_seleccionar
        self._botones = {}

        for nombre_seccion in secciones:
            boton = ttk.Button(
                self,
                text=nombre_seccion,
                style="Sidebar.TButton",
                command=lambda s=nombre_seccion: self._al_hacer_click(s),
            )
            boton.pack(fill="x")
            self._botones[nombre_seccion] = boton

    def _al_hacer_click(self, nombre_seccion):
        """Actualiza el aspecto del menu y ejecuta la funcion de cambio de vista"""
        self.marcar_activo(nombre_seccion)
        self._on_seleccionar(nombre_seccion)

    def marcar_activo(self, nombre_seccion):
        """Cambia el estilo del boton seleccionado y reestablece los demas"""
        for nombre, boton in self._botones.items():
            estilo = "SidebarActivo.TButton" if nombre == nombre_seccion else "Sidebar.TButton"
            boton.configure(style=estilo)
