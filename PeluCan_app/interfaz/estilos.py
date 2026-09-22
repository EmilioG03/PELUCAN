from tkinter import ttk

#Colores de la aplicacion
COLOR_HEADER = "#1a5c4a"
COLOR_SIDEBAR = "#e7f5ee"
COLOR_SIDEBAR_ACTIVO = "#1a5c4a"
COLOR_TEXTO = "#26312d"
COLOR_MUTED = "#6b7a74"
COLOR_BLANCO = "#ffffff"

ANCHO_SIDEBAR = 170

def configurar_estilos(root):
    """
    Aplica el tema y define los estilos ttk de toda la aplicacion
    """
    estilo = ttk.Style(root)
    estilo.theme_use("clam")

    # Estilos de la cabecera (header)
    estilo.configure("Header.TFrame", background=COLOR_HEADER)
    estilo.configure(
        "Header.TLabel",
        background=COLOR_HEADER,
        foreground=COLOR_BLANCO,
        font=("Segoe UI", 13, "bold"),
    )

    # Estilos del menu lateral y de los estados de los botones
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
    estilo.map("Sidebar.TButton", background=[("active", "#d7ede1")])

    estilo.configure(
        "SidebarActivo.TButton",
        background=COLOR_SIDEBAR_ACTIVO,
        foreground=COLOR_BLANCO,
        borderwidth=0,
        anchor="w",
        font=("Segoe UI", 10, "bold"),
        padding=(18, 10),
    )
    estilo.map("SidebarActivo.TButton", background=[("active", COLOR_SIDEBAR_ACTIVO)])

    # Estilos del area de contenido y titulos de las paginas
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

    return estilo
