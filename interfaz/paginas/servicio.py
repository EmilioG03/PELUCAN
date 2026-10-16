
from tkinter import messagebox

from datos.servicios_db import (
    DuplicadoError,
    NoEncontradoError,
    ServicioDAO,
    ServicioEnUsoError,
    ServicioError,
    ValidacionError,
    formatear_precio,
)

from .base import PaginaABM


class PaginaServicios(PaginaABM):
    titulo = "Servicios"
    subtitulo = "Catálogo de prestaciones, duración estimada y precio base."

    columnas = [
        ("nombre_servicio", "Servicio"),
        ("duracion_estimada", "Duración (min)"),
        ("precio_base", "Precio base"),
    ]

    # Una sola instancia de acceso a datos para toda la página.
    # No abre ninguna conexión hasta que se hace una operación.
    dao = ServicioDAO()

    # ------------------------------------------------------------------
    # Carga de datos
    # ------------------------------------------------------------------
    def construir_contenido(self):
        self._cargar_datos()
        super().construir_contenido()

    def recargar(self):
        """Vuelve a leer el catálogo de la base y actualiza el listado.
        Se puede llamar desde el navegador al mostrar la página."""
        self._cargar_datos()
        self._refrescar_listado()

    def _cargar_datos(self):
        try:
            servicios = self.dao.listar()
        except ServicioError as exc:
            messagebox.showerror("No se pudo cargar el catálogo", str(exc))
            servicios = []
        self.datos = [self._a_registro(s) for s in servicios]

    @staticmethod
    def _a_registro(servicio):
        """Convierte un Servicio en el dict que usa el listado.
        Guarda el objeto original para editar sin volver a parsear textos."""
        return {
            "id_servicio": servicio.id_servicio,
            "nombre_servicio": servicio.nombre_servicio,
            "duracion_estimada": str(servicio.duracion_estimada),
            "precio_base": formatear_precio(servicio.precio_base),
            "_servicio": servicio,
        }

    # ------------------------------------------------------------------
    # Acciones (reemplazan las versiones en memoria de PaginaABM)
    # ------------------------------------------------------------------
    def _registro_seleccionado(self, accion):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning(
                "Nada seleccionado",
                f"Seleccioná un servicio del listado para {accion}.",
            )
            return None, None
        indice = int(seleccion[0])
        return indice, self.datos[indice]

    def _al_presionar_editar(self):
        indice, registro = self._registro_seleccionado("editar")
        if registro is None:
            return
        servicio = registro["_servicio"]
        self.fila_seleccionada = indice
        self.variables["nombre_servicio"].set(servicio.nombre_servicio)
        self.variables["duracion_estimada"].set(str(servicio.duracion_estimada))
        self.variables["precio_base"].set(f"{servicio.precio_base:.2f}".replace(".", ","))
        self._mostrar_vista_formulario()

    def _al_presionar_guardar(self):
        valores = {clave: var.get() for clave, var in self.variables.items()}
        es_alta = self.fila_seleccionada is None

        try:
            if es_alta:
                self.dao.crear(
                    valores["nombre_servicio"],
                    valores["duracion_estimada"],
                    valores["precio_base"],
                )
            else:
                self.dao.actualizar(
                    self.datos[self.fila_seleccionada]["id_servicio"],
                    valores["nombre_servicio"],
                    valores["duracion_estimada"],
                    valores["precio_base"],
                )
        except ValidacionError as exc:
            messagebox.showwarning("Dato inválido", str(exc))
            return
        except DuplicadoError as exc:
            messagebox.showerror("Servicio duplicado", str(exc))
            return
        except NoEncontradoError as exc:
            # Otra persona lo eliminó mientras se editaba: se vuelve al listado.
            messagebox.showwarning("Servicio inexistente", str(exc))
            self._cargar_datos()
            self._mostrar_vista_listado()
            return
        except ServicioError as exc:
            messagebox.showerror("No se pudo guardar", str(exc))
            return

        self._cargar_datos()
        messagebox.showinfo(
            "Listo",
            "Servicio agregado correctamente." if es_alta
            else "Servicio actualizado correctamente.",
        )
        self._mostrar_vista_listado()

    def _al_presionar_eliminar(self):
        _, registro = self._registro_seleccionado("eliminar")
        if registro is None:
            return

        confirmar = messagebox.askyesno(
            "Eliminar",
            f'¿Seguro que querés eliminar el servicio "{registro["nombre_servicio"]}"? '
            "Esta acción no se puede deshacer.",
        )
        if not confirmar:
            return

        try:
            self.dao.eliminar(registro["id_servicio"])
        except ServicioEnUsoError as exc:
            messagebox.showwarning("No se puede eliminar", str(exc))
            return
        except NoEncontradoError as exc:
            messagebox.showwarning("Servicio inexistente", str(exc))
        except ServicioError as exc:
            messagebox.showerror("No se pudo eliminar", str(exc))
            return

        self._cargar_datos()
        self._refrescar_listado()

    def _mostrar_detalle(self, evento):
        """Doble clic: resumen del servicio (la base muestra observaciones,
        que los servicios no tienen)."""
        item_id = self.tabla.identify_row(evento.y)
        if not item_id:
            return
        reg = self.datos[int(item_id)]
        messagebox.showinfo(
            f"Servicio - {reg['nombre_servicio']}",
            f"Duración estimada: {reg['duracion_estimada']} minutos\n"
            f"Precio base: {reg['precio_base']}",
        )
