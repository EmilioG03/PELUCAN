# 🐾 PELUCAN

<p align="center">
  <strong>Sistema de gestión para peluquerías caninas</strong><br>
  Proyecto ABP · Módulo Programador · Ctrl+E · Comisión A
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Interfaz-Tkinter-1A5C4A?style=for-the-badge" alt="Tkinter">
  <img src="https://img.shields.io/badge/Estado-En%20desarrollo-F0A500?style=for-the-badge" alt="Estado: en desarrollo">
</p>

## Descripción

**PELUCAN** es una aplicación de escritorio desarrollada para organizar las tareas habituales de una peluquería canina. Su objetivo es centralizar la información de clientes, mascotas y turnos, facilitando la consulta, el registro y la actualización de los datos desde una interfaz clara y sencilla.

El proyecto se desarrolla como parte del Aprendizaje Basado en Proyectos (ABP) del **Módulo Programador**, integrando contenidos de Programación y Base de Datos.

> **Estado actual:** la aplicación cuenta con una interfaz funcional y operaciones ABM realizadas en memoria. La persistencia en base de datos todavía se encuentra planificada y los datos se reinician al cerrar el programa.

## Funcionalidades implementadas

- Panel de inicio con métricas generales.
- Navegación lateral entre las distintas secciones.
- Listado de clientes, mascotas y turnos.
- Alta, modificación y eliminación de registros.
- Búsqueda general y filtrado por columnas.
- Validación de campos obligatorios.
- Control de teléfonos duplicados.
- Confirmación antes de eliminar información.
- Visualización de observaciones mediante doble clic.
- Selección de servicios, horarios y estados mediante listas desplegables.
- Interfaz modular con estilos reutilizables.

## Tecnologías utilizadas

| Tecnología | Uso dentro del proyecto |
|---|---|
| Python | Lógica general de la aplicación |
| Tkinter / ttk | Construcción de la interfaz gráfica |
| tkcalendar | Selector visual de fechas, cuando está instalado |
| Git y GitHub | Versionado y trabajo colaborativo |
| PostgreSQL | Persistencia de datos planificada para la siguiente etapa |

## Estructura del proyecto

```text
PELUCAN/
├── main.py
├── .gitignore
└── interfaz/
    ├── __init__.py
    ├── estilos.py
    ├── header.py
    ├── navegador.py
    ├── sidebar.py
    ├── ventana_principal.py
    └── paginas/
        ├── __init__.py
        ├── base.py
        ├── inicio.py
        ├── clientes.py
        ├── mascotas.py
        └── turnos.py
```

### Organización interna

- `main.py`: punto de entrada de la aplicación.
- `ventana_principal.py`: integra la cabecera, el menú lateral y el navegador.
- `estilos.py`: concentra colores, tipografías y estilos visuales.
- `header.py`, `sidebar.py` y `navegador.py`: componentes reutilizables de navegación.
- `paginas/base.py`: contiene las clases base y la lógica común de las pantallas ABM.
- `paginas/clientes.py`: administración de clientes.
- `paginas/mascotas.py`: administración de mascotas.
- `paginas/turnos.py`: administración de turnos.
- `paginas/inicio.py`: panel general y resumen de actividad.

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/EmilioG03/PELUCAN.git
cd PELUCAN
```

### 2. Crear un entorno virtual

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

En Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar la dependencia opcional

```bash
pip install tkcalendar
```

La aplicación puede ejecutarse sin `tkcalendar`, aunque el campo de fecha utilizará una entrada de texto convencional.

### 4. Iniciar la aplicación

En Windows:

```bash
python main.py
```

En algunos sistemas Linux o macOS:

```bash
python3 main.py
```

## Flujo básico de uso

1. Ingresar a **Clientes**, **Mascotas** o **Turnos** desde el menú lateral.
2. Utilizar **Nuevo** para registrar información.
3. Seleccionar una fila y presionar **Editar** para modificarla.
4. Seleccionar una fila y presionar **Eliminar** para quitarla.
5. Escribir en el buscador y elegir una columna para filtrar los resultados.
6. Hacer doble clic sobre un registro para consultar sus observaciones.

## Modelo funcional

La aplicación trabaja con tres entidades principales:

- **Cliente:** persona responsable de una o más mascotas.
- **Mascota:** animal asociado a un cliente y destinatario de los servicios.
- **Turno:** reserva que vincula una mascota con un servicio, una fecha, un horario y un estado.

Los estados contemplados para los turnos son:

- Pendiente
- Confirmado
- Completado
- Cancelado

## Próximas etapas

- [ ] Conectar la aplicación con PostgreSQL.
- [ ] Crear una capa independiente de acceso a datos.
- [ ] Reemplazar los datos de ejemplo por información persistente.
- [ ] Relacionar clientes, mascotas, turnos y servicios mediante claves foráneas.
- [ ] Evitar la superposición de turnos.
- [ ] Incorporar usuarios y permisos según el rol.
- [ ] Ampliar las validaciones de teléfono, correo, fecha y horario.
- [ ] Incorporar pruebas unitarias y de integración.
- [ ] Agregar capturas de pantalla y documentación técnica.
- [ ] Preparar una versión distribuible de la aplicación.

## Equipo de trabajo

| Integrante | Responsabilidad principal |
|---|---|
| Federico Montoro | Coordinación e integración del proyecto |
| Marcelo Nahuel Raspo | Diseño y desarrollo de la interfaz |
| Fiorella Easdale Castillo | Modelado de datos |
| Josefina Madai Alcaraz | Acceso y persistencia de datos |
| Emmanuel Gillio | Validaciones y reglas de negocio |
| Emilio Santiago Guzmán | Documentación y pruebas |

## Recursos del proyecto

- [Repositorio en GitHub](https://github.com/EmilioG03/PELUCAN)
- [Prototipo de interfaz en Figma](https://www.figma.com/design/cHTpfQIOm9YoNabzMTpq53/Untitled?node-id=0-1&t=onKsCF2z3NQCWufN-1)
- [Modelo entidad–relación](https://drive.google.com/file/d/12lx95Q8Cd3X3ZS0SgkKPdsak2LiHMLwc/view?usp=sharing)

## Trabajo colaborativo

Para evitar conflictos, cada cambio debe realizarse en una rama propia:

```bash
git switch -c nombre/tarea
git add .
git commit -m "tipo: descripción breve del cambio"
git push -u origin nombre/tarea
```

Luego se crea un **Pull Request** hacia `main` para revisar e integrar el trabajo.

Algunos prefijos sugeridos para los commits:

- `feat:` nueva funcionalidad.
- `fix:` corrección de un error.
- `refactor:` reorganización del código sin cambiar su comportamiento.
- `docs:` documentación.
- `test:` incorporación o modificación de pruebas.
- `chore:` mantenimiento general del proyecto.

---

<p align="center">
  Desarrollado colaborativamente por el equipo Ctrl+E de la Comisión A · 2026
</p>

