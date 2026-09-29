"""
paginas/ (paquete)
-------------------
Antes 'paginas' era un solo archivo (paginas.py) con todas las
páginas juntas. Ahora es una carpeta con un módulo por página:

    paginas/
        base.py         -> PaginaBase (encabezado estándar) y
                            PaginaABM (lógica común de listar/
                            cargar/editar/eliminar), juntas porque
                            ninguna de las dos cambia según la entidad
        inicio.py        -> PaginaInicio
        clientes.py       -> PaginaClientes
        mascotas.py        -> PaginaMascotas
        turnos.py            -> PaginaTurnos

No hay página de Servicios: el equipo acordó con la cátedra acotar
el alcance de este hito a Clientes, Mascotas y Turnos.

Este __init__.py reexporta las clases para que el resto del código
(ventana_principal.py) las siga importando exactamente igual que
antes, sin enterarse de que ahora están separadas en archivos:

    from interfaz.paginas import PaginaInicio, PaginaClientes, ...
"""

from interfaz.paginas.base import PaginaBase, PaginaABM
from interfaz.paginas.inicio import PaginaInicio
from interfaz.paginas.clientes import PaginaClientes
from interfaz.paginas.mascotas import PaginaMascotas
from interfaz.paginas.turnos import PaginaTurnos

__all__ = [
    "PaginaBase",
    "PaginaABM",
    "PaginaInicio",
    "PaginaClientes",
    "PaginaMascotas",
    "PaginaTurnos",
]
