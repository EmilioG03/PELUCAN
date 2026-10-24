# pyright: reportOptionalSubscript=false, reportPossiblyUnboundVariable=false
from psycopg2 import errors

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

# Estados que ocupan la agenda (Completado y Cancelado no bloquean horarios)
ESTADOS_ACTIVOS = ("Pendiente", "Confirmado")

# Columna de `turno` que se controla en cada tipo de agenda
_COLUMNA_AGENDA = {
    "peluquero": "id_peluquero",
    "mascota": "id_mascota",
}


def _agenda_libre(tipo, id_valor, fecha, hora, id_servicio, excluir_id=None):
    """True si no hay ningún turno activo que se superponga con el intervalo
    [hora, hora + duración del servicio) para ese peluquero o esa mascota.

    Dos turnos se superponen cuando cada uno empieza antes de que termine el
    otro; si uno empieza justo cuando termina el anterior, NO se superponen.
    Se compara con fecha + hora (timestamp), así también se detectan turnos
    que cruzan la medianoche.

    excluir_id: id de un turno que se ignora (sirve al EDITAR un turno, para
    que no se compare contra sí mismo).
    """
    columna = _COLUMNA_AGENDA[tipo]  # valor fijo del diccionario, nunca texto del usuario
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        consulta = f"""
            SELECT EXISTS (
                SELECT 1
                FROM turno t
                JOIN servicio servicio_existente
                    ON servicio_existente.id_servicio = t.id_servicio
                JOIN servicio servicio_nuevo
                    ON servicio_nuevo.id_servicio = %s
                WHERE t.{columna} = %s
                  AND t.estado IN ('Pendiente', 'Confirmado')
                  AND (%s::date + %s::time)
                      < t.fecha + t.hora
                        + servicio_existente.duracion_estimada
                        * INTERVAL '1 minute'
                  AND t.fecha + t.hora
                      < %s::date + %s::time
                        + servicio_nuevo.duracion_estimada
                        * INTERVAL '1 minute'
                  AND (%s::int IS NULL OR t.id_turno <> %s)
            );
        """

        cursor.execute(
            consulta,
            (id_servicio, id_valor, fecha, hora, fecha, hora, excluir_id, excluir_id),
        )

        hay_superposicion = cursor.fetchone()[0]

        return not hay_superposicion

    finally:
        cursor.close()
        conexion.close()


def peluquero_disponible(fecha, hora, id_peluquero, id_servicio, excluir_id=None):
    """True si el peluquero está libre durante toda la duración del servicio."""
    return _agenda_libre("peluquero", id_peluquero, fecha, hora, id_servicio, excluir_id)


def mascota_disponible(fecha, hora, id_mascota, id_servicio, excluir_id=None):
    """True si la mascota no tiene otro turno activo que se superponga."""
    return _agenda_libre("mascota", id_mascota, fecha, hora, id_servicio, excluir_id)


def crear_turno(
    fecha,
    hora,
    estado,
    observaciones,
    id_mascota,
    id_peluquero,
    id_servicio
):
    """Registra un turno y devuelve su id.

    Lanza ValueError con un mensaje legible si el horario se superpone con
    otro turno del peluquero o de la mascota. La verificación previa da una
    respuesta rápida; la garantía real está en el trigger de la base
    (scripts/04_prevencion_solapamientos.sql), que también cubre cargas
    simultáneas y cualquier otro programa que escriba en la tabla.
    """

    if estado in ESTADOS_ACTIVOS:
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

        if not mascota_disponible(
            fecha,
            hora,
            id_mascota,
            id_servicio
        ):
            raise ValueError(
                "La mascota seleccionada ya tiene un turno "
                "que se superpone con ese horario."
            )

    conexion = obtener_conexion()
    cursor = None

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

    except errors.ExclusionViolation as error:
        # Lo detectó el trigger de la base (otra persona cargó un turno al mismo tiempo)
        conexion.rollback()
        raise ValueError(
            error.diag.message_primary
            or "El horario se superpone con otro turno."
        ) from error

    except errors.UniqueViolation as error:
        # Mismo inicio exacto para el mismo peluquero o la misma mascota
        conexion.rollback()
        if "mascota" in (error.diag.constraint_name or ""):
            raise ValueError(
                "La mascota ya tiene un turno a esa fecha y hora."
            ) from error
        raise ValueError(
            "El peluquero ya tiene un turno a esa fecha y hora."
        ) from error

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def actualizar_turno(
    id_turno,
    fecha,
    hora,
    estado,
    observaciones,
    id_mascota,
    id_peluquero,
    id_servicio
):
    """Modifica un turno y devuelve la cantidad de filas actualizadas
    (0 si el turno ya no existe).

    Aplica las mismas reglas que crear_turno: si el turno queda activo
    (Pendiente/Confirmado) no puede pisar a otro del peluquero ni de la
    mascota. El propio turno que se edita se ignora en esa comparación.
    """

    if estado in ESTADOS_ACTIVOS:
        if not peluquero_disponible(
            fecha, hora, id_peluquero, id_servicio, excluir_id=id_turno
        ):
            raise ValueError(
                "El peluquero seleccionado ya tiene un turno "
                "que se superpone con ese horario."
            )

        if not mascota_disponible(
            fecha, hora, id_mascota, id_servicio, excluir_id=id_turno
        ):
            raise ValueError(
                "La mascota seleccionada ya tiene un turno "
                "que se superpone con ese horario."
            )

    conexion = obtener_conexion()
    cursor = None

    try:
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE turno
            SET fecha = %s,
                hora = %s,
                estado = %s,
                observaciones = %s,
                id_mascota = %s,
                id_peluquero = %s,
                id_servicio = %s
            WHERE id_turno = %s;
            """,
            (
                fecha,
                hora,
                estado,
                observaciones,
                id_mascota,
                id_peluquero,
                id_servicio,
                id_turno,
            ),
        )

        afectadas = cursor.rowcount
        conexion.commit()
        return afectadas

    except errors.ExclusionViolation as error:
        conexion.rollback()
        raise ValueError(
            error.diag.message_primary
            or "El horario se superpone con otro turno."
        ) from error

    except errors.UniqueViolation as error:
        conexion.rollback()
        if "mascota" in (error.diag.constraint_name or ""):
            raise ValueError(
                "La mascota ya tiene un turno a esa fecha y hora."
            ) from error
        raise ValueError(
            "El peluquero ya tiene un turno a esa fecha y hora."
        ) from error

    except Exception:
        conexion.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def eliminar_turno(id_turno):
    conexion = obtener_conexion()

    try:
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM turno WHERE id_turno = %s",
            (id_turno,),
        )

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()
        