from datos.conexion import obtener_conexion


def listar_turnos():
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT
                t.id_turno,
                m.nombre AS mascota,
                p.nombre || ' ' || p.apellido AS peluquero,
                s.nombre_servicio,
                t.fecha,
                t.hora,
                t.estado,
                t.observaciones
            FROM turno t
            JOIN mascota m
                ON t.id_mascota = m.id_mascota
            JOIN peluquero p
                ON t.id_peluquero = p.id_peluquero
            JOIN servicio s
                ON t.id_servicio = s.id_servicio
            ORDER BY t.fecha, t.hora;
        """

        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def listar_mascotas():
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT id_mascota, nombre
            FROM mascota
            ORDER BY nombre;
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def listar_peluqueros():
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_peluquero,
                nombre || ' ' || apellido
            FROM peluquero
            ORDER BY nombre, apellido;
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def listar_servicios():
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                id_servicio,
                nombre_servicio,
                duracion_estimada,
                precio_base
            FROM servicio
            ORDER BY nombre_servicio;
        """)

        return cursor.fetchall()


    finally:
        cursor.close()
        conexion.close()

def peluquero_disponible(fecha, hora, id_peluquero, id_servicio):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            SELECT EXISTS (
                SELECT 1
                FROM turno t
                JOIN servicio servicio_existente
                    ON servicio_existente.id_servicio = t.id_servicio
                JOIN servicio servicio_nuevo
                    ON servicio_nuevo.id_servicio = %s
                WHERE t.id_peluquero = %s
                  AND t.fecha = %s
                  AND t.estado IN ('Pendiente', 'Confirmado')
                  AND %s::time <
                      t.hora
                      + servicio_existente.duracion_estimada
                      * INTERVAL '1 minute'
                  AND t.hora <
                      %s::time
                      + servicio_nuevo.duracion_estimada
                      * INTERVAL '1 minute'
            );
        """

        cursor.execute(
            consulta,
            (
                id_servicio,
                id_peluquero,
                fecha,
                hora,
                hora,
            ),
        )

        hay_superposicion = cursor.fetchone()[0]

        return not hay_superposicion

    finally:
        cursor.close()
        conexion.close()        


def crear_turno(
    fecha,
    hora,
    estado,
    observaciones,
    id_mascota,
    id_peluquero,
    id_servicio
):

    if estado in ("Pendiente", "Confirmado"):
        if not peluquero_disponible(
            fecha,
            hora,
            id_peluquero,
            id_servicio
        ):
            raise ValueError(
                "El peluquero seleccionado ya tiene un turno "
                "que se superpone con ese horario."
            )

    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = """
            INSERT INTO turno (
                fecha,
                hora,
                estado,
                observaciones,
                id_mascota,
                id_peluquero,
                id_servicio
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_turno;
        """

        cursor.execute(
            consulta,
            (
                fecha,
                hora,
                estado,
                observaciones,
                id_mascota,
                id_peluquero,
                id_servicio,
            ),
        )

        id_turno = cursor.fetchone()[0]

        conexion.commit()

        return id_turno

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()