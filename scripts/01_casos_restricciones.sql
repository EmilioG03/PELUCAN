-- =====================================================================
-- PELUCAN - Validación de restricciones y reglas de negocio
-- Script 01: casos de prueba sobre el esquema (pelucan_ddl.sql)
-- Responsable: Emmanuel Gillio (Validación y Reglas de Negocio)
-- Motor: PostgreSQL 14 o superior
-- =====================================================================
-- CÓMO USAR
--   1. Tener creada la base con pelucan_ddl.sql.
--   2. Ejecutar este archivo completo (psql: \i 01_casos_restricciones.sql
--      o pgAdmin: abrir en Query Tool y ejecutar con F5).
--      En pgAdmin se muestra el resultado de la ÚLTIMA sentencia. Por eso el
--      archivo termina con el DETALLE; el RESUMEN está al final, comentado,
--      para seleccionarlo y ejecutarlo aparte.
--
-- CÓMO FUNCIONA
--   * Cada caso es una sentencia SQL que se ejecuta dentro de un
--     subbloque; si funciona o falla, el efecto se deshace.
--   * Los datos de apoyo (fixtures) se crean al inicio y se deshacen al
--     final: la base queda exactamente como estaba.
--   * No hace falta una transacción externa ni modifica datos existentes.
--
-- COLUMNAS DEL RESULTADO
--   esperado : OK (la sentencia debe funcionar), ERROR (debe ser rechazada)
--              o un SQLSTATE concreto (ej.: 23505 = clave duplicada).
--   obtenido : lo que ocurrió realmente (OK o SQLSTATE).
--   resultado: PASA | FALLA | SIN CONTROL EN BD
--              (SIN CONTROL EN BD = regla que hoy valida solo la aplicación).
--   tipo     : Regla documentada | Robustez | Aplicación
--
-- obtenido 'NO CUMPLE' = una verificación incluida en el caso (por ejemplo un valor por
--   defecto o un permiso consultado en el catálogo) no dio el resultado esperado.
-- SQLSTATE usados:  23502 NOT NULL | 23503 clave foránea | 23505 UNIQUE
--                   23514 CHECK | 22001 texto muy largo | 22003 número fuera
--                   de rango | 23P01 exclusión (solapamiento) | 42501 permiso
-- =====================================================================

DROP TABLE IF EXISTS pg_temp.casos;

CREATE TEMP TABLE casos (
    orden       serial,
    id          text,
    categoria   text,
    tipo        text,
    regla       text,
    descripcion text,
    rol         text,
    sentencia   text,
    esperado    text
);

-- ---------------------------------------------------------------------
-- Motor de ejecución
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION pg_temp.ejecutar_casos()
RETURNS TABLE (
    caso        text,
    categoria   text,
    tipo        text,
    regla       text,
    descripcion text,
    esperado    text,
    obtenido    text,
    resultado   text,
    detalle     text
)
LANGUAGE plpgsql AS $fn$
DECLARE
    fx   jsonb := '{}'::jsonb;
    v    int;
    c    record;
    s    text;
    k    text;
    val  text;
    obt  text;
    det  text;
