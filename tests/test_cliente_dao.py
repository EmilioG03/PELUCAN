import unittest

import psycopg2
from psycopg2 import errors

from datos import cliente_dao
from datos.conexion import obtener_conexion


def _hay_base():
    try:
        obtener_conexion().close()
        return True
    except psycopg2.Error:
        return False


def _id_por_telefono(telefono):
    """Id del cliente con ese teléfono, o None."""
    for fila in cliente_dao.listar():
        if fila[3] == telefono:
            return fila[0]
    return None


@unittest.skipUnless(_hay_base(), "No hay base PostgreSQL disponible (ver PGUSER/PGPASSWORD).")
class ClienteDaoTest(unittest.TestCase):
    TELEFONOS = ["000-TEST-%d" % n for n in range(1, 8)]

    def tearDown(self):
        for telefono in self.TELEFONOS:
            id_cliente = _id_por_telefono(telefono)
            if id_cliente:
                cliente_dao.eliminar(id_cliente)

    def test_insertar_y_listar(self):
        cliente_dao.insertar("Prueba", "Dao", "000-TEST-1", "prueba.dao@mail.com")
        id_cliente = _id_por_telefono("000-TEST-1")
        fila = next(f for f in cliente_dao.listar() if f[0] == id_cliente)
        self.assertEqual(fila[1:], ("Prueba", "Dao", "000-TEST-1", "prueba.dao@mail.com"))

    def test_actualizar(self):
        cliente_dao.insertar("Prueba", "Dao", "000-TEST-1", "prueba.dao@mail.com")
        id_cliente = _id_por_telefono("000-TEST-1")
        cliente_dao.actualizar(id_cliente, "Cambiado", "Dao", "000-TEST-1", "")
        fila = next(f for f in cliente_dao.listar() if f[0] == id_cliente)
        self.assertEqual(fila[1], "Cambiado")
        self.assertEqual(fila[4], "")

    def test_eliminar(self):
        cliente_dao.insertar("Prueba", "Dao", "000-TEST-1", "")
        cliente_dao.eliminar(_id_por_telefono("000-TEST-1"))
        self.assertIsNone(_id_por_telefono("000-TEST-1"))

    def test_telefono_duplicado_lo_rechaza_la_base(self):
        cliente_dao.insertar("Uno", "Dao", "000-TEST-2", "uno@mail.com")
        with self.assertRaises(errors.UniqueViolation):
            cliente_dao.insertar("Dos", "Dao", "000-TEST-2", "dos@mail.com")

    def test_email_duplicado_lo_rechaza_la_base(self):
        cliente_dao.insertar("Uno", "Dao", "000-TEST-3", "igual@mail.com")
        with self.assertRaises(errors.UniqueViolation):
            cliente_dao.insertar("Dos", "Dao", "000-TEST-4", "igual@mail.com")

    def test_varios_clientes_sin_email(self):
        cliente_dao.insertar("Uno", "Dao", "000-TEST-5", "")
        cliente_dao.insertar("Dos", "Dao", "000-TEST-6", "")

    def test_buscar_sin_distinguir_mayusculas(self):
        cliente_dao.insertar("Zulema", "Dao", "000-TEST-7", "")
        self.assertTrue(any(f[1] == "Zulema" for f in cliente_dao.buscar("zULE")))

    def test_buscar_no_es_vulnerable_a_inyeccion(self):
        self.assertEqual(cliente_dao.buscar("'; DROP TABLE cliente; --"), [])
        self.assertGreater(len(cliente_dao.listar()), 0)

    def test_no_se_elimina_cliente_con_mascotas(self):
        with self.assertRaises((errors.ForeignKeyViolation, errors.RestrictViolation)):
            cliente_dao.eliminar(_id_por_telefono("351-555-0110"))


if __name__ == "__main__":
    unittest.main()
