-- =====================================================================
-- PELUCAN - Roles y permisos del SGBD (PostgreSQL)
-- Ejecutar como superusuario (postgres), conectada a la base del proyecto:
--   psql -U postgres -d pelucan
-- =====================================================================

-- 1) ROLES DE GRUPO (sin login): concentran los permisos
CREATE ROLE recepcionista     NOLOGIN;
CREATE ROLE administrador_bd  NOLOGIN;

-- 2) USUARIOS CON LOGIN (cambiar contraseñas antes de entregar)
CREATE USER recepcion_user  WITH PASSWORD 'Recep_2026!';
CREATE USER admin_pelucan   WITH PASSWORD 'Admin_2026!';

GRANT recepcionista    TO recepcion_user;
GRANT administrador_bd TO admin_pelucan;

-- 3) LIMPIEZA: nadie hereda permisos por defecto

REVOKE ALL ON DATABASE pelucan FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;   -- nadie crea objetos salvo admin

GRANT CONNECT ON DATABASE pelucan TO recepcionista, administrador_bd;
GRANT USAGE   ON SCHEMA public    TO recepcionista, administrador_bd;

-- ---------------------------------------------------------------------
-- 3b) DUEÑO DE LAS TABLAS: administrador_bd pasa a ser el dueño.
--     Se le permite hacer ALTER / DROP (modificar el esquema).
--     Las secuencias de las columnas SERIAL cambian de dueño junto con la tabla.
-- ---------------------------------------------------------------------
ALTER TABLE cliente   OWNER TO administrador_bd;
ALTER TABLE mascota   OWNER TO administrador_bd;
ALTER TABLE peluquero OWNER TO administrador_bd;
ALTER TABLE servicio  OWNER TO administrador_bd;
ALTER TABLE turno     OWNER TO administrador_bd;
ALTER TABLE pago      OWNER TO administrador_bd;

-- 4) recepcionista: operación diaria (según matriz del documento)
--    Clientes, mascotas, servicios, peluqueros, turnos y pagos:
--    consulta, alta, modificación y baja (las bajas siguen limitadas
--    por las FK ON DELETE RESTRICT y las reglas de negocio).
--    Sin permisos de esquema (CREATE, ALTER, DROP, TRUNCATE).

GRANT SELECT, INSERT, UPDATE, DELETE ON
    cliente, mascota, peluquero, servicio, turno, pago
TO recepcionista;

-- Las columnas SERIAL usan secuencias: sin esto el INSERT falla
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO recepcionista;


-- 5) administrador_bd: esquema, accesos, respaldo y restauración

GRANT ALL PRIVILEGES ON DATABASE pelucan TO administrador_bd;
GRANT ALL PRIVILEGES ON SCHEMA public    TO administrador_bd;
GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA public TO administrador_bd;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO administrador_bd;
ALTER ROLE administrador_bd CREATEROLE;       -- gestionar usuarios/credenciales


-- 6) Tablas que se creen más adelante heredan los mismos permisos

ALTER DEFAULT PRIVILEGES FOR ROLE admin_pelucan IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO recepcionista;
ALTER DEFAULT PRIVILEGES FOR ROLE admin_pelucan IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO recepcionista;


-- 7) VERIFICACIÓN 

-- Roles y atributos
\du

-- Permisos por tabla (en psql)
\dp

-- Permisos de tabla del rol recepcionista
SELECT table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'recepcionista'
ORDER BY table_name, privilege_type;

-- ¿Puede crear objetos en el schema?
SELECT has_schema_privilege('recepcion_user', 'public', 'CREATE') AS recep_crea,
has_schema_privilege('admin_pelucan',  'public', 'CREATE') AS admin_crea;

-- ---------------------------------------------------------------------
-- 8) PRUEBAS (conectarse como recepcion_user)
--    psql -U recepcion_user -d pelucan -h localhost
-- ---------------------------------------------------------------------
-- Deben FUNCIONAR:
--   SELECT * FROM cliente;
--   INSERT INTO cliente (nombre, apellido, telefono)
--          VALUES ('Prueba', 'Permisos', '3510000000');
--   UPDATE cliente SET nombre = 'Prueba2' WHERE telefono = '3510000000';
--   DELETE FROM cliente WHERE telefono = '3510000000';
--   INSERT INTO servicio (nombre_servicio, duracion_estimada, precio_base)
--          VALUES ('Servicio prueba', 30, 1000);
--
-- Deben FALLAR (ERROR: permission denied / must be owner):
--   ALTER TABLE cliente ADD COLUMN prueba VARCHAR(10);
--   DROP TABLE mascota;
--   CREATE TABLE prueba (id INT);
--   TRUNCATE turno;
--   CREATE ROLE intruso;
--   GRANT ALL ON cliente TO recepcion_user;
--
-- Como admin_pelucan: el CREATE TABLE / ALTER TABLE sí debe funcionar
-- (es dueño de las tablas por el ALTER ... OWNER TO del paso 3b):
--   ALTER TABLE cliente ADD COLUMN prueba VARCHAR(10);
--   ALTER TABLE cliente DROP COLUMN prueba;
--   CREATE TABLE prueba (id INT);
--   DROP TABLE prueba;
--
-- Verificar los dueños de las tablas:
--   SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public';
