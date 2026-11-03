from datos.conexion import obtener_conexion


def insertar(nombre, apellido, telefono, especialidad):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        sql = """INSERT INTO peluquero (nombre, apellido, telefono, especialidad)
                VALUES (%s, %s, %s, %s)"""
        # La especialidad es opcional: vacía se guarda como NULL
        cursor.execute(sql, (nombre, apellido, telefono, especialidad or None))
        conexion.commit()          # confirma los cambios en la base
        cursor.close()
    finally:
        conexion.close()


def listar():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("""SELECT id_peluquero, nombre, apellido, telefono, COALESCE(especialidad, '')
                        FROM peluquero ORDER BY apellido, nombre""")
        filas = cursor.fetchall()  # lista de tuplas
        cursor.close()
    finally:
        conexion.close()
    return filas


def buscar(texto):
    """Busca por nombre, apellido, teléfono o especialidad (coincidencia parcial, sin distinguir mayúsculas)."""
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        sql = """SELECT id_peluquero, nombre, apellido, telefono, COALESCE(especialidad, '')
                FROM peluquero
                WHERE nombre ILIKE %s OR apellido ILIKE %s OR telefono ILIKE %s OR especialidad ILIKE %s
                ORDER BY apellido, nombre"""
        patron = f"%{texto}%"
        cursor.execute(sql, (patron, patron, patron, patron))
        filas = cursor.fetchall()
        cursor.close()
    finally:
        conexion.close()
    return filas


def actualizar(id_peluquero, nombre, apellido, telefono, especialidad):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        sql = """UPDATE peluquero
                SET nombre = %s, apellido = %s, telefono = %s, especialidad = %s
                WHERE id_peluquero = %s"""
        cursor.execute(sql, (nombre, apellido, telefono, especialidad or None, id_peluquero))
        conexion.commit()
        cursor.close()
    finally:
        conexion.close()


def eliminar(id_peluquero):
    """Borra un peluquero. Si tiene turnos asociados, la base lo rechaza (ON DELETE RESTRICT)."""
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM peluquero WHERE id_peluquero = %s", (id_peluquero,))
        conexion.commit()
        cursor.close()
    finally:
        conexion.close()
