from tkinter import ttk


class HeaderPeluCan(ttk.Frame):
    """Componente para la barra superior de la aplicacion"""
    def __init__(self, contenedor, texto="PeluCan – Sistema de Gestión"):
        super().__init__(contenedor, style="Header.TFrame")

        self.lbl_titulo = ttk.Label(self, text=texto, style="Header.TLabel")
        self.lbl_titulo.pack(side="left", padx=18, pady=12)