-- =====================================================================
-- PELUCAN - Auditoría de los datos de prueba contra las reglas de negocio
-- Script 02: SOLO LECTURA (no modifica nada)
-- Responsable: Emmanuel Gillio (Validación y Reglas de Negocio)
-- Motor: PostgreSQL 14 o superior
-- =====================================================================
-- PARA QUÉ SIRVE
--   Cuando el equipo cargue los registros de prueba ampliados, este script
--   comprueba que respeten las 18 reglas del informe: edades no negativas,
--   duraciones positivas, montos mayores a 0, sin solapamientos, etc.
--   Sirve sobre cualquier conjunto de datos, no depende de ids concretos.
--
-- CÓMO LEERLO
--   Cada control devuelve cuántas filas (o pares de filas) incumplen.
--   severidad : Error        -> incumple una regla del informe (debe dar 0)
--               Advertencia  -> dato sospechoso, conviene revisarlo
--               Informativo  -> solo para conocer los datos
--   estado    : OK | VIOLACIÓN (Error) | REVISAR (Advertencia) | INFO
--
--   El archivo tiene DOS consultas: (1) cobertura de la muestra y (2) controles.
--   En pgAdmin se muestra la última (los controles); para ver la cobertura,
--   seleccionar la primera consulta y ejecutarla aparte.
-- =====================================================================

-- ---------------------------------------------------------------------
-- (1) COBERTURA: ¿la muestra es representativa?
--     FALTA = no hay ningún registro de esa categoría en los datos.
-- ---------------------------------------------------------------------
SELECT aspecto, categoria, cantidad,
       CASE WHEN cantidad = 0 THEN 'FALTA' ELSE 'OK' END AS evaluacion
FROM (
    SELECT 'Registros por tabla' AS aspecto, 'cliente'   AS categoria, count(*) AS cantidad FROM cliente
    UNION ALL SELECT 'Registros por tabla', 'mascota',   count(*) FROM mascota
    UNION ALL SELECT 'Registros por tabla', 'peluquero', count(*) FROM peluquero
    UNION ALL SELECT 'Registros por tabla', 'servicio',  count(*) FROM servicio
    UNION ALL SELECT 'Registros por tabla', 'turno',     count(*) FROM turno
    UNION ALL SELECT 'Registros por tabla', 'pago',      count(*) FROM pago
    UNION ALL
    SELECT 'Turnos por estado', e.estado, count(t.id_turno)
    FROM (VALUES ('Pendiente'), ('Confirmado'), ('Completado'), ('Cancelado')) AS e(estado)
    LEFT JOIN turno t ON t.estado = e.estado GROUP BY e.estado
    UNION ALL
    SELECT 'Pagos por método', m.metodo, count(p.id_pago)
    FROM (VALUES ('Efectivo'), ('Transferencia'), ('Tarjeta')) AS m(metodo)
    LEFT JOIN pago p ON p.metodo_pago = m.metodo GROUP BY m.metodo
    UNION ALL
    SELECT 'Mascotas por tamaño', z.tamano, count(ma.id_mascota)
    FROM (VALUES ('Pequeño'), ('Mediano'), ('Grande')) AS z(tamano)
    LEFT JOIN mascota ma ON ma.tamano = z.tamano GROUP BY z.tamano
    UNION ALL SELECT 'Variedad', 'razas distintas',               count(DISTINCT raza) FROM mascota
    UNION ALL SELECT 'Variedad', 'clientes con 2 o más mascotas', count(*) FROM (SELECT id_cliente FROM mascota GROUP BY id_cliente HAVING count(*) >= 2) x
    UNION ALL SELECT 'Variedad', 'mascotas con 2 o más turnos',   count(*) FROM (SELECT id_mascota FROM turno GROUP BY id_mascota HAVING count(*) >= 2) x
    UNION ALL SELECT 'Variedad', 'peluqueros con turnos',         count(DISTINCT id_peluquero) FROM turno
    UNION ALL SELECT 'Variedad', 'servicios usados en turnos',    count(DISTINCT id_servicio) FROM turno
    UNION ALL SELECT 'Variedad', 'clientes sin correo (NULL)',    count(*) FROM cliente WHERE correo IS NULL
) AS cobertura
ORDER BY aspecto, categoria;

