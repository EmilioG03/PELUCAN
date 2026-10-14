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
CREATE TABLE pago (
    id_pago SERIAL PRIMARY KEY,
    monto NUMERIC(10,2) NOT NULL CHECK (monto > 0),
    fecha_pago TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metodo_pago VARCHAR(30) NOT NULL,
    id_turno INTEGER NOT NULL UNIQUE,

    CONSTRAINT chk_metodo_pago
        CHECK (metodo_pago IN ('Efectivo', 'Transferencia', 'Tarjeta')),

    CONSTRAINT fk_pago_turno
        FOREIGN KEY (id_turno)
        REFERENCES turno(id_turno)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

INSERT INTO cliente (nombre, apellido, telefono, correo) VALUES
('Carlos', 'Gómez', '351-555-0110', 'carlos.gomez@mail.com'),
('Ana', 'Ferreyra', '351-555-0142', 'ana.ferreyra@mail.com'),
('Marcos', 'Díaz', '351-555-0198', 'marcos.diaz@mail.com'),
('Lucía', 'Vera', '351-555-0121', 'lucia.vera@mail.com'),
('Sofía', 'Martínez', '351-555-0155', 'sofia.m@mail.com');

INSERT INTO peluquero (nombre, apellido, telefono, especialidad) VALUES
('María', 'Rodríguez', '351-444-1122', 'Cortes complejos y razas grandes'),
('Juan', 'Pérez', '351-444-3344', 'Tratamientos de piel sensible y gatos'),
('Camila', 'Acosta', '351-444-5566', 'Cachorros y cortes de raza');

INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base) VALUES
('Baño completo', 45, 12000.00),
('Corte + Baño', 60, 18000.00),
('Corte de uñas', 15, 4000.00),
('Desparasitado', 20, 7000.00),
('Baño + Deslanado', 75, 22000.00);

INSERT INTO mascota (nombre, raza, edad, tamano, observaciones, id_cliente) VALUES
('Luna', 'Caniche', 3, 'Pequeño', 'Ninguna', 1),
('Bruno', 'Labrador', 5, 'Grande', 'Piel sensible', 2),
('Toby', 'Cocker', 2, 'Mediano', 'Enojo fácil', 3),
('Coco', 'Golden', 1, 'Grande', 'Secador lento', 4),
('Lola', 'Beagle', 4, 'Mediano', 'Muy inquieta', 5),
('Simba', 'Persa', 3, 'Pequeño', 'Requiere bozal gato', 1),
('Bella', 'Maltés', 2, 'Pequeño', 'Nudos en orejas', 2);


