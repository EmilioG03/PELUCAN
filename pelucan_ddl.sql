CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    telefono VARCHAR(20) NOT NULL UNIQUE,
    correo VARCHAR(100) UNIQUE
);

CREATE TABLE mascota (
    id_mascota SERIAL PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    raza VARCHAR(60),
    edad SMALLINT CHECK (edad >= 0),
    tamano VARCHAR(10) NOT NULL DEFAULT 'Mediano',
    observaciones TEXT,
    id_cliente INTEGER NOT NULL,

    CONSTRAINT chk_tamano
        CHECK (tamano IN ('Pequeño', 'Mediano', 'Grande')),

    CONSTRAINT fk_mascota_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE peluquero (
    id_peluquero SERIAL PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    especialidad VARCHAR(50)
);

CREATE TABLE servicio (
    id_servicio SERIAL PRIMARY KEY,
    nombre_servicio VARCHAR(80) NOT NULL UNIQUE,
    duracion_estimada INTEGER NOT NULL CHECK (duracion_estimada > 0),
    precio_base NUMERIC(10,2) NOT NULL CHECK (precio_base >= 0)
);

CREATE TABLE turno (
    id_turno SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    observaciones TEXT,
    id_mascota INTEGER NOT NULL,
    id_peluquero INTEGER NOT NULL,
    id_servicio INTEGER NOT NULL,

    CONSTRAINT chk_estado_turno
        CHECK (
            estado IN (
                'Pendiente',
                'Confirmado',
                'Completado',
                'Cancelado'
            )
        ),

    CONSTRAINT fk_turno_mascota
        FOREIGN KEY (id_mascota)
        REFERENCES mascota(id_mascota)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_turno_peluquero
        FOREIGN KEY (id_peluquero)
        REFERENCES peluquero(id_peluquero)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_turno_servicio
        FOREIGN KEY (id_servicio)
        REFERENCES servicio(id_servicio)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT uq_mascota_fecha_hora
        UNIQUE (id_mascota, fecha, hora),

    CONSTRAINT uq_peluquero_fecha_hora
        UNIQUE (id_peluquero, fecha, hora)
);
