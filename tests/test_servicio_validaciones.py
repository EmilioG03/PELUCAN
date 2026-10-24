import unittest
from decimal import Decimal

from interfaz.paginas.servicio import (
    formatear_precio,
    normalizar_nombre,
    parsear_duracion,
    parsear_precio,
    validar_nombre,
    validar_servicio,
)


class ServicioValidacionesTest(unittest.TestCase):
    def test_normalizar_nombre_colapsa_espacios(self):
        self.assertEqual(normalizar_nombre("  Corte   + Baño "), "Corte + Baño")

    def test_nombre_obligatorio_y_con_largo_maximo(self):
        for valor in ("", "   ", None, "x" * 81):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    validar_nombre(valor)

    def test_duracion_valida(self):
        self.assertEqual(parsear_duracion("45"), 45)
        self.assertEqual(parsear_duracion(" 60 "), 60)

    def test_duracion_invalida(self):
        for valor in ("", "0", "-5", "abc", "4,5", "10.5"):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    parsear_duracion(valor)

    def test_precio_acepta_formatos_locales(self):
        self.assertEqual(parsear_precio("5000"), Decimal("5000.00"))
        self.assertEqual(parsear_precio("5000.50"), Decimal("5000.50"))
        self.assertEqual(parsear_precio("5000,50"), Decimal("5000.50"))
        self.assertEqual(parsear_precio("5.000,50"), Decimal("5000.50"))
        self.assertEqual(parsear_precio("$ 12.000,00"), Decimal("12000.00"))
        self.assertEqual(parsear_precio("0"), Decimal("0.00"))

    def test_precio_invalido(self):
        # "5.000" se rechaza a propósito: tiene 3 decimales y se confunde 5 con 5000.
        for valor in ("", "-1", "abc", "5.000", "1,234", "100000000"):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    parsear_precio(valor)

    def test_validar_servicio_devuelve_los_tres_valores(self):
        self.assertEqual(
            validar_servicio("  Baño   completo ", "45", "12.000,00"),
            ("Baño completo", 45, Decimal("12000.00")),
        )

    def test_formatear_precio(self):
        self.assertEqual(formatear_precio(Decimal("37000")), "$ 37.000,00")
        self.assertEqual(formatear_precio(Decimal("5000.5")), "$ 5.000,50")


if __name__ == "__main__":
    unittest.main()
