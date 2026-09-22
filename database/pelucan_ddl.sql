-- TABLA CLIENTE

CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL UNIQUE,
    telefono VARCHAR(20) UNIQUE,
    correo VARCHAR(100) UNIQUE
);


-- TABLA MASCOTA

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
);


-- TABLA EMPLEADO

CREATE TABLE empleado (
    id_empleado SERIAL PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    puesto VARCHAR(20) NOT NULL,

    CONSTRAINT chk_puesto
        CHECK (
            puesto IN (
                'Veterinario',
                'Peluquero',
                'Administrativo'
            )
        )
);


-- TABLA SERVICIO

CREATE TABLE servicio (
    id_servicio SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    descripcion VARCHAR(200),
    precio NUMERIC(10,2) NOT NULL,
    duracion SMALLINT NOT NULL,

    CONSTRAINT chk_precio
        CHECK (precio >= 0),

    CONSTRAINT chk_duracion
        CHECK (duracion > 0)
);


-- TABLA TURNO

CREATE TABLE turno (
    id_turno SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',

    id_mascota INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
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
        REFERENCES mascota(id_mascota),

    CONSTRAINT fk_turno_empleado
        FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado),

    CONSTRAINT fk_turno_servicio
        FOREIGN KEY (id_servicio)
        REFERENCES servicio(id_servicio)
);


-- TABLA PAGO

CREATE TABLE pago (
    id_pago SERIAL PRIMARY KEY,
    monto NUMERIC(10,2) NOT NULL,
    fecha DATE NOT NULL,
    metodo_pago VARCHAR(20) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    id_turno INTEGER NOT NULL UNIQUE,

    CONSTRAINT chk_metodo_pago
        CHECK (
            metodo_pago IN (
                'Efectivo',
                'Transferencia',
                'Tarjeta'
            )
        ),

    CONSTRAINT chk_estado_pago
        CHECK (
            estado IN (
                'Pendiente',
                'Realizado'
            )
        ),

    CONSTRAINT fk_pago_turno
        FOREIGN KEY (id_turno)
        REFERENCES turno(id_turno)
        ON DELETE CASCADE
);