from interfaz.paginas.base import PaginaABM

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
