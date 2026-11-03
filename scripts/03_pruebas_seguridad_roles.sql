-- =====================================================================
-- PELUCAN - Validación de seguridad: roles y permisos del SGBD
-- Script 03: matriz de privilegios + intentos no autorizados
-- Responsable: Emmanuel Gillio (Validación y Reglas de Negocio)
-- Motor: PostgreSQL 14 o superior. Ejecutar con un usuario administrador (postgres).
-- =====================================================================
-- PRERREQUISITO
--   Que existan los roles. Hasta que Acceso a Datos entregue su script de
--   roles y permisos, se puede usar 00_roles_provisorios.sql. Cuando esté el
--   real, se ejecuta ese y se vuelve a correr ESTE archivo sin modificarlo.
--
-- QUÉ VERIFICA
--   1. Matriz de privilegios: para cada rol, tabla y privilegio compara lo
--      que DEBERÍA poder hacer (según el informe) con lo que PUEDE hacer.
--   2. Operaciones permitidas: el recepcionista trabaja con los datos.
--   3. Intentos no autorizados: el recepcionista intenta tocar el esquema,
--      las restricciones, las credenciales y escalar privilegios. Todos
--      deben ser rechazados con 42501 (permiso denegado).
--   4. El administrador_bd puede mantener el esquema y no es superusuario.
--   Cada intento se ejecuta en un subbloque y se deshace: la base no cambia.
--
-- PARÁMETROS (ajustar si el equipo decide otra matriz de permisos)
--   catalogos = true  -> el recepcionista también administra servicios y
--                        peluqueros (así lo dice la tabla "Usuarios y
--                        Permisos" del informe).
--   catalogos = false -> solo puede consultarlos (como lista la división de
--                        tareas: CRUD de clientes, mascotas, turnos y pagos).
-- =====================================================================

DROP TABLE IF EXISTS pg_temp.param;
CREATE TEMP TABLE param AS SELECT true AS catalogos;      -- <== AJUSTAR ACÁ

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
-- Motor de ejecución (igual al del script 01, con menos datos de apoyo)
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
    BEGIN
        INSERT INTO cliente (nombre, apellido, telefono)
            VALUES ('Val', 'Cliente A', 'VAL-T-0001') RETURNING id_cliente INTO v;
        fx := fx || jsonb_build_object('cliA', v);
        INSERT INTO mascota (nombre, id_cliente)
            VALUES ('ValMascotaA', (fx->>'cliA')::int) RETURNING id_mascota INTO v;
        fx := fx || jsonb_build_object('masA', v);
        INSERT INTO peluquero (nombre, apellido, telefono)
            VALUES ('Val', 'Peluquero A', 'VAL-P-0001') RETURNING id_peluquero INTO v;
        fx := fx || jsonb_build_object('pelA', v);
        INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base)
            VALUES ('VAL Servicio 60', 60, 1000.00) RETURNING id_servicio INTO v;
        fx := fx || jsonb_build_object('sv60', v);
        INSERT INTO turno (fecha, hora, estado, id_mascota, id_peluquero, id_servicio)
            VALUES ('2030-01-15', '10:00', 'Completado', (fx->>'masA')::int, (fx->>'pelA')::int, (fx->>'sv60')::int)
            RETURNING id_turno INTO v;
        fx := fx || jsonb_build_object('tBase', v);
        INSERT INTO turno (fecha, hora, estado, id_mascota, id_peluquero, id_servicio)
            VALUES ('2030-01-16', '10:00', 'Completado', (fx->>'masA')::int, (fx->>'pelA')::int, (fx->>'sv60')::int)
            RETURNING id_turno INTO v;
        fx := fx || jsonb_build_object('tLibre', v);
        INSERT INTO pago (monto, metodo_pago, id_turno)
            VALUES (1000.00, 'Efectivo', (fx->>'tBase')::int) RETURNING id_pago INTO v;
        fx := fx || jsonb_build_object('pagoA', v);

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
        NULL;
    END;
END
$fn$;

-- ---------------------------------------------------------------------
-- 0. Los roles existen y no son superusuarios
-- ---------------------------------------------------------------------
INSERT INTO casos (id, categoria, tipo, regla, descripcion, rol, sentencia, esperado) VALUES
('ROL-01','Roles','Regla documentada','Perfiles','Existe el rol recepcionista',NULL,
 $q$SELECT 1/(CASE WHEN EXISTS (SELECT 1 FROM pg_roles WHERE rolname='recepcionista') THEN 1 ELSE 0 END)$q$,'OK'),
('ROL-02','Roles','Regla documentada','Perfiles','Existe el rol administrador_bd',NULL,
 $q$SELECT 1/(CASE WHEN EXISTS (SELECT 1 FROM pg_roles WHERE rolname='administrador_bd') THEN 1 ELSE 0 END)$q$,'OK'),
