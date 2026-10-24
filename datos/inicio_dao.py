# pyright: reportOptionalSubscript=false
from datos.conexion import obtener_conexion


def obtener_metricas(fecha):
    """Devuelve los números del panel de Inicio para una fecha.

    Resultado: dict con turnos del día (sin cancelados), total de clientes,
    total de mascotas e ingresos cobrados ese día.
    """
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()

        cursor.execute(
            """SELECT COUNT(*) FROM turno
            WHERE fecha = %s AND estado <> 'Cancelado'""",
            (fecha,),
        )
        turnos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM cliente")
        clientes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM mascota")
        mascotas = cursor.fetchone()[0]

        cursor.execute(
            """SELECT COALESCE(SUM(monto), 0) FROM pago
            WHERE fecha_pago::date = %s""",
            (fecha,),
        )
        ingresos = cursor.fetchone()[0]

        cursor.close()
    finally:
        conexion.close()

    return {
        "turnos": turnos,
        "clientes": clientes,
        "mascotas": mascotas,
        "ingresos": ingresos,
    }


def listar_turnos_del_dia(fecha):
    """Turnos de una fecha (sin cancelados), ordenados por hora.

    Cada fila: (mascota, servicio, fecha, hora, estado).
    """
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """SELECT m.nombre, s.nombre_servicio, t.fecha, t.hora, t.estado
            FROM turno t
            JOIN mascota m ON t.id_mascota = m.id_mascota
            JOIN servicio s ON t.id_servicio = s.id_servicio
            WHERE t.fecha = %s AND t.estado <> 'Cancelado'
            ORDER BY t.hora""",
            (fecha,),
        )
        filas = cursor.fetchall()
        cursor.close()
    finally:
        conexion.close()
    return filas
