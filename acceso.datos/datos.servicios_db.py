

import os
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

# --------------------------------------------------------------------------
# Límites (coinciden con las restricciones de servicio_catalogo.sql)
# --------------------------------------------------------------------------
NOMBRE_MAX = 80
DURACION_MAX = 2_147_483_647            # tope de INTEGER en PostgreSQL
PRECIO_MAX = Decimal("99999999.99")     # tope de NUMERIC(10,2)
CENTAVOS = Decimal("0.01")


# --------------------------------------------------------------------------
# Excepciones
# --------------------------------------------------------------------------
class ServicioError(Exception):
    """Base de todos los errores del módulo."""


class ValidacionError(ServicioError):
    """Dato inválido (se detecta antes de llegar a la base o por un CHECK)."""


class DuplicadoError(ServicioError):
    """Ya existe un servicio con ese nombre."""


class NoEncontradoError(ServicioError):
    """El servicio no existe (por ejemplo, fue eliminado por otra persona)."""


class ServicioEnUsoError(ServicioError):
    """El servicio tiene turnos asociados y no puede eliminarse."""


class ConexionError(ServicioError):
    """No se pudo conectar con la base de datos."""


class BaseDatosError(ServicioError):
    """Cualquier otro error de la base de datos."""


# --------------------------------------------------------------------------
# Modelo
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Servicio:
    id_servicio: int
    nombre_servicio: str
    duracion_estimada: int      # minutos
    precio_base: Decimal


# --------------------------------------------------------------------------
# Validaciones (espejan los CHECK de la base, con mensajes amigables)
# --------------------------------------------------------------------------
def normalizar_nombre(nombre):
    """Recorta y colapsa espacios internos: '  Corte   + Baño ' -> 'Corte + Baño'."""
    return " ".join(str(nombre or "").split())


def validar_nombre(nombre):
    nombre = normalizar_nombre(nombre)
    if not nombre:
        raise ValidacionError("El nombre del servicio es obligatorio.")
    if len(nombre) > NOMBRE_MAX:
        raise ValidacionError(f"El nombre no puede superar los {NOMBRE_MAX} caracteres.")
    return nombre


def parsear_duracion(valor):
    """Devuelve la duración como int de minutos (> 0)."""
    if isinstance(valor, bool):
        raise ValidacionError("La duración debe ser un número entero de minutos.")
    if isinstance(valor, int):
        minutos = valor
    else:
        texto = str(valor if valor is not None else "").strip()
        if not texto:
            raise ValidacionError("La duración estimada es obligatoria.")
        if not re.fullmatch(r"\d+", texto):
            raise ValidacionError("La duración debe ser un número entero de minutos (ej.: 45).")
        minutos = int(texto)
    if minutos <= 0:
        raise ValidacionError("La duración debe ser mayor que cero.")
    if minutos > DURACION_MAX:
        raise ValidacionError("La duración ingresada es demasiado grande.")
    return minutos


def parsear_precio(valor):
    """
    Devuelve el precio como Decimal con 2 decimales (>= 0).
    Acepta '5000', '5000.50', '5000,50' y '5.000,50'.
    Un valor como '5.000' se rechaza (3 decimales) para evitar confundir
    5 con 5000.
    """
    if isinstance(valor, Decimal):
        texto = format(valor, "f")
    else:
        texto = str(valor if valor is not None else "")
    texto = texto.strip().replace("$", "").replace(" ", "")
    if not texto:
        raise ValidacionError("El precio base es obligatorio.")
    if texto.startswith("-"):
        raise ValidacionError("El precio no puede ser negativo.")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(",", ".")
    if not re.fullmatch(r"\d+(\.\d+)?", texto):
        raise ValidacionError("El precio debe ser un número (ej.: 5000 o 5000,50).")
    try:
        precio = Decimal(texto)
    except InvalidOperation:
        raise ValidacionError("El precio debe ser un número (ej.: 5000 o 5000,50).")
    if precio.as_tuple().exponent < -2:
        raise ValidacionError("El precio admite como máximo 2 decimales.")
    precio = precio.quantize(CENTAVOS)
    if precio > PRECIO_MAX:
        raise ValidacionError("El precio ingresado es demasiado grande.")
    return precio


def validar_servicio(nombre, duracion, precio):
    """Valida los tres campos y devuelve (nombre, minutos, Decimal)."""
    return validar_nombre(nombre), parsear_duracion(duracion), parsear_precio(precio)


def formatear_precio(precio):
    """Decimal('5000.5') -> '$ 5.000,50' (formato argentino)."""
    texto = f"{Decimal(precio):,.2f}"
    return "$ " + texto.replace(",", "\0").replace(".", ",").replace("\0", ".")


# --------------------------------------------------------------------------
# Conexión
# --------------------------------------------------------------------------
def obtener_conexion():
    """
    Abre una conexión a PostgreSQL. Los datos salen de variables de entorno
    (así la contraseña no queda escrita en el código ni en el repositorio):
        PELUCAN_DB_HOST (localhost)   PELUCAN_DB_PORT (5432)
        PELUCAN_DB_NAME (pelucan)     PELUCAN_DB_USER (postgres)
        PELUCAN_DB_PASSWORD
    """
    try:
        import psycopg2
    except ImportError as exc:
        raise ConexionError(
            "Falta instalar el conector de PostgreSQL: pip install psycopg2-binary"
        ) from exc
    try:
        return psycopg2.connect(
            host=os.getenv("PELUCAN_DB_HOST", "localhost"),
            port=int(os.getenv("PELUCAN_DB_PORT", "5432")),
            dbname=os.getenv("PELUCAN_DB_NAME", "pelucan"),
            user=os.getenv("PELUCAN_DB_USER", "postgres"),
            password=os.getenv("PELUCAN_DB_PASSWORD", ""),
            connect_timeout=5,
        )
    except psycopg2.Error as exc:
        raise ConexionError(
            "No se pudo conectar con la base de datos. Verificá que PostgreSQL "
            "esté encendido y que los datos de conexión sean correctos."
        ) from exc


