from tkinter import messagebox
from interfaz.paginas.base import PaginaABM
from interfaz.paginas.clientes import CLIENTES_EJEMPLO, etiqueta_cliente

MASCOTAS_EJEMPLO = [
    {"nombre": "Luna", "raza": "Caniche", "edad": "3", "tamano": "Pequeño", "dueno": "Carlos Gómez", "observaciones": "Ninguna"},
    {"nombre": "Bruno", "raza": "Labrador", "edad": "5", "tamano": "Grande", "dueno": "Ana Ferreyra", "observaciones": "Piel sensible"},
    {"nombre": "Toby", "raza": "Cocker", "edad": "2", "tamano": "Mediano", "dueno": "Marcos Díaz", "observaciones": "Enojo fácil"},
    {"nombre": "Milo", "raza": "Beagle", "edad": "4", "tamano": "Mediano", "dueno": "Lucía Romero", "observaciones": "Muy inquieto"},
    {"nombre": "Simón", "raza": "Bulldog Francés", "edad": "1", "tamano": "Pequeño", "dueno": "Martín Sosa", "observaciones": "Problemas respiratorios leves"},
    {"nombre": "Kira", "raza": "Ovejero Alemán", "edad": "6", "tamano": "Grande", "dueno": "Valeria Benítez", "observaciones": "Muy dócil"},
    {"nombre": "Rocco", "raza": "Boxer", "edad": "3", "tamano": "Grande", "dueno": "Esteban Torres", "observaciones": "Alérgico a perfumes fuertes"},
    {"nombre": "Lola", "raza": "Golden Retriever", "edad": "2", "tamano": "Grande", "dueno": "Camila Navarro", "observaciones": "Cuidado con nudos en las orejas"},
    {"nombre": "Bobi", "raza": "Mestizo", "edad": "7", "tamano": "Mediano", "dueno": "Federico Castro", "observaciones": "Asustadizo con el secador"},
    {"nombre": "Mia", "raza": "Shih Tzu", "edad": "4", "tamano": "Pequeño", "dueno": "Mariana Herrera", "observaciones": "Requiere desenredo suave"},
    {"nombre": "Thor", "raza": "Rottweiler", "edad": "5", "tamano": "Grande", "dueno": "Gonzalo Paz", "observaciones": "Usar bozal preventivo"},
    {"nombre": "Bella", "raza": "Pug", "edad": "3", "tamano": "Pequeño", "dueno": "Florencia Medina", "observaciones": "Limpieza especial de pliegues"},
    {"nombre": "Zeus", "raza": "Husky Siberiano", "edad": "4", "tamano": "Grande", "dueno": "Agustín Vega", "observaciones": "Mucha muda de pelo"},
    {"nombre": "Ciro", "raza": "Dachshund", "edad": "2", "tamano": "Pequeño", "dueno": "Sofía Ríos", "observaciones": "Cuidar la columna al alzar"},
    {"nombre": "Nina", "raza": "Schnauzer Mini", "edad": "3", "tamano": "Pequeño", "dueno": "Joaquín Molina", "observaciones": "Corte de raza tradicional"},
]

def etiqueta_mascota(mascota):
    """Texto con el que se muestra una mascota en los desplegables."""
    return f"{mascota['nombre']} ({mascota['raza']})"

class PaginaMascotas(PaginaABM):
    titulo = "Listado de Mascotas"
    subtitulo = "Administración y búsqueda general de mascotas registradas."
    columnas = [
        ("nombre", "Nombre"),
        ("raza", "Raza"),
        ("edad", "Edad"),
        ("tamano", "Tamaño"),
        ("dueno", "Dueño/a"),
        ("observaciones", "Observaciones"),
    ]
    datos_iniciales = MASCOTAS_EJEMPLO
    campo_busqueda = "nombre"

    opciones_desplegables = {
        "tamano": ["Pequeño", "Mediano", "Grande"],
        "dueno": lambda: [etiqueta_cliente(c) for c in CLIENTES_EJEMPLO],
    }
    
    def _al_presionar_eliminar(self):
        seleccion = self.tabla.selection()
        if seleccion:
            from interfaz.paginas.turnos import TURNOS_EJEMPLO
            etiqueta = etiqueta_mascota(self.datos[int(seleccion[0])])
            if any(t["mascota"] == etiqueta for t in TURNOS_EJEMPLO):
                messagebox.showwarning("No se puede eliminar", f"{etiqueta} tiene turnos registrados. Eliminá o cancelá esos turnos primero.")
                return
        super()._al_presionar_eliminar()
