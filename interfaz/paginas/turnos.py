from interfaz.paginas.base import PaginaABM
from datetime import date, timedelta, time, datetime
from tkinter import messagebox

from interfaz.paginas.base import PaginaABM
from interfaz.paginas.mascotas import MASCOTAS_EJEMPLO, etiqueta_mascota

HORARIOS_DISPONIBLES = [
    f"{hora:02d}:{minuto:02d}"
    for hora in range(8, 20)
    for minuto in (0, 30)
]

ESTADOS_ACTIVOS = ("Pendiente", "Confirmado")

def _fecha(dias):
    """Fecha relativa a hoy en formato dd/mm/aaaa (así los datos de ejemplo nunca quedan viejos)."""
    return (date.today() + timedelta(days=dias)).strftime("%d/%m/%Y")

def _turno(mascota, servicio, dias, hora, estado, observaciones=""):
    etiqueta = etiqueta_mascota(next(m for m in MASCOTAS_EJEMPLO if m["nombre"] == mascota))
    return {
        "mascota": etiqueta, "servicio": servicio, "fecha": _fecha(dias),
        "hora": hora, "estado": estado, "observaciones": observaciones,
    }

TURNOS_EJEMPLO = [
    {"mascota": "Luna (Caniche)", "servicio": "Baño completo", "fecha": "31/08/2026", "hora": "09:00", "estado": "Pendiente", "observaciones": ""},
    {"mascota": "Bruno (Labrador)", "servicio": "Corte + Baño", "fecha": "31/08/2026", "hora": "10:30", "estado": "Confirmado", "observaciones": "Cuidado con piel sensible"},
    {"mascota": "Toby (Cocker)", "servicio": "Corte de uñas", "fecha": "31/08/2026", "hora": "11:45", "estado": "Confirmado", "observaciones": "Enojo fácil"},
    {"mascota": "Milo (Beagle)", "servicio": "Baño sanitario", "fecha": "31/08/2026", "hora": "11:15", "estado": "Pendiente", "observaciones": "Traer toalla propia"},
    {"mascota": "Simón (Bulldog Francés)", "servicio": "Baño completo", "fecha": "31/08/2026", "hora": "12:00", "estado": "Cancelado", "observaciones": "Avisó por WhatsApp"},
    {"mascota": "Kira (Ovejero Alemán)", "servicio": "Deslanado + Baño", "fecha": "31/08/2026", "hora": "13:30", "estado": "Confirmado", "observaciones": "Trabajo de 2 horas"},
    {"mascota": "Rocco (Boxer)", "servicio": "Baño completo", "fecha": "31/08/2026", "hora": "14:15", "estado": "Pendiente", "observaciones": "Usar shampoo neutro"},
    {"mascota": "Lola (Golden Retriever)", "servicio": "Corte + Baño", "fecha": "31/08/2026", "hora": "15:00", "estado": "Confirmado", "observaciones": "Desenredo profundo"},
    {"mascota": "Bobi (Mestizo)", "servicio": "Baño express", "fecha": "31/08/2026", "hora": "15:45", "estado": "Completado", "observaciones": "Secador a temperatura tibia"},
    {"mascota": "Mia (Shih Tzu)", "servicio": "Corte higiénico", "fecha": "31/08/2026", "hora": "16:30", "estado": "Confirmado", "observaciones": "Moño rojo al terminar"},
    {"mascota": "Thor (Rottweiler)", "servicio": "Baño completo", "fecha": "31/08/2026", "hora": "17:15", "estado": "Pendiente", "observaciones": "Manejar con cuidado"},
    {"mascota": "Bella (Pug)", "servicio": "Limpieza de pliegues + Baño", "fecha": "31/08/2026", "hora": "18:00", "estado": "Confirmado", "observaciones": ""},
    {"mascota": "Zeus (Husky)", "servicio": "Cepillado profundo", "fecha": "31/08/2026", "hora": "18:45", "estado": "Pendiente", "observaciones": "Mucha paciencia con la cola"},
    {"mascota": "Ciro (Dachshund)", "servicio": "Corte de uñas + Oídos", "fecha": "31/08/2026", "hora": "19:15", "estado": "Completado", "observaciones": "Control veterinario al día"},
    {"mascota": "Nina (Schnauzer Mini)", "servicio": "Corte estándar", "fecha": "31/08/2026", "hora": "19:45", "estado": "Pendiente", "observaciones": "Mantener barba larga"},
]


class PaginaTurnos(PaginaABM):
    titulo = "Listado de Turnos"
    subtitulo = "Administración y búsqueda general de citas programadas en el sistema."
    columnas = [
        ("mascota", "Mascota"),
        ("servicio", "Servicio"),
        ("fecha", "Fecha"),
        ("hora", "Hora"),
        ("estado", "Estado"),
        ("observaciones", "Observaciones"),
    ]
    datos_iniciales = TURNOS_EJEMPLO
    campo_busqueda = "mascota"

    campos_fecha = ["fecha"]

    opciones_desplegables = {
        "servicio": [
            "Baño completo",
            "Corte + Baño",
            "Corte de uñas",
            "Corte de uñas + Oídos",
            "Corte de uñas + Cepillado",
            "Corte higiénico",
            "Corte estándar",
            "Baño express",
            "Baño sanitario",
            "Deslanado + Baño",
            "Cepillado profundo",
            "Limpieza de pliegues + Baño",
        ],
        "estado": [
            "Pendiente",
            "Confirmado",
            "Completado",
            "Cancelado",
        ],
        "hora": HORARIOS_DISPONIBLES,
    }

    def _validar_datos(self, valores):
        if not super()._validar_datos(valores):
            return False
        fecha = datetime.strptime(valores["fecha"], "%d/%m/%Y").date()
        hora = time.fromisoformat(valores["hora"])
        
        if self.fila_seleccionada is None and datetime.combine(fecha, hora) < datetime.now():
            messagebox.showerror("Fecha y hora pasadas", "No se puede agendar un turno en una fecha u hora que ya pasó.")
            return False

        if valores["estado"] in ESTADOS_ACTIVOS:
                for i, turno in enumerate(self.datos):
                    if i == self.fila_seleccionada or turno["estado"] not in ESTADOS_ACTIVOS:
                        continue
                    if turno["fecha"] == valores["fecha"] and turno["hora"] == valores["hora"]:
                        messagebox.showerror(
                            "Horario ocupado",
                            f"El {turno['fecha']} a las {turno['hora']} ya hay un turno para {turno['mascota']}.",
                        )
                        return False
        return True