BEGIN
    BEGIN   -- bloque exterior: lo creado acá se deshace al final
        -- ------------------ datos de apoyo (fixtures) ------------------
        INSERT INTO cliente (nombre, apellido, telefono, correo)
            VALUES ('Val', 'Cliente A', 'VAL-T-0001', 'val.a@validacion.test') RETURNING id_cliente INTO v;
        fx := fx || jsonb_build_object('cliA', v);
        INSERT INTO cliente (nombre, apellido, telefono, correo)
            VALUES ('Val', 'Cliente B', 'VAL-T-0002', NULL) RETURNING id_cliente INTO v;
        fx := fx || jsonb_build_object('cliB', v);
        INSERT INTO cliente (nombre, apellido, telefono, correo)
            VALUES ('Val', 'Cliente C (sin mascotas)', 'VAL-T-0003', NULL) RETURNING id_cliente INTO v;
        fx := fx || jsonb_build_object('cliC', v);

        INSERT INTO mascota (nombre, raza, edad, tamano, id_cliente)
            VALUES ('ValMascotaA', 'Caniche', 3, 'Pequeño', (fx->>'cliA')::int) RETURNING id_mascota INTO v;
        fx := fx || jsonb_build_object('masA', v);
        INSERT INTO mascota (nombre, raza, edad, tamano, id_cliente)
            VALUES ('ValMascotaB', 'Labrador', 5, 'Grande', (fx->>'cliA')::int) RETURNING id_mascota INTO v;
        fx := fx || jsonb_build_object('masB', v);
        INSERT INTO mascota (nombre, raza, edad, tamano, id_cliente)
            VALUES ('ValMascotaC', 'Beagle', 2, 'Mediano', (fx->>'cliB')::int) RETURNING id_mascota INTO v;
        fx := fx || jsonb_build_object('masC', v);

        INSERT INTO peluquero (nombre, apellido, telefono)
            VALUES ('Val', 'Peluquero A', 'VAL-P-0001') RETURNING id_peluquero INTO v;
        fx := fx || jsonb_build_object('pelA', v);
        INSERT INTO peluquero (nombre, apellido, telefono)
            VALUES ('Val', 'Peluquero B', 'VAL-P-0002') RETURNING id_peluquero INTO v;
        fx := fx || jsonb_build_object('pelB', v);

        INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base)
            VALUES ('VAL Servicio 60', 60, 1000.00) RETURNING id_servicio INTO v;
        fx := fx || jsonb_build_object('sv60', v);
        INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base)
            VALUES ('VAL Servicio 15', 15, 500.00) RETURNING id_servicio INTO v;
        fx := fx || jsonb_build_object('sv15', v);
        INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base)
            VALUES ('VAL Servicio 45', 45, 800.00) RETURNING id_servicio INTO v;
        fx := fx || jsonb_build_object('sv45', v);

        -- tBase: pelA 15/01/2030 10:00-11:00 (Pendiente)
        INSERT INTO turno (fecha, hora, estado, id_mascota, id_peluquero, id_servicio)
            VALUES ('2030-01-15', '10:00', 'Pendiente', (fx->>'masA')::int, (fx->>'pelA')::int, (fx->>'sv60')::int)
            RETURNING id_turno INTO v;
        fx := fx || jsonb_build_object('tBase', v);
        -- tCanc: pelB 15/01/2030 15:00-15:15 (Cancelado, mascota masB)
        INSERT INTO turno (fecha, hora, estado, id_mascota, id_peluquero, id_servicio)
            VALUES ('2030-01-15', '15:00', 'Cancelado', (fx->>'masB')::int, (fx->>'pelB')::int, (fx->>'sv15')::int)
            RETURNING id_turno INTO v;
        fx := fx || jsonb_build_object('tCanc', v);
        -- tPago: turno Completado que ya tiene un pago
        INSERT INTO turno (fecha, hora, estado, id_mascota, id_peluquero, id_servicio)
            VALUES ('2030-01-16', '09:00', 'Completado', (fx->>'masC')::int, (fx->>'pelB')::int, (fx->>'sv45')::int)
            RETURNING id_turno INTO v;
        fx := fx || jsonb_build_object('tPago', v);
        INSERT INTO pago (monto, metodo_pago, id_turno)
            VALUES (800.00, 'Efectivo', (fx->>'tPago')::int) RETURNING id_pago INTO v;
        fx := fx || jsonb_build_object('pagoA', v);
        -- tLibre: turno Completado sin pago
        INSERT INTO turno (fecha, hora, estado, id_mascota, id_peluquero, id_servicio)
            VALUES ('2030-01-17', '09:00', 'Completado', (fx->>'masC')::int, (fx->>'pelB')::int, (fx->>'sv15')::int)
            RETURNING id_turno INTO v;
        fx := fx || jsonb_build_object('tLibre', v);
        -- tMov: turno de pelA a las 13:00, para probar modificaciones
        INSERT INTO turno (fecha, hora, estado, id_mascota, id_peluquero, id_servicio)
            VALUES ('2030-01-15', '13:00', 'Pendiente', (fx->>'masC')::int, (fx->>'pelA')::int, (fx->>'sv15')::int)
            RETURNING id_turno INTO v;
        fx := fx || jsonb_build_object('tMov', v);

        -- ------------------------- casos -------------------------------
        FOR c IN SELECT * FROM pg_temp.casos ORDER BY orden LOOP
            s := c.sentencia;
            FOR k, val IN SELECT key, value FROM jsonb_each_text(fx) LOOP
                s := replace(s, '{' || k || '}', val);
            END LOOP;
            obt := 'OK';
            det := NULL;
            BEGIN
                IF c.rol IS NOT NULL THEN
                    EXECUTE format('SET LOCAL ROLE %I', c.rol);
                END IF;
                EXECUTE s;
                RAISE EXCEPTION 'fin del caso' USING ERRCODE = 'PR000';
            EXCEPTION WHEN OTHERS THEN
                IF SQLSTATE = 'PR000' THEN
                    obt := 'OK';
                ELSIF SQLSTATE = '22012' THEN        -- una verificación (1/0) no se cumplió
                    obt := 'NO CUMPLE';
                    det := 'La condición verificada por el caso no se cumple';
                ELSE
                    obt := SQLSTATE;
                    det := left(SQLERRM, 110);
                END IF;
            END;

            caso := c.id;  categoria := c.categoria;  tipo := c.tipo;
            regla := c.regla;  descripcion := c.descripcion;
            esperado := c.esperado;  obtenido := obt;  detalle := det;
            resultado := CASE
                WHEN (c.esperado = 'OK' AND obt = 'OK')
                  OR (c.esperado = 'ERROR' AND obt <> 'OK')
                  OR (c.esperado = obt)                         THEN 'PASA'
                WHEN c.tipo = 'Aplicación'                      THEN 'SIN CONTROL EN BD'
                ELSE 'FALLA'
            END;
            RETURN NEXT;
        END LOOP;

        RAISE EXCEPTION 'fin de las pruebas' USING ERRCODE = 'PR001';
    EXCEPTION WHEN SQLSTATE 'PR001' THEN
        NULL;   -- se deshacen los datos de apoyo
    END;
