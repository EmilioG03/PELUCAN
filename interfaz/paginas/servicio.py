import re
from decimal import Decimal, InvalidOperation
from tkinter import messagebox

import psycopg2
from psycopg2 import errors

from interfaz.paginas.base import PaginaABM
from datos import servicio_dao


# Límites (coinciden con las columnas de la tabla servicio)
NOMBRE_MAX = 80
DURACION_MAX = 2_147_483_647            # tope de INTEGER en PostgreSQL
PRECIO_MAX = Decimal("99999999.99")     # tope de NUMERIC(10,2)
CENTAVOS = Decimal("0.01")


# ----------------------------------------------------------------------
# Validaciones y formato (las usa la página; no tocan la base)
# ----------------------------------------------------------------------
def normalizar_nombre(nombre):
    """Recorta y colapsa espacios internos: '  Corte   + Baño ' -> 'Corte + Baño'."""
    return " ".join(str(nombre or "").split())


def validar_nombre(nombre):
    nombre = normalizar_nombre(nombre)
    if not nombre:
        raise ValueError("El nombre del servicio es obligatorio.")
    if len(nombre) > NOMBRE_MAX:
        raise ValueError(f"El nombre no puede superar los {NOMBRE_MAX} caracteres.")
    return nombre


def parsear_duracion(valor):
    """Devuelve la duración como int de minutos (> 0)."""
    texto = str(valor if valor is not None else "").strip()
    if not texto:
        raise ValueError("La duración estimada es obligatoria.")
    if not re.fullmatch(r"\d+", texto):
        raise ValueError("La duración debe ser un número entero de minutos (ej.: 45).")
    minutos = int(texto)
    if minutos <= 0:
        raise ValueError("La duración debe ser mayor que cero.")
    if minutos > DURACION_MAX:
        raise ValueError("La duración ingresada es demasiado grande.")
    return minutos


def parsear_precio(valor):
    """
    Devuelve el precio como Decimal con 2 decimales (>= 0).
    Acepta '5000', '5000.50', '5000,50' y '5.000,50'.
    Un valor como '5.000' se rechaza (3 decimales) para no confundir 5 con 5000.
    """
    texto = str(valor if valor is not None else "")
    texto = texto.strip().replace("$", "").replace(" ", "")
    if not texto:
        raise ValueError("El precio base es obligatorio.")
    if texto.startswith("-"):
        raise ValueError("El precio no puede ser negativo.")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", ".")
    if not re.fullmatch(r"\d+(\.\d+)?", texto):
        raise ValueError("El precio debe ser un número (ej.: 5000 o 5000,50).")
    try:
        precio = Decimal(texto)
    except InvalidOperation as error:
        raise ValueError("El precio debe ser un número (ej.: 5000 o 5000,50).") from error
    exponente = precio.as_tuple().exponent
    if isinstance(exponente, int) and exponente < -2:
        raise ValueError("El precio admite como máximo 2 decimales.")
    precio = precio.quantize(CENTAVOS)
    if precio > PRECIO_MAX:
        raise ValueError("El precio ingresado es demasiado grande.")
    return precio


def validar_servicio(nombre, duracion, precio):
    """Valida los tres campos y devuelve (nombre, minutos, Decimal)."""
    return validar_nombre(nombre), parsear_duracion(duracion), parsear_precio(precio)


def formatear_precio(precio):
    """Decimal('5000.5') -> '$ 5.000,50' (formato argentino)."""
    texto = f"{Decimal(precio):,.2f}"
    return "$ " + texto.replace(",", "\0").replace(".", ",").replace("\0", ".")


