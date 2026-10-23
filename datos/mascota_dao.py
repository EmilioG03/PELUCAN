from datos.conexion import obtener_conexion


def listar():
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                m.id_mascota,
                m.nombre,
                COALESCE(m.raza, ''),
                m.edad,
                m.tamano,
                c.nombre || ' ' || c.apellido AS dueno,
                COALESCE(m.observaciones, ''),
                m.id_cliente
            FROM mascota m
            JOIN cliente c
                ON c.id_cliente = m.id_cliente
            ORDER BY m.nombre;
        """

        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def listar_clientes():
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_cliente,
                nombre || ' ' || apellido
            FROM cliente
            ORDER BY apellido, nombre;
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def insertar(
    nombre,
    raza,
    edad,
    tamano,
    observaciones,
    id_cliente
):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO mascota (
                nombre,
                raza,
                edad,
                tamano,
                observaciones,
                id_cliente
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_mascota;
        """

        cursor.execute(
            consulta,
            (
                nombre,
                raza or None,
                edad,
                tamano,
                observaciones or None,
                id_cliente,
            ),
        )

        id_mascota = cursor.fetchone()[0]
        conexion.commit()

        return id_mascota

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def actualizar(
    id_mascota,
    nombre,
    raza,
    edad,
    tamano,
    observaciones,
    id_cliente
):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            UPDATE mascota
            SET
                nombre = %s,
                raza = %s,
                edad = %s,
                tamano = %s,
                observaciones = %s,
                id_cliente = %s
            WHERE id_mascota = %s;
        """

        cursor.execute(
            consulta,
            (
                nombre,
                raza or None,
                edad,
                tamano,
                observaciones or None,
                id_cliente,
                id_mascota,
            ),
        )

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def eliminar(id_mascota):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM mascota WHERE id_mascota = %s",
            (id_mascota,),
        )

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()