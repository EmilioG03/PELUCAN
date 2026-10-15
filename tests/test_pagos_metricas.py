import unittest
from datetime import date
from decimal import Decimal

from interfaz.paginas.inicio import calcular_metricas, formatear_pesos
from interfaz.paginas.pagos import convertir_monto, total_ingresos, turno_ya_pagado
from scripts.backup_bd import construir_comando


class PagosTest(unittest.TestCase):
    def test_convertir_monto_acepta_formatos_locales(self):
        self.assertEqual(convertir_monto("12.500,50"), Decimal("12500.50"))
        self.assertEqual(convertir_monto("12500.50"), Decimal("12500.50"))

    def test_convertir_monto_rechaza_valores_invalidos(self):
        for valor in ("", "abc", "0", "-10"):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    convertir_monto(valor)

    def test_total_ingresos_filtra_por_fecha(self):
        pagos = [
            {"monto": "1200", "fecha_pago": "01/10/2026"},
            {"monto": "800,50", "fecha_pago": "01/10/2026"},
            {"monto": "900", "fecha_pago": "02/10/2026"},
        ]
        self.assertEqual(total_ingresos(pagos, date(2026, 10, 1)), Decimal("2000.50"))

    def test_un_turno_no_admite_dos_pagos(self):
        pagos = [{"turno": "Turno #1"}, {"turno": "Turno #2"}]
        self.assertTrue(turno_ya_pagado(pagos, "Turno #1"))
        self.assertFalse(turno_ya_pagado(pagos, "Turno #1", ignorar_indice=0))


class DashboardTest(unittest.TestCase):
    def test_metricas_de_fecha_con_datos_de_ejemplo(self):
        metricas = calcular_metricas(date(2026, 8, 31))
        self.assertEqual(metricas["turnos"], 14)
        self.assertEqual(metricas["clientes"], 15)
        self.assertEqual(metricas["mascotas"], 15)
        self.assertEqual(metricas["ingresos"], Decimal("37000.00"))

    def test_formatear_pesos(self):
        self.assertEqual(formatear_pesos(Decimal("37000")), "$ 37.000,00")


class BackupTest(unittest.TestCase):
    def test_construir_comando_pg_dump(self):
        comando = construir_comando("pelucan", "backups/pelucan.backup")
        self.assertEqual(comando[0], "pg_dump")
        self.assertIn("--format=custom", comando)
        self.assertIn("--file=backups/pelucan.backup", comando)
        self.assertEqual(comando[-1], "pelucan")


if __name__ == "__main__":
    unittest.main()