# ----------------------------------------------------------------------
# Página
# ----------------------------------------------------------------------
class PaginaServicios(PaginaABM):
    titulo = "Servicios"
    subtitulo = "Catálogo de prestaciones, duración estimada y precio base."

    columnas = [
        ("nombre_servicio", "Servicio"),
        ("duracion_estimada", "Duración (min)"),
        ("precio_base", "Precio base"),
    ]

    datos_iniciales = []
    campo_busqueda = "nombre_servicio"

    def __init__(self, contenedor):
        # Los datos salen siempre de PostgreSQL. Si no hay conexión se avisa:
        # no se muestran datos de ejemplo.
        try:
            self.datos_iniciales = self._obtener_servicios_bd()
        except psycopg2.Error as error:
            self.datos_iniciales = []
            messagebox.showerror(
                "Error de conexión",
                f"No se pudieron cargar los servicios desde PostgreSQL.\n\n{error}",
            )

        super().__init__(contenedor)

    # ------------------------------------------------------------------
    # Carga de datos
    # ------------------------------------------------------------------
    def _obtener_servicios_bd(self):
        """Lee el catálogo de la base y lo pasa al formato de PaginaABM."""
        servicios = []
        for id_servicio, nombre, duracion, precio in servicio_dao.listar():
            servicios.append(
                {
                    "id_servicio": id_servicio,
                    "nombre_servicio": nombre,
                    "duracion_estimada": str(duracion),
                    "precio_base": formatear_precio(precio),
                    "precio_numero": precio,   # valor real, para precargar el formulario
                }
            )
        return servicios

    def _recargar_servicios(self):
        """Vuelve a consultar PostgreSQL y actualiza el listado."""
        self.datos = self._obtener_servicios_bd()
        self._refrescar_listado()

    # ------------------------------------------------------------------
    # Editar: el formulario muestra el precio sin formato ($ y puntos de miles)
    # ------------------------------------------------------------------
    def _al_presionar_editar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Nada seleccionado", "Seleccioná un servicio del listado para editar.")
            return

        self.fila_seleccionada = int(seleccion[0])
        servicio = self.datos[self.fila_seleccionada]
        self.variables["nombre_servicio"].set(servicio["nombre_servicio"])
        self.variables["duracion_estimada"].set(servicio["duracion_estimada"])
        self.variables["precio_base"].set(f"{servicio['precio_numero']:.2f}".replace(".", ","))
        self._mostrar_vista_formulario()

    # ------------------------------------------------------------------
    # Guardar (INSERT / UPDATE)
    # ------------------------------------------------------------------
    def _al_presionar_guardar(self):
        valores = {clave: variable.get().strip() for clave, variable in self.variables.items()}

        try:
            nombre, minutos, precio = validar_servicio(
                valores["nombre_servicio"],
                valores["duracion_estimada"],
                valores["precio_base"],
            )
        except ValueError as error:
            messagebox.showwarning("Dato inválido", str(error))
            return

        fila = self.fila_seleccionada   # None = alta nueva; un número = editando esa fila
        try:
            if fila is None:
                servicio_dao.insertar(nombre, minutos, precio)
                aviso = "Servicio agregado correctamente."
            else:
                servicio_dao.actualizar(self.datos[fila]["id_servicio"], nombre, minutos, precio)
                aviso = "Servicio actualizado correctamente."
        except errors.UniqueViolation:
            messagebox.showerror("Servicio duplicado", f"Ya existe un servicio llamado «{nombre}».")
            return
        except psycopg2.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudo guardar el servicio.\n\n{error}",
            )
            return

        messagebox.showinfo("Listo", aviso)
        self._recargar_servicios()
        self._mostrar_vista_listado()

    # ------------------------------------------------------------------
    # Eliminar (DELETE)
    # ------------------------------------------------------------------
    def _al_presionar_eliminar(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Nada seleccionado", "Seleccioná un servicio del listado para eliminar.")
            return

        servicio = self.datos[int(seleccion[0])]
        nombre = servicio["nombre_servicio"]

        if not messagebox.askyesno(
            "Eliminar servicio",
            f"¿Seguro que querés eliminar el servicio «{nombre}»?\n\nEsta acción no se puede deshacer.",
        ):
            return

        try:
            servicio_dao.eliminar(servicio["id_servicio"])
        except (errors.ForeignKeyViolation, errors.RestrictViolation):
            messagebox.showwarning(
                "No se puede eliminar",
                f"«{nombre}» tiene turnos asociados.\n"
                "No puede eliminarse mientras tenga turnos registrados.",
            )
            return
        except psycopg2.Error as error:
            messagebox.showerror(
                "Error de base de datos",
                f"No se pudo eliminar el servicio.\n\n{error}",
            )
            return

        messagebox.showinfo("Servicio eliminado", "El servicio fue eliminado correctamente.")
        self._recargar_servicios()

    # ------------------------------------------------------------------
    # Doble clic: ficha del servicio (los servicios no tienen observaciones)
    # ------------------------------------------------------------------
    def _mostrar_detalle(self, evento):
        item_id = self.tabla.identify_row(evento.y)
        if not item_id:
            return
        servicio = self.datos[int(item_id)]
        messagebox.showinfo(
            f"Servicio - {servicio['nombre_servicio']}",
            f"Duración estimada: {servicio['duracion_estimada']} minutos\n"
            f"Precio base: {servicio['precio_base']}",
        )