# --------------------------------------------------------------------------
# Traducción de errores de la base a excepciones propias
# --------------------------------------------------------------------------
def traducir_error(exc):
    """Convierte una excepción del driver en una ServicioError con mensaje claro."""
    if isinstance(exc, ServicioError):
        return exc

    pgcode = getattr(exc, "pgcode", None) or ""
    constraint = getattr(getattr(exc, "diag", None), "constraint_name", None) or ""
    texto = str(exc).lower()
    detalle = f"{constraint} {texto}"

    if pgcode == "23505" or "unique constraint failed" in texto:
        return DuplicadoError("Ya existe un servicio con ese nombre.")
    if pgcode == "23503" or "foreign key constraint failed" in texto:
        return ServicioEnUsoError(
            "No se puede eliminar el servicio porque tiene turnos asociados."
        )
    if pgcode == "23514" or "check constraint failed" in texto:
        if "duracion" in detalle:
            return ValidacionError("La duración debe ser mayor que cero.")
        if "precio" in detalle:
            return ValidacionError("El precio no puede ser negativo.")
        if "nombre" in detalle:
            return ValidacionError("El nombre del servicio es obligatorio.")
        return ValidacionError("Algún dato no cumple las restricciones del catálogo.")
    if pgcode == "23502" or "not null constraint failed" in texto:
        return ValidacionError("Falta completar un dato obligatorio.")
    if pgcode == "42P01" or "no such table" in texto:
        return BaseDatosError(
            "La tabla 'servicio' no existe. Ejecutá antes el script servicio_catalogo.sql."
        )
    if pgcode.startswith("08") or (
        type(exc).__name__ == "OperationalError"
        and type(exc).__module__.startswith("psycopg2")
    ):
        return ConexionError("Se perdió la conexión con la base de datos.")
    return BaseDatosError(f"Error de base de datos: {exc}")


# --------------------------------------------------------------------------
# CRUD
# --------------------------------------------------------------------------
_COLUMNAS = "id_servicio, nombre_servicio, duracion_estimada, precio_base"


def _fila_a_servicio(fila):
    return Servicio(
        id_servicio=int(fila[0]),
        nombre_servicio=fila[1],
        duracion_estimada=int(fila[2]),
        precio_base=Decimal(str(fila[3])).quantize(CENTAVOS),
    )


class ServicioDAO:
    def __init__(self, conexion_factory=obtener_conexion):
        self._factory = conexion_factory

    def _transaccion(self, operacion):
        """Ejecuta operacion(cursor) en una transacción propia."""
        conn = self._factory()
        try:
            cur = conn.cursor()
            try:
                resultado = operacion(cur)
            finally:
                cur.close()
            conn.commit()
            return resultado
        except Exception as exc:
            try:
                conn.rollback()
            except Exception:
                pass
            traducida = traducir_error(exc)
            if traducida is exc:
                raise
            raise traducida from exc
        finally:
            conn.close()

    # ---- Alta -------------------------------------------------------------
    def crear(self, nombre, duracion, precio):
        nombre, minutos, precio = validar_servicio(nombre, duracion, precio)

        def op(cur):
            cur.execute(
                "INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base) "
                "VALUES (%s, %s, %s) RETURNING " + _COLUMNAS,
                (nombre, minutos, precio),
            )
            return _fila_a_servicio(cur.fetchone())

        return self._transaccion(op)

    # ---- Consulta ---------------------------------------------------------
    def listar(self, texto=None):
        """Lista el catálogo ordenado por nombre; `texto` filtra por nombre."""
        sql = "SELECT " + _COLUMNAS + " FROM servicio"
        params = []
        if texto and texto.strip():
            sql += " WHERE lower(nombre_servicio) LIKE %s"
            params.append("%" + texto.strip().lower() + "%")
        sql += " ORDER BY lower(nombre_servicio)"

        def op(cur):
            cur.execute(sql, params)
            return [_fila_a_servicio(f) for f in cur.fetchall()]

        return self._transaccion(op)

    def obtener(self, id_servicio):
        def op(cur):
            cur.execute(
                "SELECT " + _COLUMNAS + " FROM servicio WHERE id_servicio = %s",
                (id_servicio,),
            )
            fila = cur.fetchone()
            if fila is None:
                raise NoEncontradoError("El servicio ya no existe.")
            return _fila_a_servicio(fila)

        return self._transaccion(op)

    # ---- Modificación -----------------------------------------------------
    def actualizar(self, id_servicio, nombre, duracion, precio):
        nombre, minutos, precio = validar_servicio(nombre, duracion, precio)

        def op(cur):
            cur.execute(
                "UPDATE servicio SET nombre_servicio = %s, duracion_estimada = %s, "
                "precio_base = %s WHERE id_servicio = %s RETURNING " + _COLUMNAS,
                (nombre, minutos, precio, id_servicio),
            )
            fila = cur.fetchone()
            if fila is None:
                raise NoEncontradoError("El servicio ya no existe.")
            return _fila_a_servicio(fila)

        return self._transaccion(op)

    # ---- Baja -------------------------------------------------------------
    def eliminar(self, id_servicio):
        def op(cur):
            cur.execute("DELETE FROM servicio WHERE id_servicio = %s", (id_servicio,))
            if cur.rowcount == 0:
                raise NoEncontradoError("El servicio ya no existe.")

        self._transaccion(op)