END
$fn$;

-- ---------------------------------------------------------------------
-- CASOS
-- columnas: id, categoria, tipo, regla (nº en el informe), descripcion,
--           rol (NULL = usuario actual), sentencia, esperado
-- ---------------------------------------------------------------------
INSERT INTO casos (id, categoria, tipo, regla, descripcion, rol, sentencia, esperado) VALUES
-- ======================= CLIENTES (reglas 2 y 3) =======================
('CLI-01','Clientes','Regla documentada','R2','Alta válida de un cliente',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono,correo) VALUES ('Nuevo','Cliente','VAL-N-0001','nuevo@validacion.test')$q$,'OK'),
('CLI-02','Clientes','Regla documentada','R2','Cliente sin nombre',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES (NULL,'Cliente','VAL-N-0002')$q$,'23502'),
('CLI-03','Clientes','Regla documentada','R2','Cliente sin apellido',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES ('Nuevo',NULL,'VAL-N-0003')$q$,'23502'),
('CLI-04','Clientes','Regla documentada','R2','Cliente sin teléfono',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES ('Nuevo','Cliente',NULL)$q$,'23502'),
('CLI-05','Clientes','Regla documentada','R3','Teléfono duplicado',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES ('Otro','Cliente','VAL-T-0001')$q$,'23505'),
('CLI-06','Clientes','Regla documentada','R3','Correo duplicado',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono,correo) VALUES ('Otro','Cliente','VAL-N-0006','val.a@validacion.test')$q$,'23505'),
('CLI-07','Clientes','Regla documentada','R3','Dos clientes sin correo (el correo es opcional y NULL no colisiona)',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono,correo) VALUES ('Sin','Correo1','VAL-N-0007',NULL),('Sin','Correo2','VAL-N-0008',NULL)$q$,'OK'),
('CLI-08','Clientes','Regla documentada','R2','Nombre de 61 caracteres (máximo 60)',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES (repeat('x',61),'Cliente','VAL-N-0009')$q$,'22001'),
('CLI-09','Clientes','Robustez','R2','Nombre como cadena vacía (NOT NULL no lo detecta)',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES ('','Cliente','VAL-N-0010')$q$,'23514'),
('CLI-10','Clientes','Robustez','R2','Apellido solo con espacios',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES ('Nuevo','   ','VAL-N-0011')$q$,'23514'),
('CLI-11','Clientes','Robustez','R2','Teléfono como cadena vacía',NULL,
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES ('Nuevo','Cliente','')$q$,'23514'),

