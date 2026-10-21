INSERT INTO cliente (nombre, apellido, telefono, correo) VALUES
('Carlos', 'Gómez', '3515550110', 'carlos.gomez@mail.com'),
('Ana', 'Ferreyra', '3515550142', 'ana.ferreyra@mail.com'),
('Marcos', 'Díaz', '3515550198', 'marcos.diaz@mail.com'),
('Lucía', 'Vera', '3515550121', 'lucia.vera@mail.com');

insert into mascota ( nombre, raza, edad, tamaño, observaciones, id_cliente) values 
(" luna", "caniche", 3, "pequeño", "ninguna", 1)
("bruno", "labrador", 5, "grande", "piel sensible", 2)
("molly", "beagle", 2, "mediano", "suele asustarse con el secador", 2)
("toby", "cocker", 2, "mediano", "enojo facil al cortarse las uñas", 3)
("kira", "golden", 1, "grande", "secador lento", 4)
(" lola", "caniche", 4, "pequeño", "ninguna", 4)

insert into servicio ( nombre_servicio, duracion_estimada, precio_base) values
("baño completo", 45, 12000.00),
("corte + baño", 60, 18000.00),
("corte de uñas", 15, 5000.00),
("desparasitado", 20, 8000.00);

insert into ( peluquero (nombre, apellido, telefeno, especialidad) values
("Maria", "Rodriguez", "3572467322", "corte de tijera"),
("javier", "lopez", "3456767898", "deslanado y baños");

insert into turno( fecha, hora, estado, observaciones, id_mascotas, id_peluquero, id_servicio) values
("2026-09-24", "9:00:00", "pendiente", "corte higenico estandar", 1, 1, 1),
("2026-08-31", "10:30:00", "confirmado", "piel sensible", 2,2,2),
("2026-08-29", "11:45:00", "confirmado", "cuidado de uñas", 4, 1, 3),
("2026-07-12", "14:30:00", "confirmado", "bañado y secado lento", 5, 2, 1),
("2026-02-18", "08:20:00", "pendiente", "aplicacion de pipeta", 5,1,4),
("2026-07-25", "12:00:00", "confirmado", "atencion especial al peinar", 3,2,1);

insert into pago (monto, fecha_pago, metodo_pago, id_turno) vaalues
(8000.00, "14:30:00", "efectivo" , 4),
(18000.00, "12:00:00", "transferencia", 6);