('ROL-03','Roles','Regla documentada','Perfiles','recepcionista no es superusuario ni puede crear roles ni bases',NULL,
 $q$SELECT 1/(CASE WHEN EXISTS (SELECT 1 FROM pg_roles WHERE rolname='recepcionista'
                                  AND NOT rolsuper AND NOT rolcreaterole AND NOT rolcreatedb) THEN 1 ELSE 0 END)$q$,'OK'),
('ROL-04','Roles','Regla documentada','Perfiles','administrador_bd no es superusuario',NULL,
 $q$SELECT 1/(CASE WHEN EXISTS (SELECT 1 FROM pg_roles WHERE rolname='administrador_bd' AND NOT rolsuper) THEN 1 ELSE 0 END)$q$,'OK'),
('ROL-05','Roles','Regla documentada','Perfiles','PUBLIC no tiene permisos sobre las tablas del esquema public',NULL,
 $q$SELECT 1/(CASE WHEN NOT EXISTS (SELECT 1 FROM information_schema.role_table_grants
                                     WHERE grantee='PUBLIC' AND table_schema='public') THEN 1 ELSE 0 END)$q$,'OK');

-- ---------------------------------------------------------------------
-- 1. Matriz de privilegios (esperado vs real, por catálogo del sistema)
-- ---------------------------------------------------------------------
INSERT INTO casos (id, categoria, tipo, regla, descripcion, rol, sentencia, esperado)
SELECT
    'MAT-' || lpad(row_number() OVER (ORDER BY r.rol DESC, t.tabla, p.priv)::text, 3, '0'),
    'Matriz de privilegios',
    'Regla documentada',
    'Perfiles',
    r.rol || ' ' || CASE WHEN esperado THEN 'PUEDE' ELSE 'NO PUEDE' END || ' ' || p.priv || ' sobre ' || t.tabla,
    NULL,
    format($f$SELECT 1/(CASE WHEN %s has_table_privilege(%L, %L, %L) THEN 1 ELSE 0 END)$f$,
           CASE WHEN esperado THEN '' ELSE 'NOT' END, r.rol, 'public.' || t.tabla, p.priv),
    'OK'