-- ---------------------------------------------------------------------
-- (2) CONTROLES DE REGLAS DE NEGOCIO
-- ---------------------------------------------------------------------
SELECT id, regla, severidad, descripcion, violaciones,
       CASE
           WHEN violaciones = 0 AND severidad <> 'Informativo' THEN 'OK'
           WHEN severidad = 'Error'       THEN 'VIOLACIÓN'
           WHEN severidad = 'Advertencia' THEN 'REVISAR'
           ELSE 'INFO'
       END AS estado
FROM (
    -- ----------------------------- Clientes -----------------------------
    SELECT 'CL-01' AS id, 'R2' AS regla, 'Error' AS severidad,
           'Clientes con nombre, apellido o teléfono vacío o nulo' AS descripcion,
           count(*) AS violaciones
    FROM cliente
    WHERE nombre IS NULL OR btrim(nombre) = '' OR apellido IS NULL OR btrim(apellido) = ''
       OR telefono IS NULL OR btrim(telefono) = ''
    UNION ALL
    SELECT 'CL-02', 'R3', 'Error', 'Teléfonos repetidos entre clientes (grupos)', count(*)
    FROM (SELECT telefono FROM cliente GROUP BY telefono HAVING count(*) > 1) x
    UNION ALL
    SELECT 'CL-03', 'R3', 'Advertencia',
           'Teléfonos que son el mismo número escrito distinto (guiones, espacios) entre clientes (grupos)', count(*)
    FROM (SELECT regexp_replace(telefono, '\D', '', 'g') AS num
          FROM cliente GROUP BY 1 HAVING count(DISTINCT telefono) > 1) x
    UNION ALL
    SELECT 'CL-04', 'R3', 'Error', 'Correos repetidos sin distinguir mayúsculas ni espacios (grupos)', count(*)
    FROM (SELECT lower(btrim(correo)) FROM cliente
          WHERE correo IS NOT NULL AND btrim(correo) <> ''
          GROUP BY 1 HAVING count(*) > 1) x
    UNION ALL
    SELECT 'CL-05', 'R3', 'Advertencia', 'Correos guardados como cadena vacía en lugar de NULL', count(*)
    FROM cliente WHERE correo IS NOT NULL AND btrim(correo) = ''
    -- ----------------------------- Mascotas -----------------------------
    UNION ALL
    SELECT 'MA-01', 'R5', 'Error', 'Mascotas con edad negativa', count(*) FROM mascota WHERE edad < 0
    UNION ALL
    SELECT 'MA-02', 'R5', 'Error', 'Mascotas con tamaño fuera de Pequeño / Mediano / Grande', count(*)
    FROM mascota WHERE tamano IS NULL OR tamano NOT IN ('Pequeño', 'Mediano', 'Grande')
    UNION ALL
    SELECT 'MA-03', 'R1', 'Error', 'Mascotas sin dueño o con un dueño que no existe', count(*)
    FROM mascota m LEFT JOIN cliente c ON c.id_cliente = m.id_cliente WHERE c.id_cliente IS NULL
    UNION ALL
    SELECT 'MA-04', 'R2', 'Error', 'Mascotas con nombre vacío o nulo', count(*)
    FROM mascota WHERE nombre IS NULL OR btrim(nombre) = ''
    UNION ALL
    SELECT 'MA-05', 'R5', 'Advertencia', 'Mascotas con edad mayor a 30 años (posible error de carga)', count(*)
    FROM mascota WHERE edad > 30
    -- ----------------------------- Servicios ----------------------------
    UNION ALL
    SELECT 'SE-01', 'R6', 'Error', 'Servicios con duración estimada nula o menor o igual a 0', count(*)
    FROM servicio WHERE duracion_estimada IS NULL OR duracion_estimada <= 0
    UNION ALL
    SELECT 'SE-02', 'R6', 'Error', 'Servicios con precio base nulo o negativo', count(*)
    FROM servicio WHERE precio_base IS NULL OR precio_base < 0
    UNION ALL
    SELECT 'SE-03', 'R6', 'Error', 'Nombres de servicio repetidos sin distinguir mayúsculas ni espacios (grupos)', count(*)
    FROM (SELECT lower(btrim(nombre_servicio)) FROM servicio GROUP BY 1 HAVING count(*) > 1) x
    UNION ALL
    SELECT 'SE-04', 'R6', 'Error', 'Servicios con nombre vacío o nulo', count(*)
    FROM servicio WHERE nombre_servicio IS NULL OR btrim(nombre_servicio) = ''
    -- ----------------------------- Peluqueros ---------------------------
    UNION ALL
    SELECT 'PE-01', 'R7', 'Error', 'Peluqueros con nombre, apellido o teléfono vacío o nulo', count(*)
    FROM peluquero
    WHERE nombre IS NULL OR btrim(nombre) = '' OR apellido IS NULL OR btrim(apellido) = ''
       OR telefono IS NULL OR btrim(telefono) = ''
    -- ------------------------------ Turnos ------------------------------
    UNION ALL
    SELECT 'TU-01', 'R9', 'Error', 'Turnos con mascota, peluquero o servicio nulo o inexistente', count(*)
    FROM turno t
    LEFT JOIN mascota   m ON m.id_mascota   = t.id_mascota
    LEFT JOIN peluquero p ON p.id_peluquero = t.id_peluquero
    LEFT JOIN servicio  s ON s.id_servicio  = t.id_servicio
    WHERE m.id_mascota IS NULL OR p.id_peluquero IS NULL OR s.id_servicio IS NULL
    UNION ALL
    SELECT 'TU-02', 'R15', 'Error', 'Turnos con estado fuera de Pendiente / Confirmado / Completado / Cancelado', count(*)
    FROM turno WHERE estado IS NULL OR estado NOT IN ('Pendiente', 'Confirmado', 'Completado', 'Cancelado')
    UNION ALL
    SELECT 'TU-03', 'R9', 'Error', 'Turnos sin fecha u hora', count(*)
    FROM turno WHERE fecha IS NULL OR hora IS NULL
    UNION ALL
    SELECT 'TU-04', 'R10', 'Error', 'Mascotas con dos turnos no cancelados en la misma fecha y hora (grupos)', count(*)
    FROM (SELECT id_mascota FROM turno WHERE estado <> 'Cancelado'
          GROUP BY id_mascota, fecha, hora HAVING count(*) > 1) x
    UNION ALL
    SELECT 'TU-05', 'R11', 'Error', 'Peluqueros con dos turnos no cancelados en la misma fecha y hora (grupos)', count(*)
    FROM (SELECT id_peluquero FROM turno WHERE estado <> 'Cancelado'
          GROUP BY id_peluquero, fecha, hora HAVING count(*) > 1) x
    UNION ALL
    SELECT 'TU-06', 'R12', 'Error',
           'Pares de turnos del mismo peluquero que se solapan por duración del servicio (no cancelados)', count(*)
    FROM turno a
    JOIN servicio sa ON sa.id_servicio = a.id_servicio
    JOIN turno b     ON b.id_peluquero = a.id_peluquero AND b.fecha = a.fecha AND b.id_turno > a.id_turno
    JOIN servicio sb ON sb.id_servicio = b.id_servicio
    WHERE a.estado <> 'Cancelado' AND b.estado <> 'Cancelado'
      AND (a.fecha + a.hora) < (b.fecha + b.hora) + sb.duracion_estimada * INTERVAL '1 minute'
      AND (b.fecha + b.hora) < (a.fecha + a.hora) + sa.duracion_estimada * INTERVAL '1 minute'
    UNION ALL
    SELECT 'TU-07', 'R10', 'Error',
           'Pares de turnos de la misma mascota que se solapan por duración del servicio (no cancelados)', count(*)
    FROM turno a
    JOIN servicio sa ON sa.id_servicio = a.id_servicio
    JOIN turno b     ON b.id_mascota = a.id_mascota AND b.fecha = a.fecha AND b.id_turno > a.id_turno
    JOIN servicio sb ON sb.id_servicio = b.id_servicio
    WHERE a.estado <> 'Cancelado' AND b.estado <> 'Cancelado'
      AND (a.fecha + a.hora) < (b.fecha + b.hora) + sb.duracion_estimada * INTERVAL '1 minute'
      AND (b.fecha + b.hora) < (a.fecha + a.hora) + sa.duracion_estimada * INTERVAL '1 minute'
    UNION ALL
    SELECT 'TU-08', 'R14', 'Advertencia',
           'Turnos Pendiente o Confirmado cuya fecha y hora ya pasaron (agenda vencida)', count(*)
    FROM turno WHERE estado IN ('Pendiente', 'Confirmado') AND (fecha + hora) < localtimestamp
    UNION ALL
    SELECT 'TU-09', 'R15', 'Advertencia', 'Turnos Completado con fecha y hora futuras', count(*)
    FROM turno WHERE estado = 'Completado' AND (fecha + hora) > localtimestamp
    UNION ALL
    SELECT 'TU-10', 'Interfaz', 'Advertencia',
           'Turnos fuera del horario de la interfaz (08:00 a 19:30)', count(*)
    FROM turno WHERE hora < TIME '08:00' OR hora > TIME '19:30'
    -- ------------------------------- Pagos ------------------------------
    UNION ALL
    SELECT 'PA-01', 'R17', 'Error', 'Pagos con monto nulo o menor o igual a 0', count(*)
    FROM pago WHERE monto IS NULL OR monto <= 0
    UNION ALL
    SELECT 'PA-02', 'R17', 'Error', 'Pagos con método distinto de Efectivo / Transferencia / Tarjeta', count(*)
    FROM pago WHERE metodo_pago IS NULL OR metodo_pago NOT IN ('Efectivo', 'Transferencia', 'Tarjeta')
    UNION ALL
    SELECT 'PA-03', 'R16', 'Error', 'Pagos sin turno o con un turno que no existe', count(*)
    FROM pago p LEFT JOIN turno t ON t.id_turno = p.id_turno WHERE t.id_turno IS NULL
    UNION ALL
    SELECT 'PA-04', 'R16', 'Error', 'Turnos con más de un pago (relación 1:1)', count(*)
    FROM (SELECT id_turno FROM pago GROUP BY id_turno HAVING count(*) > 1) x
    UNION ALL
    SELECT 'PA-05', 'R16', 'Advertencia', 'Turnos Completado sin ningún pago registrado', count(*)
    FROM turno t WHERE t.estado = 'Completado' AND NOT EXISTS (SELECT 1 FROM pago p WHERE p.id_turno = t.id_turno)
    UNION ALL
    SELECT 'PA-06', 'R16', 'Advertencia', 'Pagos registrados sobre turnos Cancelados', count(*)
    FROM pago p JOIN turno t ON t.id_turno = p.id_turno WHERE t.estado = 'Cancelado'
    UNION ALL
    SELECT 'PA-07', 'R17', 'Advertencia', 'Pagos con fecha anterior a la fecha del turno', count(*)
    FROM pago p JOIN turno t ON t.id_turno = p.id_turno WHERE p.fecha_pago::date < t.fecha
    UNION ALL
    SELECT 'PA-08', 'R17', 'Informativo', 'Pagos cuyo monto difiere del precio base del servicio (descuentos o recargos)', count(*)
    FROM pago p JOIN turno t ON t.id_turno = p.id_turno JOIN servicio s ON s.id_servicio = t.id_servicio
    WHERE p.monto <> s.precio_base
) AS controles
ORDER BY id;
