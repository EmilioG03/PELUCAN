import unittest
from decimal import Decimal

import psycopg2
from psycopg2 import errors

from datos import servicio_dao
from datos.conexion import obtener_conexion


def _hay_base():
    try:
        obtener_conexion().close()
        return True
    except psycopg2.Error:
        return False


def _id_por_nombre(nombre):
    """Id del servicio con ese nombre, o None."""
    for fila in servicio_dao.listar():
        if fila[1] == nombre:
            return fila[0]
    return None


@unittest.skipUnless(_hay_base(), "No hay base PostgreSQL disponible (ver PELUCAN_DB_USER/PELUCAN_DB_PASSWORD).")
class ServicioDaoTest(unittest.TestCase):
    NOMBRES = ["TEST Servicio %d" % n for n in range(1, 6)]

    def tearDown(self):
        for nombre in self.NOMBRES:
            id_servicio = _id_por_nombre(nombre)
            if id_servicio:
                servicio_dao.eliminar(id_servicio)

    def test_insertar_y_listar(self):
        servicio_dao.insertar("TEST Servicio 1", 45, Decimal("12500.50"))
        id_servicio = _id_por_nombre("TEST Servicio 1")
        fila = next(f for f in servicio_dao.listar() if f[0] == id_servicio)
        self.assertEqual(fila[1:], ("TEST Servicio 1", 45, Decimal("12500.50")))

    def test_actualizar(self):
        servicio_dao.insertar("TEST Servicio 1", 45, Decimal("1000"))
        id_servicio = _id_por_nombre("TEST Servicio 1")
        servicio_dao.actualizar(id_servicio, "TEST Servicio 2", 60, Decimal("2000"))
        fila = next(f for f in servicio_dao.listar() if f[0] == id_servicio)
        self.assertEqual(fila[1:], ("TEST Servicio 2", 60, Decimal("2000.00")))

    def test_eliminar(self):
        servicio_dao.insertar("TEST Servicio 3", 30, Decimal("500"))
        servicio_dao.eliminar(_id_por_nombre("TEST Servicio 3"))
        self.assertIsNone(_id_por_nombre("TEST Servicio 3"))

    def test_nombre_duplicado_lo_rechaza_la_base(self):
        servicio_dao.insertar("TEST Servicio 4", 30, Decimal("500"))
        with self.assertRaises(errors.UniqueViolation):
            servicio_dao.insertar("TEST Servicio 4", 20, Decimal("700"))

    def test_duracion_cero_lo_rechaza_la_base(self):
        with self.assertRaises(errors.CheckViolation):
            servicio_dao.insertar("TEST Servicio 5", 0, Decimal("500"))

    def test_precio_negativo_lo_rechaza_la_base(self):
        with self.assertRaises(errors.CheckViolation):
            servicio_dao.insertar("TEST Servicio 5", 30, Decimal("-1"))

    def test_buscar_sin_distinguir_mayusculas(self):
        servicio_dao.insertar("TEST Servicio 5", 30, Decimal("500"))
        self.assertTrue(any(f[1] == "TEST Servicio 5" for f in servicio_dao.buscar("test SERVICIO 5")))

    def test_buscar_no_es_vulnerable_a_inyeccion(self):
        self.assertEqual(servicio_dao.buscar("'; DROP TABLE servicio; --"), [])
        self.assertGreater(len(servicio_dao.listar()), 0)

    def test_no_se_elimina_servicio_con_turnos(self):
        conexion = obtener_conexion()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id_servicio FROM turno LIMIT 1")
            fila = cursor.fetchone()
            cursor.close()
        finally:
            conexion.close()
        if fila is None:
            self.skipTest("No hay turnos cargados (faltan los datos de prueba).")
        with self.assertRaises((errors.ForeignKeyViolation, errors.RestrictViolation)):
            servicio_dao.eliminar(fila[0])


if __name__ == "__main__":
    unittest.main()