-- ======================= MASCOTAS (reglas 1, 4 y 5) =====================
('MAS-01','Mascotas','Regla documentada','R1','Alta válida de una mascota',NULL,
 $q$INSERT INTO mascota (nombre,raza,edad,tamano,id_cliente) VALUES ('Rex',NULL,2,'Pequeño',{cliA})$q$,'OK'),
('MAS-02','Mascotas','Regla documentada','R5','Edad negativa',NULL,
 $q$INSERT INTO mascota (nombre,edad,id_cliente) VALUES ('Rex',-1,{cliA})$q$,'23514'),
('MAS-03','Mascotas','Regla documentada','R5','Edad 0 (cachorro)',NULL,
 $q$INSERT INTO mascota (nombre,edad,id_cliente) VALUES ('Rex',0,{cliA})$q$,'OK'),
('MAS-04','Mascotas','Regla documentada','R5','Edad no informada (NULL)',NULL,
 $q$INSERT INTO mascota (nombre,edad,id_cliente) VALUES ('Rex',NULL,{cliA})$q$,'OK'),
('MAS-05','Mascotas','Regla documentada','R5','Tamaño fuera de la lista (Gigante)',NULL,
 $q$INSERT INTO mascota (nombre,tamano,id_cliente) VALUES ('Rex','Gigante',{cliA})$q$,'23514'),
('MAS-06','Mascotas','Regla documentada','R5','Tamaño en minúscula (pequeño)',NULL,
 $q$INSERT INTO mascota (nombre,tamano,id_cliente) VALUES ('Rex','pequeño',{cliA})$q$,'23514'),
('MAS-07','Mascotas','Regla documentada','R5','Tamaño omitido toma el valor por defecto Mediano',NULL,
 $q$WITH i AS (INSERT INTO mascota (nombre,id_cliente) VALUES ('Rex',{cliA}) RETURNING tamano)
    SELECT 1/(CASE WHEN (SELECT tamano FROM i) = 'Mediano' THEN 1 ELSE 0 END)$q$,'OK'),
('MAS-08','Mascotas','Regla documentada','R1','Mascota sin dueño (id_cliente NULL)',NULL,
 $q$INSERT INTO mascota (nombre,id_cliente) VALUES ('Rex',NULL)$q$,'23502'),
('MAS-09','Mascotas','Regla documentada','R1','Mascota con dueño inexistente',NULL,
 $q$INSERT INTO mascota (nombre,id_cliente) VALUES ('Rex',2000000000)$q$,'23503'),
('MAS-10','Mascotas','Regla documentada','R2','Mascota sin nombre',NULL,
 $q$INSERT INTO mascota (nombre,id_cliente) VALUES (NULL,{cliA})$q$,'23502'),
('MAS-11','Mascotas','Regla documentada','R4','Eliminar un cliente que tiene mascotas',NULL,
 $q$DELETE FROM cliente WHERE id_cliente = {cliA}$q$,'23503'),
('MAS-12','Mascotas','Regla documentada','R4','Eliminar un cliente sin mascotas',NULL,
 $q$DELETE FROM cliente WHERE id_cliente = {cliC}$q$,'OK'),
('MAS-13','Mascotas','Regla documentada','R1','ON UPDATE CASCADE: al cambiar el id del cliente sus mascotas lo siguen',NULL,
 $q$UPDATE cliente SET id_cliente = 2000000001 WHERE id_cliente = {cliA};
    SELECT 1/(CASE WHEN (SELECT count(*) FROM mascota WHERE id_cliente = 2000000001) = 2 THEN 1 ELSE 0 END)$q$,'OK'),

