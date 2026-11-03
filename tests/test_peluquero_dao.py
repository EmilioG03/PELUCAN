import unittest

import psycopg2
from psycopg2 import errors

from datos import peluquero_dao
from datos.conexion import obtener_conexion


def _hay_base():
    try:
        obtener_conexion().close()
        return True
    except psycopg2.Error:
        return False


def _id_por_telefono(telefono):
    """Id del peluquero con ese teléfono, o None."""
    for fila in peluquero_dao.listar():
        if fila[3] == telefono:
            return fila[0]
    return None


@unittest.skipUnless(_hay_base(), "No hay base PostgreSQL disponible (ver PGUSER/PGPASSWORD).")
class PeluqueroDaoTest(unittest.TestCase):
    TELEFONOS = ["000-PELU-%d" % n for n in range(1, 5)]

    def tearDown(self):
        for telefono in self.TELEFONOS:
            id_peluquero = _id_por_telefono(telefono)
            if id_peluquero:
                peluquero_dao.eliminar(id_peluquero)

    def test_insertar_y_listar(self):
        peluquero_dao.insertar("Prueba", "Dao", "000-PELU-1", "Cachorros")
        id_peluquero = _id_por_telefono("000-PELU-1")
        fila = next(f for f in peluquero_dao.listar() if f[0] == id_peluquero)
        self.assertEqual(fila[1:], ("Prueba", "Dao", "000-PELU-1", "Cachorros"))

    def test_la_especialidad_es_opcional(self):
        peluquero_dao.insertar("Sin", "Especialidad", "000-PELU-2", "")
        id_peluquero = _id_por_telefono("000-PELU-2")
        fila = next(f for f in peluquero_dao.listar() if f[0] == id_peluquero)
        self.assertEqual(fila[4], "")

    def test_actualizar(self):
        peluquero_dao.insertar("Prueba", "Dao", "000-PELU-1", "Cachorros")
        id_peluquero = _id_por_telefono("000-PELU-1")
        peluquero_dao.actualizar(id_peluquero, "Cambiado", "Dao", "000-PELU-1", "")
        fila = next(f for f in peluquero_dao.listar() if f[0] == id_peluquero)
        self.assertEqual(fila[1], "Cambiado")
        self.assertEqual(fila[4], "")

    def test_eliminar(self):
        peluquero_dao.insertar("Prueba", "Dao", "000-PELU-3", "")
        peluquero_dao.eliminar(_id_por_telefono("000-PELU-3"))
        self.assertIsNone(_id_por_telefono("000-PELU-3"))

    def test_buscar_sin_distinguir_mayusculas(self):
        peluquero_dao.insertar("Zulema", "Dao", "000-PELU-4", "Razas grandes")
        self.assertTrue(any(f[1] == "Zulema" for f in peluquero_dao.buscar("zULE")))
        self.assertTrue(any(f[1] == "Zulema" for f in peluquero_dao.buscar("RAZAS")))

    def test_buscar_no_es_vulnerable_a_inyeccion(self):
        self.assertEqual(peluquero_dao.buscar("'; DROP TABLE peluquero; --"), [])
        self.assertGreater(len(peluquero_dao.listar()), 0)

    def test_no_se_elimina_peluquero_con_turnos(self):
        # Peluquera de los datos de prueba, que tiene turnos asignados.
        id_peluquero = _id_por_telefono("351-444-1122")
        if id_peluquero is None:
            self.skipTest("No están cargados los datos de prueba.")
        with self.assertRaises((errors.ForeignKeyViolation, errors.RestrictViolation)):
            peluquero_dao.eliminar(id_peluquero)


if __name__ == "__main__":
    unittest.main()
