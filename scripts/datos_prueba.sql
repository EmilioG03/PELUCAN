INSERT INTO cliente (nombre, apellido, telefono, correo) VALUES
('Valentina', 'Gómez', '351-600-1001', 'valentina.gomez@mail.com'),
('Martín', 'Ruiz', '351-600-1002', 'martin.ruiz@mail.com'),
('Sofía', 'Torres', '351-600-1003', 'sofia.torres@mail.com'),
('Diego', 'Herrera', '351-600-1004', 'diego.herrera@mail.com'),
('Lucía', 'Fernández', '351-600-1005', 'lucia.fernandez@mail.com');



INSERT INTO mascota (nombre, raza, edad, tamano, observaciones, id_cliente) VALUES
('Mora', 'Border Collie', 4, 'Mediano', 'Mascota tranquila', 6),
('Rocky', 'Boxer', 6, 'Grande', 'Sensible al ruido del secador', 7),
('Frida', 'Schnauzer', 3, 'Pequeño', 'Requiere cepillado cuidadoso', 8);



INSERT INTO peluquero (nombre, apellido, telefono, especialidad) VALUES
('Lucas', 'Benítez', '351-610-2001', 'Baño y secado'),
('Ana', 'Suárez', '351-610-2002', 'Cortes'),
('Diego', 'Molina', '351-610-2003', 'Cepillado'),
('Carolina', 'Vega', '351-610-2004', 'Deslanado'),
('Federico', 'Ríos', '351-610-2005', 'Corte de uñas'),
('Paula', 'Navarro', '351-610-2006', 'Baño sanitario'),
('Nicolás', 'Castro', '351-610-2007', 'Corte y baño');



INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base) VALUES
('Limpieza de oídos', 10, 3500.00),
('Corte higiénico', 30, 9000.00),
('Cepillado profundo', 40, 11000.00),
('Baño sanitario', 50, 14000.00),
('Limpieza de pliegues', 25, 6500.00);



INSERT INTO turno (fecha, hora, estado, observaciones, id_mascota, id_peluquero, id_servicio) VALUES
('2026-10-30', '12:30:00', 'Pendiente', 'Baño general', 6, 3, 1),
('2026-10-30', '13:30:00', 'Confirmado', 'Deslanado completo', 7, 3, 5),
('2026-11-02', '09:00:00', 'Confirmado', 'Primera visita', 8, 4, 6),
('2026-11-02', '10:00:00', 'Pendiente', 'Solicita corte corto', 9, 5, 7),
('2026-11-02', '11:30:00', 'Completado', 'Atención realizada sin inconvenientes', 10, 6, 8);



INSERT INTO pago (monto, fecha_pago, metodo_pago, id_turno) VALUES
(4000.00, '2026-08-31 12:10:00', 'Tarjeta', 3),
(12000.00, '2026-08-31 15:00:00', 'Efectivo', 4),
(12000.00, '2026-10-30 13:20:00', 'Transferencia', 6),
(22000.00, '2026-10-30 15:00:00', 'Tarjeta', 7),
(3500.00, '2026-11-02 09:30:00', 'Efectivo', 8),
(9000.00, '2026-11-02 10:45:00', 'Transferencia', 9),
(11000.00, '2026-11-02 12:30:00', 'Tarjeta', 10);