-- ==================== SERVICIOS (reglas 6 y 8) =========================
('SER-01','Servicios','Regla documentada','R6','Alta válida de un servicio',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL Nuevo',30,2500.50)$q$,'OK'),
('SER-02','Servicios','Regla documentada','R6','Duración igual a 0',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL Cero',0,100)$q$,'23514'),
('SER-03','Servicios','Regla documentada','R6','Duración negativa',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL Neg',-15,100)$q$,'23514'),
('SER-04','Servicios','Regla documentada','R6','Precio base negativo',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL Precio',30,-1)$q$,'23514'),
('SER-05','Servicios','Regla documentada','R6','Precio base 0 (permitido: cortesía o promoción)',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL Promo',20,0)$q$,'OK'),
('SER-06','Servicios','Regla documentada','R6','Nombre de servicio duplicado',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL Servicio 60',30,100)$q$,'23505'),
('SER-07','Servicios','Regla documentada','R6','Servicio sin nombre',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES (NULL,30,100)$q$,'23502'),
('SER-08','Servicios','Regla documentada','R6','Servicio sin duración',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL SinDur',NULL,100)$q$,'23502'),
('SER-09','Servicios','Regla documentada','R6','Servicio sin precio base',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL SinPrecio',30,NULL)$q$,'23502'),
('SER-10','Servicios','Regla documentada','R6','Precio fuera de rango de numeric(10,2)',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL Enorme',30,100000000.00)$q$,'22003'),
('SER-11','Servicios','Regla documentada','R8','Eliminar un servicio que tiene turnos',NULL,
 $q$DELETE FROM servicio WHERE id_servicio = {sv60}$q$,'23503'),
('SER-12','Servicios','Robustez','R6','Nombre duplicado con otras mayúsculas y espacios ("val servicio 60 ")',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('val servicio 60 ',30,100)$q$,'23505'),
('SER-13','Servicios','Robustez','R6','Nombre de servicio como cadena vacía',NULL,
 $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('',30,100)$q$,'23514'),

-- ==================== PELUQUEROS (reglas 7 y 8) ========================
('PEL-01','Peluqueros','Regla documentada','R7','Alta válida sin especialidad (es opcional)',NULL,
 $q$INSERT INTO peluquero (nombre,apellido,telefono) VALUES ('Nuevo','Peluquero','VAL-P-0100')$q$,'OK'),
('PEL-02','Peluqueros','Regla documentada','R7','Peluquero sin nombre',NULL,
 $q$INSERT INTO peluquero (nombre,apellido,telefono) VALUES (NULL,'Peluquero','VAL-P-0101')$q$,'23502'),
('PEL-03','Peluqueros','Regla documentada','R7','Peluquero sin apellido',NULL,
 $q$INSERT INTO peluquero (nombre,apellido,telefono) VALUES ('Nuevo',NULL,'VAL-P-0102')$q$,'23502'),
('PEL-04','Peluqueros','Regla documentada','R7','Peluquero sin teléfono',NULL,
 $q$INSERT INTO peluquero (nombre,apellido,telefono) VALUES ('Nuevo','Peluquero',NULL)$q$,'23502'),
('PEL-05','Peluqueros','Regla documentada','R8','Eliminar un peluquero que tiene turnos',NULL,
 $q$DELETE FROM peluquero WHERE id_peluquero = {pelA}$q$,'23503'),
('PEL-06','Peluqueros','Robustez','R7','Nombre de peluquero como cadena vacía',NULL,
 $q$INSERT INTO peluquero (nombre,apellido,telefono) VALUES ('','Peluquero','VAL-P-0103')$q$,'23514'),

-- ============ TURNOS: integridad y estados (reglas 9 y 15) =============
('TUR-01','Turnos','Regla documentada','R9','Alta válida de un turno',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00',{masC},{pelA},{sv15})$q$,'OK'),
('TUR-02','Turnos','Regla documentada','R9','Turno sin mascota',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00',NULL,{pelA},{sv15})$q$,'23502'),
('TUR-03','Turnos','Regla documentada','R9','Turno sin peluquero',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00',{masC},NULL,{sv15})$q$,'23502'),
('TUR-04','Turnos','Regla documentada','R9','Turno sin servicio',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00',{masC},{pelA},NULL)$q$,'23502'),
('TUR-05','Turnos','Regla documentada','R9','Turno sin fecha',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES (NULL,'09:00',{masC},{pelA},{sv15})$q$,'23502'),
('TUR-06','Turnos','Regla documentada','R9','Turno sin hora',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01',NULL,{masC},{pelA},{sv15})$q$,'23502'),
('TUR-07','Turnos','Regla documentada','R9','Turno con mascota inexistente',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00',2000000000,{pelA},{sv15})$q$,'23503'),
('TUR-08','Turnos','Regla documentada','R9','Turno con peluquero inexistente',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00',{masC},2000000000,{sv15})$q$,'23503'),
('TUR-09','Turnos','Regla documentada','R9','Turno con servicio inexistente',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00',{masC},{pelA},2000000000)$q$,'23503'),
('TUR-10','Turnos','Regla documentada','R15','Estado fuera de la lista (Reprogramado)',NULL,
 $q$INSERT INTO turno (fecha,hora,estado,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00','Reprogramado',{masC},{pelA},{sv15})$q$,'23514'),
('TUR-11','Turnos','Regla documentada','R15','Estado en minúscula (pendiente)',NULL,
 $q$INSERT INTO turno (fecha,hora,estado,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00','pendiente',{masC},{pelA},{sv15})$q$,'23514'),
('TUR-12','Turnos','Regla documentada','R15','Estado omitido toma el valor por defecto Pendiente',NULL,
 $q$WITH i AS (INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-02-01','09:00',{masC},{pelA},{sv15}) RETURNING estado)
    SELECT 1/(CASE WHEN (SELECT estado FROM i) = 'Pendiente' THEN 1 ELSE 0 END)$q$,'OK'),

-- ============ TURNOS: agenda y solapamientos (reglas 10 a 13) ==========
-- Referencia: tBase = peluquero A, 15/01/2030 de 10:00 a 11:00 (servicio de 60 min)
('AGE-01','Agenda','Regla documentada','R11','Mismo peluquero, misma fecha y hora, otra mascota',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','10:00',{masC},{pelA},{sv15})$q$,'23505'),
('AGE-02','Agenda','Regla documentada','R10','Misma mascota, misma fecha y hora, otro peluquero',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','10:00',{masA},{pelB},{sv15})$q$,'23505'),
('AGE-03','Agenda','Regla documentada','R11','Mismo horario con otra mascota y otro peluquero (permitido)',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','10:00',{masC},{pelB},{sv15})$q$,'OK'),
('AGE-04','Agenda','Regla documentada','R12','Turno que empieza justo cuando termina el anterior (11:00; no es solapamiento)',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','11:00',{masC},{pelA},{sv15})$q$,'OK'),
('AGE-05','Agenda','Regla documentada','R12','Solapamiento parcial: nuevo a las 10:30, existente de 10:00 a 11:00',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','10:30',{masC},{pelA},{sv15})$q$,'ERROR'),
('AGE-06','Agenda','Regla documentada','R12','Solapamiento: nuevo de 09:30 a 10:30 pisa el comienzo del existente',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','09:30',{masC},{pelA},{sv60})$q$,'ERROR'),
('AGE-07','Agenda','Regla documentada','R12','Solapamiento: nuevo de 10:15 a 10:30 queda dentro del existente',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','10:15',{masC},{pelA},{sv15})$q$,'ERROR'),
('AGE-08','Agenda','Regla documentada','R12','Solapamiento al reprogramar: mover el turno de las 13:00 a las 10:30',NULL,
 $q$UPDATE turno SET hora = '10:30' WHERE id_turno = {tMov}$q$,'ERROR'),
('AGE-09','Agenda','Regla documentada','R11','Reprogramar un turno exactamente al horario de otro del mismo peluquero',NULL,
 $q$UPDATE turno SET hora = '10:00' WHERE id_turno = {tMov}$q$,'23505'),
('AGE-10','Agenda','Regla documentada','R12','Solapar con un turno Cancelado no bloquea (15:10 vs cancelado de 15:00-15:15)',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','15:10',{masC},{pelB},{sv15})$q$,'OK'),
('AGE-11','Agenda','Robustez','R11','Reutilizar el horario exacto de un turno Cancelado con el mismo peluquero',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','15:00',{masC},{pelB},{sv15})$q$,'OK'),
('AGE-12','Agenda','Robustez','R10','Reutilizar el horario exacto de un turno Cancelado con la misma mascota',NULL,
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-01-15','15:00',{masB},{pelA},{sv15})$q$,'OK'),
('AGE-13','Agenda','Aplicación','R14','Agendar un turno Pendiente con fecha pasada (01/01/2020)',NULL,
 $q$INSERT INTO turno (fecha,hora,estado,id_mascota,id_peluquero,id_servicio) VALUES ('2020-01-01','09:00','Pendiente',{masC},{pelA},{sv15})$q$,'ERROR'),

-- ========================= PAGOS (reglas 16 a 18) ======================
('PAG-01','Pagos','Regla documentada','R16','Alta válida de un pago',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (500.00,'Tarjeta',{tLibre})$q$,'OK'),
('PAG-02','Pagos','Regla documentada','R17','Monto igual a 0',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (0,'Efectivo',{tLibre})$q$,'23514'),
('PAG-03','Pagos','Regla documentada','R17','Monto negativo',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (-100,'Efectivo',{tLibre})$q$,'23514'),
('PAG-04','Pagos','Regla documentada','R17','Método de pago fuera de la lista (Cheque)',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (500,'Cheque',{tLibre})$q$,'23514'),
('PAG-05','Pagos','Regla documentada','R17','Método de pago en minúscula (efectivo)',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (500,'efectivo',{tLibre})$q$,'23514'),
('PAG-06','Pagos','Regla documentada','R16','Segundo pago para el mismo turno (relación 1:1)',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (300,'Efectivo',{tPago})$q$,'23505'),
('PAG-07','Pagos','Regla documentada','R16','Pago sin turno',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (500,'Efectivo',NULL)$q$,'23502'),
('PAG-08','Pagos','Regla documentada','R16','Pago de un turno inexistente',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (500,'Efectivo',2000000000)$q$,'23503'),
('PAG-09','Pagos','Regla documentada','R17','Pago sin monto',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (NULL,'Efectivo',{tLibre})$q$,'23502'),
('PAG-10','Pagos','Regla documentada','R17','Pago sin método',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (500,NULL,{tLibre})$q$,'23502'),
('PAG-11','Pagos','Regla documentada','R17','Monto fuera de rango de numeric(10,2)',NULL,
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (100000000.00,'Efectivo',{tLibre})$q$,'22003'),
('PAG-12','Pagos','Regla documentada','R17','La fecha del pago se registra automáticamente (valor actual)',NULL,
 $q$WITH i AS (INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (500,'Tarjeta',{tLibre}) RETURNING fecha_pago)
    SELECT 1/(CASE WHEN (SELECT abs(extract(epoch FROM now() - fecha_pago)) FROM i) < 5 THEN 1 ELSE 0 END)$q$,'OK'),
('PAG-13','Pagos','Regla documentada','R18','Eliminar un turno que tiene pago asociado',NULL,
 $q$DELETE FROM turno WHERE id_turno = {tPago}$q$,'23503');

-- ---------------------------------------------------------------------
-- DETALLE (última sentencia: es la que muestra pgAdmin)
-- ---------------------------------------------------------------------
-- RESUMEN (seleccionar solo esta sentencia y ejecutar):
-- SELECT tipo, resultado, count(*) AS casos
--   FROM pg_temp.ejecutar_casos() GROUP BY tipo, resultado ORDER BY tipo, resultado;

SELECT * FROM pg_temp.ejecutar_casos();
