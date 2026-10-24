# pyright: reportOptionalSubscript=false
import unittest
from datetime import date, time

import psycopg2
from psycopg2 import errors

from datos import turnos_dao
from datos.conexion import obtener_conexion

FECHA = date(2031, 1, 10)  # lejos de cualquier dato real


def _hay_base():
    try:
        obtener_conexion().close()
        return True
    except psycopg2.Error:
        return False


def _ejecutar(sql, params=None, devolver=False):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        cursor.execute(sql, params)
        resultado = cursor.fetchone()[0] if devolver else None
        conexion.commit()
        cursor.close()
    finally:
        conexion.close()
    return resultado


def _hay_trigger():
    return bool(
        _ejecutar(
            "SELECT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_turno_sin_solapamiento')",
            devolver=True,
        )
    )


@unittest.skipUnless(_hay_base(), "No hay base PostgreSQL disponible (ver archivo .env).")
class SolapamientoTurnosTest(unittest.TestCase):
    """Un turno no puede pisar a otro del mismo peluquero o de la misma mascota,
    considerando la duración del servicio (60 min en estas pruebas)."""

    def setUp(self):
        self.limpiar()
        self.id_cliente = _ejecutar(
            "INSERT INTO cliente (nombre, apellido, telefono) "
            "VALUES ('Test', 'Turnos', '000-TEST-TURNOS') RETURNING id_cliente",
            devolver=True,
        )
        self.mascota_1 = self._mascota("TestMascota1")
        self.mascota_2 = self._mascota("TestMascota2")
        self.peluquero_1 = self._peluquero("TestPelu1")
        self.peluquero_2 = self._peluquero("TestPelu2")
        self.servicio = _ejecutar(
            "INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base) "
            "VALUES ('TEST-TURNOS-60', 60, 1000) RETURNING id_servicio",
            devolver=True,
        )

    def tearDown(self):
        self.limpiar()

    def limpiar(self):
        _ejecutar(
            "DELETE FROM turno WHERE id_mascota IN "
            "(SELECT id_mascota FROM mascota WHERE nombre LIKE 'TestMascota%')"
        )
        _ejecutar("DELETE FROM mascota WHERE nombre LIKE 'TestMascota%'")
        _ejecutar("DELETE FROM cliente WHERE telefono = '000-TEST-TURNOS'")
        _ejecutar("DELETE FROM peluquero WHERE nombre LIKE 'TestPelu%'")
        _ejecutar("DELETE FROM servicio WHERE nombre_servicio = 'TEST-TURNOS-60'")

    def _mascota(self, nombre):
        return _ejecutar(
            "INSERT INTO mascota (nombre, id_cliente) VALUES (%s, %s) RETURNING id_mascota",
            (nombre, self.id_cliente),
            devolver=True,
        )

    def _peluquero(self, nombre):
        return _ejecutar(
            "INSERT INTO peluquero (nombre, apellido, telefono) "
            "VALUES (%s, 'Test', '000') RETURNING id_peluquero",
            (nombre,),
            devolver=True,
        )

    def _turno(self, hora, mascota, peluquero, estado="Pendiente"):
        return turnos_dao.crear_turno(
            FECHA, hora, estado, "", mascota, peluquero, self.servicio
        )

    def test_turno_contiguo_esta_permitido(self):
        self._turno(time(10, 0), self.mascota_1, self.peluquero_1)
        # empieza justo cuando termina el anterior: no es solapamiento
        self._turno(time(11, 0), self.mascota_2, self.peluquero_1)

    def test_solapamiento_del_peluquero(self):
        self._turno(time(10, 0), self.mascota_1, self.peluquero_1)
        with self.assertRaisesRegex(ValueError, "peluquero"):
            self._turno(time(10, 30), self.mascota_2, self.peluquero_1)

    def test_solapamiento_de_la_mascota(self):
        self._turno(time(10, 0), self.mascota_1, self.peluquero_1)
        with self.assertRaisesRegex(ValueError, "mascota"):
            self._turno(time(10, 30), self.mascota_1, self.peluquero_2)

    def test_otro_peluquero_y_otra_mascota_puede_coincidir(self):
        self._turno(time(10, 0), self.mascota_1, self.peluquero_1)
        self._turno(time(10, 30), self.mascota_2, self.peluquero_2)

    def test_turno_cancelado_no_bloquea_la_agenda(self):
        self._turno(time(10, 0), self.mascota_1, self.peluquero_1, estado="Cancelado")
        self._turno(time(10, 30), self.mascota_2, self.peluquero_1)

    def test_editar_turno_no_choca_consigo_mismo(self):
        id_turno = self._turno(time(10, 0), self.mascota_1, self.peluquero_1)
        # se corre 30 min: se superpone con su propio horario anterior, pero es el mismo turno
        afectadas = turnos_dao.actualizar_turno(
            id_turno, FECHA, time(10, 30), "Confirmado", "editado",
            self.mascota_1, self.peluquero_1, self.servicio,
        )
        self.assertEqual(afectadas, 1)
        fila = [f for f in turnos_dao.listar_turnos() if f[0] == id_turno][0]
        self.assertEqual(fila[5], time(10, 30))
        self.assertEqual(fila[6], "Confirmado")
        self.assertEqual(fila[7], "editado")

    def test_editar_turno_rechaza_solapamiento_con_otro(self):
        self._turno(time(10, 0), self.mascota_1, self.peluquero_1)
        id_otro = self._turno(time(12, 0), self.mascota_2, self.peluquero_1)
        with self.assertRaisesRegex(ValueError, "peluquero"):
            turnos_dao.actualizar_turno(
                id_otro, FECHA, time(10, 30), "Pendiente", "",
                self.mascota_2, self.peluquero_1, self.servicio,
            )

    def test_editar_turno_inexistente_devuelve_cero(self):
        afectadas = turnos_dao.actualizar_turno(
            -1, FECHA, time(10, 0), "Pendiente", "",
            self.mascota_1, self.peluquero_1, self.servicio,
        )
        self.assertEqual(afectadas, 0)

    def test_cancelar_turno_libera_la_agenda(self):
        id_turno = self._turno(time(10, 0), self.mascota_1, self.peluquero_1)
        turnos_dao.actualizar_turno(
            id_turno, FECHA, time(10, 0), "Cancelado", "",
            self.mascota_1, self.peluquero_1, self.servicio,
        )
        self._turno(time(10, 30), self.mascota_2, self.peluquero_1)

    def test_disponibilidad_considera_la_duracion(self):
        self._turno(time(10, 0), self.mascota_1, self.peluquero_1)
        libre = lambda h: turnos_dao.peluquero_disponible(
            FECHA, h, self.peluquero_1, self.servicio
        )
        self.assertFalse(libre(time(9, 30)))   # 09:30-10:30 pisa el comienzo
        self.assertFalse(libre(time(10, 59)))  # cae dentro del turno existente
        self.assertTrue(libre(time(9, 0)))     # termina justo a las 10:00
        self.assertTrue(libre(time(11, 0)))    # empieza justo a las 11:00

    @unittest.skipUnless(
        _hay_base() and _hay_trigger(),
        "Falta ejecutar scripts/04_prevencion_solapamientos.sql en la base.",
    )
    def test_trigger_rechaza_insercion_directa(self):
        """El control también funciona si alguien escribe en la tabla sin pasar por Python."""
        self._turno(time(10, 0), self.mascota_1, self.peluquero_1)
        with self.assertRaises(errors.ExclusionViolation):
            _ejecutar(
                "INSERT INTO turno (fecha, hora, id_mascota, id_peluquero, id_servicio) "
                "VALUES (%s, %s, %s, %s, %s)",
                (FECHA, time(10, 30), self.mascota_2, self.peluquero_1, self.servicio),
            )


if __name__ == "__main__":
    unittest.main()
