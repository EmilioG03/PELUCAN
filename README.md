# 🐾 PELUCAN

<p align="center">
  <strong>Sistema de gestión para peluquerías caninas</strong><br>
  Proyecto ABP · Módulo Programador · Ctrl+E · Comisión A
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Interfaz-Tkinter-1A5C4A?style=for-the-badge" alt="Tkinter">
  <img src="https://img.shields.io/badge/Base%20de%20datos-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Estado-En%20desarrollo-F0A500?style=for-the-badge" alt="Estado: en desarrollo">
</p>

## Descripción

**PELUCAN** es una aplicación de escritorio destinada a organizar las tareas habituales de una peluquería canina. Centraliza la información de clientes, mascotas, personal, servicios, turnos y pagos mediante una interfaz clara desarrollada con Python y Tkinter.

El proyecto se realiza como parte del Aprendizaje Basado en Proyectos (ABP) del **Módulo Programador**, integrando contenidos de **Base de Datos** y **Programación I**.

> **Estado actual:** la interfaz permite realizar operaciones ABM en memoria, incluido el registro de pagos 1:1 con turnos. El panel calcula métricas diarias y el modelo PostgreSQL incluye las seis entidades, relaciones, restricciones y datos iniciales. La conexión directa entre Python y PostgreSQL se encuentra en desarrollo.

## Funcionalidades implementadas

- Panel de inicio con turnos e ingresos del día y totales de clientes y mascotas.
- Navegación lateral entre las distintas secciones.
- Listado de clientes, mascotas, turnos y pagos.
- Alta, modificación y eliminación de registros.
- Búsqueda general y filtrado por columnas.
- Validación de campos obligatorios y teléfonos duplicados.
- Confirmación antes de eliminar información.
- Visualización de observaciones mediante doble clic.
- Selección de servicios, horarios y estados mediante listas desplegables.
- Validación de montos, métodos de pago y relación única entre pago y turno.
- Interfaz modular con estilos reutilizables.
- Script DDL de PostgreSQL con tablas, claves foráneas, restricciones y datos de prueba.
- Script automatizado de respaldo mediante `pg_dump`.
- Pruebas unitarias para pagos, métricas y construcción del backup.

## Tecnologías utilizadas

| Tecnología | Uso dentro del proyecto |
|---|---|
| Python | Lógica general de la aplicación |
| Tkinter / ttk | Construcción de la interfaz gráfica |
| tkcalendar | Selector visual de fechas, cuando está instalado |
| PostgreSQL | Modelo relacional y persistencia planificada |
| SQL | DDL, restricciones, inserciones y consultas |
| Git y GitHub | Versionado y trabajo colaborativo |

## Estructura del proyecto

~~~text
PELUCAN/
├── main.py
├── pelucan_ddl.sql
├── .gitignore
├── scripts/
│   └── backup_bd.py
├── tests/
│   └── test_pagos_metricas.py
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
        ├── turnos.py
        └── pagos.py
~~~

### Organización interna

- **main.py:** punto de entrada de la aplicación.
- **pelucan_ddl.sql:** tablas, relaciones, restricciones y datos iniciales de PostgreSQL.
- **ventana_principal.py:** integra la cabecera, el menú lateral y el navegador.
- **estilos.py:** concentra colores, tipografías y estilos visuales.
- **header.py, sidebar.py y navegador.py:** componentes reutilizables de navegación.
- **paginas/base.py:** clases base y lógica común de las pantallas ABM.
- **paginas/clientes.py:** administración de clientes.
- **paginas/mascotas.py:** administración de mascotas.
- **paginas/turnos.py:** administración de turnos.
- **paginas/pagos.py:** administración de pagos y validación de la relación 1:1 con turnos.
- **paginas/inicio.py:** panel general con métricas dinámicas por fecha.
- **scripts/backup_bd.py:** generación de respaldos PostgreSQL en formato personalizado.
- **tests/test_pagos_metricas.py:** pruebas automáticas del módulo de pagos y del panel.

## Instalación y ejecución

### 1. Clonar el repositorio

~~~bash
git clone https://github.com/EmilioG03/PELUCAN.git
cd PELUCAN
~~~

### 2. Crear un entorno virtual

En Windows:

~~~bash
python -m venv .venv
.venv\Scripts\activate
~~~

En Linux o macOS:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

### 3. Instalar la dependencia opcional

~~~bash
pip install tkcalendar
~~~

La aplicación puede ejecutarse sin tkcalendar, aunque el campo de fecha utilizará una entrada de texto convencional.

### 4. Iniciar la aplicación

En Windows:

~~~bash
python main.py
~~~

En algunos sistemas Linux o macOS:

~~~bash
python3 main.py
~~~

### 5. Ejecutar las pruebas

~~~bash
python -m unittest discover -s tests -v
~~~

### 6. Generar un respaldo de PostgreSQL

Con `pg_dump` instalado y las variables `PGHOST`, `PGPORT`, `PGUSER` y `PGPASSWORD` configuradas:

~~~bash
python scripts/backup_bd.py --database pelucan
~~~

El archivo se genera dentro de `backups/`, una carpeta excluida del control de versiones para evitar subir información sensible.

## Modelo funcional

La base de datos trabaja con seis entidades principales:

- **Cliente:** persona responsable de una o más mascotas.
- **Mascota:** animal asociado a un cliente y destinatario de los servicios.
- **Servicio:** prestación ofrecida, con duración estimada y precio base.
- **Peluquero:** integrante del personal asignable a los turnos.
- **Turno:** reserva que relaciona una mascota, un peluquero y un servicio en una fecha y horario.
- **Pago:** registro vinculado de manera única con un turno.

