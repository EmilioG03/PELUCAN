from datos.conexion import conectar


def insertar(nombre, apellido, telefono, email):
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        sql = """INSERT INTO cliente (nombre, apellido, telefono, correo)
                VALUES (%s, %s, %s, %s)"""
        # El correo es opcional: vacío se guarda como NULL (así varios clientes pueden no tenerlo)
        cursor.execute(sql, (nombre, apellido, telefono, email or None))
        conexion.commit()          # confirma los cambios en la base
        cursor.close()
    finally:
        conexion.close()


def listar():
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute("""SELECT id_cliente, nombre, apellido, telefono, COALESCE(correo, '')
                        FROM cliente ORDER BY apellido, nombre""")
        filas = cursor.fetchall()  # lista de tuplas
        cursor.close()
    finally:
        conexion.close()
    return filas


def buscar(texto):
    """Busca por nombre, apellido, teléfono o correo (coincidencia parcial, sin distinguir mayúsculas)."""
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        sql = """SELECT id_cliente, nombre, apellido, telefono, COALESCE(correo, '')
                FROM cliente
                WHERE nombre ILIKE %s OR apellido ILIKE %s OR telefono ILIKE %s OR correo ILIKE %s
                ORDER BY apellido, nombre"""
        patron = f"%{texto}%"
        cursor.execute(sql, (patron, patron, patron, patron))
        filas = cursor.fetchall()
        cursor.close()
    finally:
        conexion.close()
    return filas


def actualizar(id_cliente, nombre, apellido, telefono, email):
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        sql = """UPDATE cliente
                SET nombre = %s, apellido = %s, telefono = %s, correo = %s
                WHERE id_cliente = %s"""
        cursor.execute(sql, (nombre, apellido, telefono, email or None, id_cliente))
        conexion.commit()
        cursor.close()
    finally:
        conexion.close()


def eliminar(id_cliente):
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
        conexion.commit()
        cursor.close()
    finally:
        conexion.close()