FROM (VALUES ('recepcionista'), ('administrador_bd')) AS r(rol)
CROSS JOIN (VALUES ('cliente'), ('mascota'), ('turno'), ('pago'), ('servicio'), ('peluquero')) AS t(tabla)
CROSS JOIN (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE'), ('REFERENCES'), ('TRIGGER')) AS p(priv)
CROSS JOIN LATERAL (
    SELECT CASE
        WHEN r.rol = 'administrador_bd'                          THEN true
        WHEN p.priv IN ('TRUNCATE', 'REFERENCES', 'TRIGGER')     THEN false
        WHEN t.tabla IN ('servicio', 'peluquero') AND p.priv = 'SELECT' THEN true
        WHEN t.tabla IN ('servicio', 'peluquero')                THEN (SELECT catalogos FROM param)
        ELSE true
    END AS esperado
) AS e;

INSERT INTO casos (id, categoria, tipo, regla, descripcion, rol, sentencia, esperado) VALUES
('MAT-SCH1','Matriz de privilegios','Regla documentada','Perfiles','recepcionista NO PUEDE crear objetos en el esquema public',NULL,
 $q$SELECT 1/(CASE WHEN NOT has_schema_privilege('recepcionista','public','CREATE') THEN 1 ELSE 0 END)$q$,'OK'),
('MAT-SCH2','Matriz de privilegios','Regla documentada','Perfiles','administrador_bd PUEDE crear objetos en el esquema public',NULL,
 $q$SELECT 1/(CASE WHEN has_schema_privilege('administrador_bd','public','CREATE') THEN 1 ELSE 0 END)$q$,'OK'),
('MAT-SEQ1','Matriz de privilegios','Regla documentada','Perfiles','recepcionista PUEDE usar todas las secuencias (necesario para los INSERT con SERIAL)',NULL,
 $q$SELECT 1/(CASE WHEN NOT EXISTS (SELECT 1 FROM pg_sequences s
                                      WHERE s.schemaname = 'public'
                                        AND NOT has_sequence_privilege('recepcionista',
                                                format('%I.%I', s.schemaname, s.sequencename), 'USAGE')) THEN 1 ELSE 0 END)$q$,'OK');

-- ---------------------------------------------------------------------
-- 2. Operaciones permitidas al recepcionista (ejecutadas con SET ROLE)
-- ---------------------------------------------------------------------
INSERT INTO casos (id, categoria, tipo, regla, descripcion, rol, sentencia, esperado) VALUES
('OPE-01','Operaciones permitidas','Regla documentada','Perfiles','recepcionista consulta clientes','recepcionista',
 $q$SELECT * FROM cliente LIMIT 1$q$,'OK'),
('OPE-02','Operaciones permitidas','Regla documentada','Perfiles','recepcionista da de alta un cliente','recepcionista',
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES ('Alta','Recepcion','VAL-R-0001')$q$,'OK'),
('OPE-03','Operaciones permitidas','Regla documentada','Perfiles','recepcionista da de alta una mascota','recepcionista',
 $q$INSERT INTO mascota (nombre,id_cliente) VALUES ('Rex',{cliA})$q$,'OK'),
('OPE-04','Operaciones permitidas','Regla documentada','Perfiles','recepcionista agenda un turno','recepcionista',
 $q$INSERT INTO turno (fecha,hora,id_mascota,id_peluquero,id_servicio) VALUES ('2030-03-01','09:00',{masA},{pelA},{sv60})$q$,'OK'),
('OPE-05','Operaciones permitidas','Regla documentada','Perfiles','recepcionista modifica el estado de un turno','recepcionista',
 $q$UPDATE turno SET estado = 'Cancelado' WHERE id_turno = {tLibre}$q$,'OK'),
('OPE-06','Operaciones permitidas','Regla documentada','Perfiles','recepcionista registra un pago','recepcionista',
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (500,'Tarjeta',{tLibre})$q$,'OK'),
('OPE-07','Operaciones permitidas','Regla documentada','Perfiles','recepcionista da de baja un pago','recepcionista',
 $q$DELETE FROM pago WHERE id_pago = {pagoA}$q$,'OK'),
('OPE-08','Operaciones permitidas','Regla documentada','Perfiles','recepcionista consulta el catálogo de servicios','recepcionista',
 $q$SELECT * FROM servicio$q$,'OK');

INSERT INTO casos (id, categoria, tipo, regla, descripcion, rol, sentencia, esperado)
SELECT 'OPE-09','Operaciones permitidas','Regla documentada','Perfiles',
       'recepcionista modifica el catálogo de servicios (según parámetro "catalogos")','recepcionista',
       $q$INSERT INTO servicio (nombre_servicio,duracion_estimada,precio_base) VALUES ('VAL Nuevo',30,2000)$q$,
       CASE WHEN catalogos THEN 'OK' ELSE '42501' END
FROM param;

-- Las reglas de negocio también rigen para el rol de la aplicación
INSERT INTO casos (id, categoria, tipo, regla, descripcion, rol, sentencia, esperado) VALUES
('OPE-10','Operaciones permitidas','Regla documentada','R3','recepcionista no puede saltarse la regla de teléfono único','recepcionista',
 $q$INSERT INTO cliente (nombre,apellido,telefono) VALUES ('Dup','Dup','VAL-T-0001')$q$,'23505'),
('OPE-11','Operaciones permitidas','Regla documentada','R17','recepcionista no puede registrar un pago con monto 0','recepcionista',
 $q$INSERT INTO pago (monto,metodo_pago,id_turno) VALUES (0,'Efectivo',{tLibre})$q$,'23514');

-- ---------------------------------------------------------------------
-- 3. Intentos no autorizados del recepcionista (todos deben dar 42501)
-- ---------------------------------------------------------------------
INSERT INTO casos (id, categoria, tipo, regla, descripcion, rol, sentencia, esperado) VALUES
('SEG-01','Intentos no autorizados','Regla documentada','Perfiles','Borrar una tabla (DROP TABLE cliente)','recepcionista',
 $q$DROP TABLE cliente CASCADE$q$,'42501'),
('SEG-02','Intentos no autorizados','Regla documentada','Perfiles','Modificar la estructura (ALTER TABLE ... ADD COLUMN)','recepcionista',
 $q$ALTER TABLE cliente ADD COLUMN intruso int$q$,'42501'),
('SEG-03','Intentos no autorizados','Regla documentada','Perfiles','Crear una tabla nueva en el esquema','recepcionista',
 $q$CREATE TABLE intruso (id int)$q$,'42501'),
('SEG-04','Intentos no autorizados','Regla documentada','Perfiles','Vaciar una tabla (TRUNCATE pago)','recepcionista',
 $q$TRUNCATE pago$q$,'42501'),
('SEG-05','Intentos no autorizados','Regla documentada','Perfiles','Eliminar una restricción de integridad (DROP CONSTRAINT)','recepcionista',
 $q$ALTER TABLE turno DROP CONSTRAINT uq_peluquero_fecha_hora$q$,'42501'),
('SEG-06','Intentos no autorizados','Regla documentada','Perfiles','Desactivar los triggers de una tabla','recepcionista',
 $q$ALTER TABLE pago DISABLE TRIGGER ALL$q$,'42501'),
('SEG-07','Intentos no autorizados','Regla documentada','Perfiles','Crear un índice','recepcionista',
 $q$CREATE INDEX ix_intruso ON cliente (nombre)$q$,'42501'),
('SEG-08','Intentos no autorizados','Regla documentada','Perfiles','Crear una función en el esquema','recepcionista',
 $q$CREATE FUNCTION public.fn_intruso() RETURNS int LANGUAGE sql AS 'SELECT 1'$q$,'42501'),
('SEG-09','Intentos no autorizados','Regla documentada','Perfiles','Eliminar el esquema completo (DROP SCHEMA public)','recepcionista',
 $q$DROP SCHEMA public CASCADE$q$,'42501'),
('SEG-10','Intentos no autorizados','Regla documentada','Perfiles','Crear un usuario nuevo (CREATE ROLE)','recepcionista',
 $q$CREATE ROLE intruso LOGIN$q$,'42501'),
('SEG-11','Intentos no autorizados','Regla documentada','Perfiles','Darse privilegios de superusuario (ALTER ROLE ... SUPERUSER)','recepcionista',
 $q$ALTER ROLE recepcionista SUPERUSER$q$,'42501'),
-- Nota: un SET ROLE no sirve para probar la escalada, porque esta prueba corre en
-- una sesión de superusuario (que siempre puede cambiar de rol). Se verifica la
-- causa: que recepcionista no sea miembro de administrador_bd ni de ningún rol con más poder.
('SEG-12','Intentos no autorizados','Regla documentada','Perfiles','recepcionista no es miembro de administrador_bd (no puede escalar con SET ROLE)',NULL,
 $q$SELECT 1/(CASE WHEN NOT pg_has_role('recepcionista','administrador_bd','MEMBER') THEN 1 ELSE 0 END)$q$,'OK'),
('SEG-13','Intentos no autorizados','Regla documentada','Perfiles','Leer las contraseñas del motor (pg_authid)','recepcionista',
 $q$SELECT rolpassword FROM pg_authid$q$,'42501'),
('SEG-14','Intentos no autorizados','Regla documentada','Perfiles','Exportar datos a un archivo del servidor (COPY ... TO)','recepcionista',
 $q$COPY cliente TO '/tmp/pelucan_exfiltracion.csv'$q$,'42501'),
('SEG-15','Intentos no autorizados','Regla documentada','Perfiles','Cambiar el dueño de una tabla','recepcionista',
 $q$ALTER TABLE cliente OWNER TO recepcionista$q$,'42501');

-- ---------------------------------------------------------------------
-- 4. administrador_bd: mantenimiento del esquema y de accesos
-- ---------------------------------------------------------------------
INSERT INTO casos (id, categoria, tipo, regla, descripcion, rol, sentencia, esperado) VALUES
('ADM-01','Administrador','Regla documentada','Perfiles','administrador_bd crea una tabla','administrador_bd',
 $q$CREATE TABLE prueba_admin (id int)$q$,'OK'),
('ADM-02','Administrador','Regla documentada','Perfiles','administrador_bd modifica una tabla existente (ALTER TABLE)','administrador_bd',
 $q$ALTER TABLE servicio ADD COLUMN temporal int$q$,'OK'),
('ADM-03','Administrador','Regla documentada','Perfiles','administrador_bd crea un índice','administrador_bd',
 $q$CREATE INDEX ix_prueba_admin ON cliente (apellido)$q$,'OK'),
('ADM-04','Administrador','Regla documentada','Perfiles','administrador_bd lee todas las tablas (necesario para el respaldo con pg_dump)','administrador_bd',
 $q$SELECT (SELECT count(*) FROM cliente)+(SELECT count(*) FROM mascota)+(SELECT count(*) FROM turno)
         +(SELECT count(*) FROM pago)+(SELECT count(*) FROM servicio)+(SELECT count(*) FROM peluquero)$q$,'OK'),
('ADM-05','Administrador','Regla documentada','Perfiles','administrador_bd gestiona accesos (crea un rol de usuario)','administrador_bd',
 $q$CREATE ROLE usuario_prueba_tmp NOLOGIN$q$,'OK'),
('ADM-06','Administrador','Regla documentada','Perfiles','administrador_bd no puede convertirse en superusuario','administrador_bd',
 $q$ALTER ROLE administrador_bd SUPERUSER$q$,'42501');

-- ---------------------------------------------------------------------
-- DETALLE (última sentencia: es la que muestra pgAdmin)
-- ---------------------------------------------------------------------
-- RESUMEN (seleccionar solo esta sentencia y ejecutar):
-- SELECT categoria, resultado, count(*) AS casos
--   FROM pg_temp.ejecutar_casos() GROUP BY categoria, resultado ORDER BY categoria, resultado;

SELECT * FROM pg_temp.ejecutar_casos();
