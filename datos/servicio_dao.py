from datos.conexion import obtener_conexion


def insertar(nombre_servicio, duracion_estimada, precio_base):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        sql = """INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base)
                VALUES (%s, %s, %s)"""
        cursor.execute(sql, (nombre_servicio, duracion_estimada, precio_base))
        conexion.commit()          # confirma los cambios en la base
        cursor.close()
    finally:
        conexion.close()


def listar():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("""SELECT id_servicio, nombre_servicio, duracion_estimada, precio_base
                        FROM servicio ORDER BY nombre_servicio""")
        filas = cursor.fetchall()  # lista de tuplas
        cursor.close()
    finally:
        conexion.close()
    return filas


def buscar(texto):
    """Busca por nombre del servicio (coincidencia parcial, sin distinguir mayúsculas)."""
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        sql = """SELECT id_servicio, nombre_servicio, duracion_estimada, precio_base
                FROM servicio
                WHERE nombre_servicio ILIKE %s
                ORDER BY nombre_servicio"""
        cursor.execute(sql, (f"%{texto}%",))
        filas = cursor.fetchall()
        cursor.close()
    finally:
        conexion.close()
    return filas


def actualizar(id_servicio, nombre_servicio, duracion_estimada, precio_base):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        sql = """UPDATE servicio
                SET nombre_servicio = %s, duracion_estimada = %s, precio_base = %s
                WHERE id_servicio = %s"""
        cursor.execute(sql, (nombre_servicio, duracion_estimada, precio_base, id_servicio))
        conexion.commit()
        cursor.close()
    finally:
        conexion.close()


def eliminar(id_servicio):
    """Borra un servicio. Si tiene turnos asociados, la base lo rechaza (ON DELETE RESTRICT)."""
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM servicio WHERE id_servicio = %s", (id_servicio,))
        conexion.commit()
        cursor.close()
    finally:
        conexion.close()
