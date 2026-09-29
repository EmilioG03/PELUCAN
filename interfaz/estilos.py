from tkinter import ttk

#Colores de la aplicacion
COLOR_HEADER = "#1a5c4a"
COLOR_SIDEBAR = "#e7f5ee"
COLOR_SIDEBAR_ACTIVO = "#1a5c4a"
COLOR_TEXTO = "#26312d"
COLOR_MUTED = "#6b7a74"
COLOR_BLANCO = "#ffffff"
COLOR_BORDE_CARD = "#c5e8d5"
ANCHO_SIDEBAR = 170

def _estilo_cabecera(estilo):
    estilo.configure("Header.TFrame", background=COLOR_HEADER)
    estilo.configure(
        "Header.TLabel",
        background=COLOR_HEADER,
        foreground=COLOR_BLANCO,
        font=("Segoe UI", 13, "bold"),
    )

def _estilo_menu_lateral(estilo):
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


def _estilo_contenido_general(estilo):
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
    estilo.configure(
        "Seccion.TLabel",
        background=COLOR_BLANCO,
        foreground=COLOR_TEXTO,
        font=("Segoe UI", 11, "bold"),
    )


def _estilo_tarjetas(estilo):
    estilo.configure(
        "Card.TFrame",
        background=COLOR_SIDEBAR,
        relief="solid",
        borderwidth=1,
    )
    estilo.configure(
        "CardTitulo.TLabel",
        background=COLOR_SIDEBAR,
        foreground=COLOR_MUTED,
        font=("Segoe UI", 8, "bold"),
    )
    estilo.configure(
        "CardNumero.TLabel",
        background=COLOR_SIDEBAR,
        foreground=COLOR_HEADER,
        font=("Segoe UI", 22, "bold"),
    )


def _estilo_tabla(estilo):
    estilo.configure(
        "Treeview",
        background=COLOR_BLANCO,
        foreground=COLOR_TEXTO,
        fieldbackground=COLOR_BLANCO,
        rowheight=28,
        borderwidth=1,
        relief="solid",
        font=("Segoe UI", 9),
    )
    estilo.configure(
        "Treeview.Heading",
        background="#f1f5f3",
        foreground=COLOR_TEXTO,
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        borderwidth=1,
    )
    estilo.map("Treeview.Heading", background=[("active", "#e0ede6")])


def _estilo_botones_y_scroll(estilo):
    # Botón primario
    estilo.configure(
        "TButton",
        background=COLOR_HEADER,
        foreground=COLOR_BLANCO,
        borderwidth=0,
        focuscolor="none",
        font=("Segoe UI", 9, "bold"),
        padding=(12, 6),
    )
    estilo.map(
        "TButton",
        background=[("active", "#237a63"), ("disabled", "#a8c2b8")],
        foreground=[("disabled", "#f0f0f0")],
    )

    # Botón secundario
    estilo.configure(
        "Secundario.TButton",
        background="#e2e8e5",
        foreground=COLOR_TEXTO,
        borderwidth=0,
        focuscolor="none",
        font=("Segoe UI", 9),
        padding=(12, 6),
    )
    estilo.map("Secundario.TButton", background=[("active", "#d0dcd6")])

    # Barra de desplazamiento
    estilo.configure(
        "Vertical.TScrollbar",
        background=COLOR_SIDEBAR,
        troughcolor="#f4fbf7",
        bordercolor="#c5e8d5",
        arrowcolor=COLOR_HEADER,
        relief="flat",
        borderwidth=0,
        gripcount=0,
    )
    estilo.map(
        "Vertical.TScrollbar",
        background=[("active", "#c5e8d5")],
        arrowcolor=[("active", "#124033")],
    )


def configurar_estilos(root):
    """
    Función orquestadora que aplica el tema y delega
    la configuración visual en funciones modulares.
    """
    estilo = ttk.Style(root)
    estilo.theme_use("clam")

    _estilo_cabecera(estilo)
    _estilo_menu_lateral(estilo)
    _estilo_contenido_general(estilo)
    _estilo_tarjetas(estilo)
    _estilo_tabla(estilo)
    _estilo_botones_y_scroll(estilo)

    return estilo
