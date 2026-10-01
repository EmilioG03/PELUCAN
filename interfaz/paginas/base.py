from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

class PaginaBase(ttk.Frame):
    """
    Página con encabezado estándar (título + subtítulo).
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
        """Pensado para ser sobreescrito por cada página concreta."""
        pass

class PaginaABM(PaginaBase):
    """Página con alternancia entre vista listado y vista formulario."""

    columnas = []
    datos_iniciales = []
    campo_busqueda = None
    opciones_desplegables = {}
    campos_fecha = []

    def __init__(self, contenedor):
        self.datos = self.datos_iniciales
        self.fila_seleccionada = None
        super().__init__(contenedor)

    def construir_contenido(self):
        # 1. Contenedor de la Vista Listado
        self.marco_listado = ttk.Frame(self, style="Contenido.TFrame")
        self.marco_listado.pack(fill="both", expand=True)

        self._crear_cabecera_listado()
        self._crear_tabla_listado()

        # Contenedor de la Vista Formulario (oculto por defecto)
        self.marco_formulario = ttk.Frame(self, style="Contenido.TFrame")
        self._crear_vista_formulario()

        self._refrescar_listado()

    #VISTA: listado
    def _crear_cabecera_listado(self):
        # Fila superior de búsqueda
        marco_busqueda = ttk.Frame(self.marco_listado, style="Contenido.TFrame")
        marco_busqueda.pack(fill="x", padx=24, pady=(0, 10))

        ttk.Label(marco_busqueda, text="Buscar:", style="Subtitulo.TLabel").pack(side="left")

        self.texto_busqueda = tk.StringVar()
        self.texto_busqueda.trace_add("write", lambda *_: self._refrescar_listado())
        ttk.Entry(marco_busqueda, textvariable=self.texto_busqueda, width=32).pack(
            side="left", padx=8
        )

        ttk.Label(marco_busqueda, text="en:", style="Subtitulo.TLabel").pack(side="left", padx=(8, 4))
        self.criterio_filtro = tk.StringVar(value="Todos")
        opciones_criterio = ["Todos"] + [etiqueta for _, etiqueta in self.columnas]

        combo_criterio = ttk.Combobox(
            marco_busqueda,
            textvariable=self.criterio_filtro,
            values=opciones_criterio,
            state="readonly",
            width=16,
        )
        combo_criterio.pack(side="left")
        combo_criterio.bind("<<ComboboxSelected>>", lambda *_: self._refrescar_listado())

        # Barra de botones: Nuevo, Editar, Eliminar
        marco_acciones = ttk.Frame(self.marco_listado, style="Contenido.TFrame")
        marco_acciones.pack(fill="x", padx=24, pady=(5, 12))

        ttk.Button(marco_acciones, text="Eliminar", style="Secundario.TButton", command=self._al_presionar_eliminar).pack(
            side="right", padx=(6, 0)
        )
        ttk.Button(marco_acciones, text="Editar", style="Secundario.TButton", command=self._al_presionar_editar).pack(
            side="right", padx=(6, 0)
        )
        ttk.Button(marco_acciones, text="Nuevo", command=self._al_presionar_nuevo).pack(
            side="right"
        )

    def _crear_tabla_listado(self):
        marco_tabla = ttk.Frame(self.marco_listado, style="Contenido.TFrame")
        marco_tabla.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        claves = [clave for clave, _ in self.columnas]
        self.tabla = ttk.Treeview(
            marco_tabla, columns=claves, show="headings", height=10, selectmode="browse"
        )
        for clave, etiqueta in self.columnas:
            self.tabla.heading(clave, text=etiqueta)
            self.tabla.column(clave, width=130, anchor="w")

        scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)

        scroll.pack(side="right", fill="y")

        self.tabla.pack(side="left", fill="both", expand=True)

        self.tabla.bind("<Double-1>", self._mostrar_detalle)

    # VISTA 2: Formulario
    def _crear_vista_formulario(self):
        self.variables = {}
        marco_campos = ttk.Frame(self.marco_formulario, style="Contenido.TFrame")
        marco_campos.pack(fill="x", padx=24, pady=(10, 20))

        for indice, (clave, etiqueta) in enumerate(self.columnas):
            fila, col = indice // 2, (indice % 2) * 2
            ttk.Label(marco_campos, text=etiqueta + ":", style="Subtitulo.TLabel").grid(
                row=fila, column=col, sticky="w", padx=(0, 6), pady=6
            )
            variable = tk.StringVar()

            if clave in self.campos_fecha and DateEntry is not None:
                campo = DateEntry(marco_campos, textvariable=variable, date_pattern="dd/mm/yyyy", width=25)
            elif clave in self.opciones_desplegables:
                campo = ttk.Combobox(marco_campos, textvariable=variable, values=self.opciones_desplegables[clave], state="normal", width=26)
            else:
                campo = ttk.Entry(marco_campos, textvariable=variable, width=28)

            campo.grid(row=fila, column=col + 1, sticky="w", padx=(0, 24), pady=6)
            self.variables[clave] = variable

        fila_botones = (len(self.columnas) // 2) + 1
        marco_botones = ttk.Frame(marco_campos, style="Contenido.TFrame")
        marco_botones.grid(row=fila_botones, column=0, columnspan=4, sticky="w", pady=(20, 0))

        ttk.Button(marco_botones, text="Cancelar", style="Secundario.TButton", command=self._mostrar_vista_listado).pack(
            side="left"
        )
        ttk.Button(marco_botones, text="Guardar", command=self._al_presionar_guardar).pack(
            side="left", padx=8
        )

    # NAVEGACIÓN ENTRE VISTAS
    def _mostrar_vista_listado(self):
        self.marco_formulario.pack_forget()
        self.marco_listado.pack(fill="both", expand=True)
        self._limpiar_formulario()
        self._refrescar_listado()

    def _mostrar_vista_formulario(self):
        self.marco_listado.pack_forget()
        self.marco_formulario.pack(fill="both", expand=True)

    # ACCIONES Y EVENTOS
    def _al_presionar_nuevo(self):
        self._limpiar_formulario()
        self.fila_seleccionada = None
        self._mostrar_vista_formulario()

    def _al_presionar_editar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Nada seleccionado", "Seleccioná un registro del listado para editar.")
            return

        self.fila_seleccionada = int(seleccion[0])
        registro = self.datos[self.fila_seleccionada]
        for clave, variable in self.variables.items():
            variable.set(registro.get(clave, ""))

        self._mostrar_vista_formulario()

    def _al_presionar_guardar(self):
        valores = {clave: var.get().strip() for clave, var in self.variables.items()}

        if not self._validar_datos(valores):
            return

        if self.fila_seleccionada is None:
            self.datos.append(valores)
            messagebox.showinfo("Listo", "Registro agregado correctamente.")
        else:
            self.datos[self.fila_seleccionada] = valores
            messagebox.showinfo("Listo", "Registro actualizado correctamente.")

        self._mostrar_vista_listado()

    def _al_presionar_eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Nada seleccionado", "Elegí un registro del listado para eliminar.")
            return

        indice = int(seleccion[0])
        confirmar = messagebox.askyesno(
            "Eliminar",
            "¿Seguro que querés eliminar este registro? Esta acción no se puede deshacer.",
        )
        if confirmar:
            del self.datos[indice]
            self._refrescar_listado()

    def _validar_datos(self, valores):
        campos_vacios = [
            etiqueta for clave, etiqueta in self.columnas
            if clave != "observaciones" and not valores.get(clave, "").strip()
        ]
        if campos_vacios:
            messagebox.showwarning(
                "Campo incompleto",
                "Completá los siguientes campos obligatorios:\n- " + "\n- ".join(campos_vacios),
            )
            return False

        if "telefono" in valores:
            tel_nuevo = valores["telefono"].strip()
            for i, reg in enumerate(self.datos):
                if self.fila_seleccionada is not None and i == self.fila_seleccionada:
                    continue
                if reg.get("telefono", "").strip() == tel_nuevo:
                    messagebox.showerror(
                        "Teléfono duplicado",
                        f"Ya existe un registro con el teléfono {tel_nuevo}."
                    )
                    return False

        for clave in self.campos_fecha:
            try:
                datetime.strptime(valores[clave], "%d/%m/%Y")
            except ValueError:
                messagebox.showwarning("Fecha Invalida", "Ingresa la fecha con el formato dd/mm/aaaa, por ejemplo 15/10/2026.")
            return False

        return True

    def _refrescar_listado(self):
        self.tabla.delete(*self.tabla.get_children())
        filtro = self.texto_busqueda.get().strip().lower()
        criterio = getattr(self, "criterio_filtro", None)
        criterio_sel = criterio.get() if criterio else "Todos"
        dicc = {etiqueta: clave for clave, etiqueta in self.columnas}

        for i, registro in enumerate(self.datos):
            if filtro:
                if criterio_sel == "Todos":
                    coincide = any(filtro in str(registro.get(c, "")).lower() for c, _ in self.columnas)
                else:
                    col_clave = dicc.get(criterio_sel)
                    coincide = filtro in str(registro.get(col_clave, "")).lower()
                if not coincide:
                    continue

            valores = [registro.get(c, "") for c, _ in self.columnas]
            self.tabla.insert("", "end", iid=str(i), values=valores)

    def _limpiar_formulario(self):
        self.fila_seleccionada = None
        for variable in self.variables.values():
            variable.set("")
        self.tabla.selection_remove(self.tabla.selection())

    def _mostrar_detalle(self, evento):
        item_id = self.tabla.identify_row(evento.y)
        if not item_id:
            return
        reg = self.datos[int(item_id)]
        obs = reg.get("observaciones", "").strip()
        nombre = reg.get("nombre") or reg.get("mascota", "Detalle")
        if obs:
            messagebox.showinfo(f"Observaciones - {nombre}", obs)
        else:
            messagebox.showinfo(f"Detalle - {nombre}", "No hay observaciones registradas.")
