# pyright: reportOptionalSubscript=false, reportPossiblyUnboundVariable=false
from datos.conexion import obtener_conexion

def listar():
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                p.id_pago,
                p.id_turno,
                m.nombre AS mascota,
                t.fecha,
                t.hora,
                p.monto,
                p.fecha_pago,
                p.metodo_pago
            FROM pago p
            JOIN turno t
                ON t.id_turno = p.id_turno
            JOIN mascota m
                ON m.id_mascota = t.id_mascota
            ORDER BY p.fecha_pago DESC;
        """

        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def listar_turnos_sin_pago():
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                t.id_turno,
                m.nombre,
                t.fecha,
                t.hora
            FROM turno t
            JOIN mascota m
                ON m.id_mascota = t.id_mascota
            LEFT JOIN pago p
                ON p.id_turno = t.id_turno
            WHERE p.id_pago IS NULL
            ORDER BY t.fecha, t.hora;
        """

        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def insertar(monto, fecha_pago, metodo_pago, id_turno):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO pago (
                monto,
                fecha_pago,
                metodo_pago,
                id_turno
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id_pago;
        """

        cursor.execute(
            consulta,
            (
                monto,
                fecha_pago,
                metodo_pago,
                id_turno,
            ),
        )

        id_pago = cursor.fetchone()[0]
        conexion.commit()

        return id_pago

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def actualizar(id_pago, monto, fecha_pago, metodo_pago, id_turno):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE pago
            SET
                monto = %s,
                fecha_pago = %s,
                metodo_pago = %s,
                id_turno = %s
            WHERE id_pago = %s;
        """

        cursor.execute(
            consulta,
            (
                monto,
                fecha_pago,
                metodo_pago,
                id_turno,
                id_pago,
            ),
        )

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def eliminar(id_pago):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM pago WHERE id_pago = %s",
            (id_pago,),
        )

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()