Los estados contemplados para los turnos son: **Pendiente, Confirmado, Completado y Cancelado**.

## Distribución homogénea del trabajo ABP

Para cumplir con los lineamientos del ABP, el sistema se divide en **seis módulos funcionales**. Cada integrante participa tanto en **Base de Datos** como en **Programación I**, con responsabilidad de punta a punta sobre su módulo. Así, todos generan evidencia de autoría mediante scripts SQL, código Python y commits en GitHub.

### 1. Josefina Madai Alcaraz — Gestión de Clientes

**Base de Datos**

- Diseño, normalización y restricciones de integridad de la tabla cliente.
- Aplicación de NOT NULL y UNIQUE sobre los datos correspondientes.
- Creación de datos de prueba para clientes.

**Programación I**

- Desarrollo de las pantallas de listado, alta, edición y ficha del cliente.
- Validación de teléfonos duplicados.
- Consultas parametrizadas SELECT, INSERT, UPDATE y DELETE.

### 2. Fiorella Easdale Castillo — Gestión de Mascotas

**Base de Datos**

- Modelado de la relación 1:N entre cliente y mascota.
- Definición de la clave foránea id_cliente, tipos de datos y restricciones de edad.
- Elaboración del diccionario de datos del módulo.

**Programación I**

- Desarrollo de las pantallas de listado, alta y ficha de mascotas.
- Visualización del historial de cada mascota.
- Consultas con JOIN entre clientes y mascotas.

### 3. Emmanuel Gillio — Catálogo de Servicios y Precios

**Base de Datos**

- Diseño de la entidad servicio.
- Restricciones CHECK para duración estimada y precio base.
- Definición de las reglas de negocio del catálogo de prestaciones.

**Programación I**

- Desarrollo de la interfaz de administración de servicios.
- Implementación de operaciones CRUD para altas, bajas, consultas y modificaciones.

### 4. Emilio Santiago Guzmán — Gestión de Personal

**Base de Datos**

- Diseño de la tabla peluquero.
- Definición de roles y permisos diferenciados de lectura y escritura en el SGBD.
- Control de restricciones vinculadas con la agenda.

**Programación I**

- Desarrollo de la lógica para consultar la disponibilidad del personal.
- Prevención de solapamientos de turnos.
- Manejo de excepciones de base de datos desde Python.

### 5. Marcelo Nahuel Raspo — Agenda y Turnos

**Base de Datos**

- Diseño de la entidad turno.
- Definición de claves foráneas hacia mascota, peluquero y servicio.
- Restricciones de estados, horarios y disponibilidad temporal.

**Programación I**

- Desarrollo de las pantallas de listado, alta y edición de turnos.
- Bloqueo del horario del peluquero según la duración del servicio.
- Integración de la agenda con los demás módulos.

### 6. Federico Montoro — Pagos, Panel General y Métricas

**Base de Datos**

- Diseño de la tabla pago y su relación 1:1 con turno.
- Restricciones para montos y métodos de pago válidos.
- Consolidación del script DDL y preparación del respaldo de la base de datos.

**Programación I**

- Desarrollo del panel principal con contadores y métricas dinámicas.
- Visualización de turnos del día, clientes y mascotas registradas.
- Integración final y pruebas del sistema completo.

## Tareas transversales

Las tareas comunes también se distribuyen entre los seis integrantes:

- **Consultas SQL avanzadas:** elaboración en parejas de las cinco consultas obligatorias, incluyendo JOIN y agregaciones mediante COUNT y SUM.
- **Documentación y bitácora:** cada integrante redacta la sección correspondiente al módulo que diseñó y programó.
- **Pruebas e integración:** cada módulo debe incluir evidencia de validación antes de integrarse a main.
- **Trazabilidad:** los aportes se registran mediante ramas, commits y Pull Requests identificables por integrante.

## Próximas etapas

- [ ] Conectar la aplicación con PostgreSQL.
- [ ] Crear una capa independiente de acceso a datos.
- [ ] Reemplazar los datos en memoria por información persistente.
- [ ] Incorporar las interfaces de servicios y personal.
- [ ] Evitar la superposición de turnos considerando la duración del servicio.
- [ ] Incorporar usuarios y permisos según el rol.
- [ ] Añadir las cinco consultas SQL avanzadas obligatorias.
- [x] Incorporar pruebas unitarias para pagos, métricas y backup.
- [ ] Agregar capturas de pantalla y documentación técnica.
- [ ] Preparar una versión distribuible de la aplicación.

## Recursos del proyecto

- [Repositorio en GitHub](https://github.com/EmilioG03/PELUCAN)
- [Prototipo de interfaz en Figma](https://www.figma.com/design/cHTpfQIOm9YoNabzMTpq53/Untitled?node-id=0-1&t=onKsCF2z3NQCWufN-1)
- [Modelo entidad–relación](https://drive.google.com/file/d/12lx95Q8Cd3X3ZS0SgkKPdsak2LiHMLwc/view?usp=sharing)

## Trabajo colaborativo

Cada cambio debe realizarse en una rama propia:

~~~bash
git switch -c nombre/tarea
git add .
git commit -m "tipo: descripción breve del cambio"
git push -u origin nombre/tarea
~~~

Luego se crea un **Pull Request** hacia main para revisar e integrar el trabajo.

Prefijos sugeridos para los commits:

- **feat:** nueva funcionalidad.
- **fix:** corrección de un error.
- **refactor:** reorganización del código sin cambiar su comportamiento.
- **docs:** documentación.
- **test:** incorporación o modificación de pruebas.
- **chore:** mantenimiento general del proyecto.

---

<p align="center">
  Desarrollado colaborativamente por el equipo Ctrl+E de la Comisión A · 2026
</p>
