-- =====================================================
-- RESTABLECER ROLES PREDETERMINADOS DEL SISTEMA
-- =====================================================
-- Este script limpia y recrea los 4 roles base con sus
-- configuraciones correctas para coincidir con los módulos
-- =====================================================

-- =====================================================
-- PASO 1: LIMPIAR ROLES EXISTENTES (CUIDADO!)
-- =====================================================
-- ADVERTENCIA: Esto eliminará todos los roles y sus asignaciones
-- Los usuarios quedarán sin rol asignado temporalmente

SET FOREIGN_KEY_CHECKS = 0;

-- Eliminar asignaciones de módulos a roles
DELETE FROM module_x_rol;

-- Eliminar roles (excepto si hay usuarios asignados)
-- Primero, desasignar roles de usuarios temporalmente
UPDATE user SET id_rol = NULL WHERE id_rol IS NOT NULL;

-- Ahora eliminar roles
DELETE FROM rol;
ALTER TABLE rol AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- PASO 2: CREAR ROLES BASE DEL SISTEMA
-- =====================================================
-- 4 roles predeterminados con IDs fijos

INSERT INTO rol (id, name, description, state, created_at, updated_at) VALUES
(1, 'Admin', 'Administrador del sistema con acceso completo', 1, NOW(), NOW()),
(2, 'Doctor', 'Médico con acceso a citas y análisis de pacientes', 1, NOW(), NOW()),
(3, 'patient', 'Paciente con acceso a sus citas y análisis', 1, NOW(), NOW()),
(4, 'secretary', 'Secretaria con acceso a gestión de citas', 1, NOW(), NOW());

-- =====================================================
-- PASO 3: ASIGNAR MÓDULOS A ROLES BASE
-- =====================================================
-- Estos módulos deben existir previamente
-- Si no existen, ejecuta primero setup_modulos_sistema.sql

-- ========================================
-- ROL 1: ADMINISTRADOR
-- ========================================
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(1, 1, 1, NOW(), NOW()),  -- Administración
(1, 2, 1, NOW(), NOW()),  -- Citas
(1, 3, 1, NOW(), NOW());  -- Análisis

-- ========================================
-- ROL 2: DOCTOR
-- ========================================
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(2, 2, 1, NOW(), NOW()),  -- Citas
(2, 3, 1, NOW(), NOW());  -- Análisis

-- ========================================
-- ROL 3: PACIENTE
-- ========================================
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(3, 2, 1, NOW(), NOW()),  -- Citas
(3, 3, 1, NOW(), NOW());  -- Análisis

-- ========================================
-- ROL 4: SECRETARIA
-- ========================================
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(4, 2, 1, NOW(), NOW()),  -- Citas
(4, 4, 1, NOW(), NOW());  -- Ver Usuarios

-- =====================================================
-- PASO 4: REASIGNAR USUARIOS A SUS ROLES
-- =====================================================
-- Ajusta estos comandos según tus usuarios existentes

-- Ejemplo: Asignar rol Admin al primer usuario
-- UPDATE user SET id_rol = 1 WHERE id = 1;

-- Listar usuarios sin rol asignado para revisión
SELECT 
    id,
    user_name,
    full_name,
    email,
    id_rol
FROM user
WHERE id_rol IS NULL AND state = 1;

-- =====================================================
-- PASO 5: VERIFICACIÓN
-- =====================================================

-- Ver roles creados
SELECT 
    id,
    name,
    description,
    state
FROM rol
WHERE state = 1
ORDER BY id;

-- Ver módulos asignados a cada rol
SELECT 
    r.id as rol_id,
    r.name as rol_name,
    m.id as module_id,
    m.name as module_name,
    m.description
FROM rol r
LEFT JOIN module_x_rol mx ON r.id = mx.id_rol AND mx.state = 1
LEFT JOIN module m ON mx.id_module = m.id AND m.state = 1
WHERE r.state = 1
ORDER BY r.id, m.id;

-- Resumen de permisos por rol
SELECT 
    r.id,
    r.name as rol,
    GROUP_CONCAT(m.name ORDER BY m.id SEPARATOR ', ') as modulos_asignados,
    COUNT(m.id) as total_modulos
FROM rol r
LEFT JOIN module_x_rol mx ON r.id = mx.id_rol AND mx.state = 1
LEFT JOIN module m ON mx.id_module = m.id AND m.state = 1
WHERE r.state = 1
GROUP BY r.id, r.name
ORDER BY r.id;

-- =====================================================
-- DOCUMENTACIÓN
-- =====================================================

/*
========================================
ROLES RESTABLECIDOS
========================================

ID  | Nombre    | Ruta        | Módulos
----|-----------|-------------|---------------------------
1   | Admin     | /admin      | Administración, Citas, Análisis
2   | Doctor    | /doctor     | Citas, Análisis
3   | patient   | /patient    | Citas, Análisis
4   | secretary | /secretary  | Citas, Ver Usuarios

========================================
PRÓXIMOS PASOS
========================================

1. Verificar que los 4 roles se crearon correctamente:
   SELECT * FROM rol WHERE id IN (1,2,3,4);

2. Verificar que los módulos están asignados:
   SELECT * FROM module_x_rol;

3. Reasignar usuarios a sus roles apropiados:
   
   -- Usuario administrador
   UPDATE user SET id_rol = 1 WHERE user_name = 'admin';
   
   -- Usuarios doctores
   UPDATE user SET id_rol = 2 WHERE user_name IN ('doctor1', 'doctor2');
   
   -- Usuarios pacientes
   UPDATE user SET id_rol = 3 WHERE user_name LIKE 'patient%';
   
   -- Usuarios secretarias
   UPDATE user SET id_rol = 4 WHERE user_name LIKE 'secretary%';

4. Verificar que todos los usuarios tienen rol:
   SELECT user_name, full_name, id_rol 
   FROM user 
   WHERE state = 1 
   ORDER BY id_rol;

========================================
COMANDOS ÚTILES POST-INSTALACIÓN
========================================

-- Ver usuarios por rol
SELECT 
    r.name as rol,
    COUNT(u.id) as total_usuarios,
    GROUP_CONCAT(u.user_name SEPARATOR ', ') as usuarios
FROM rol r
LEFT JOIN user u ON r.id = u.id_rol AND u.state = 1
WHERE r.state = 1
GROUP BY r.id, r.name;

-- Crear nuevo usuario administrador
INSERT INTO user (user_name, password, full_name, last_name, email, id_rol, state)
VALUES ('admin', '$2b$12$hashed_password', 'Admin', 'Sistema', 'admin@example.com', 1, 1);

-- Cambiar rol de un usuario
UPDATE user SET id_rol = 1 WHERE user_name = 'usuario123';

*/
