-- =====================================================
-- SCRIPT DE MÓDULOS ACTUALIZADOS PARA SISTEMA MÉDICO
-- =====================================================
-- Este script limpia y recrea los módulos del sistema
-- según las funcionalidades reales del proyecto
-- =====================================================

-- 1. LIMPIAR DATOS EXISTENTES (OPCIONAL - Descomenta si quieres empezar de cero)
-- Primero eliminamos las relaciones, luego los módulos
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM module_x_rol;
DELETE FROM module;
ALTER TABLE module AUTO_INCREMENT = 1;
SET FOREIGN_KEY_CHECKS = 1;

-- 2. INSERTAR MÓDULOS DEL SISTEMA (SIMPLIFICADOS)
-- Módulos agrupados por funcionalidad principal

INSERT INTO module (id, name, description, state, created_at, updated_at) VALUES
-- Módulos Core (4 módulos principales)
(1, 'Administración', 'Gestión de usuarios, roles y permisos del sistema', 1, NOW(), NOW()),
(2, 'Citas', 'Gestión completa de citas médicas (agendar, ver, modificar)', 1, NOW(), NOW()),
(3, 'Análisis', 'Gestión de análisis clínicos y resultados', 1, NOW(), NOW()),
(4, 'Reportes', 'Dashboard y reportes del sistema', 1, NOW(), NOW()),

-- Módulos Complementarios (2 módulos)
(5, 'Pacientes', 'Gestión de información de pacientes', 1, NOW(), NOW()),
(6, 'Configuración', 'Configuración general del sistema (tipos de documento, estados, ubicaciones)', 1, NOW(), NOW());

-- =====================================================
-- 3. ASIGNAR MÓDULOS A ROLES EXISTENTES
-- =====================================================

-- IMPORTANTE: Ajusta los id_rol según tu base de datos
-- Para ver tus roles actuales ejecuta: SELECT * FROM rol;
-- Nota: Ya limpiamos module_x_rol arriba, así que no necesitamos DELETE aquí

-- ========================================
-- ROL 1: ADMINISTRADOR (Acceso Total)
-- ========================================
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(1, 1, 1, NOW(), NOW()),  -- Administración
(1, 2, 1, NOW(), NOW()),  -- Citas
(1, 3, 1, NOW(), NOW()),  -- Análisis
(1, 4, 1, NOW(), NOW()),  -- Reportes
(1, 5, 1, NOW(), NOW()),  -- Pacientes
(1, 6, 1, NOW(), NOW());  -- Configuración

-- ========================================
-- ROL 2: DOCTOR
-- ========================================
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(2, 2, 1, NOW(), NOW()),  -- Citas (ver sus citas asignadas)
(2, 3, 1, NOW(), NOW()),  -- Análisis (crear/editar/ver)
(2, 4, 1, NOW(), NOW());  -- Reportes (dashboard)

-- ========================================
-- ROL 3: PACIENTE
-- ========================================
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(3, 2, 1, NOW(), NOW()),  -- Citas (agendar y ver propias)
(3, 3, 1, NOW(), NOW());  -- Análisis (ver propios)

-- ========================================
-- ROL 7: SECRETARIA
-- ========================================
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(7, 2, 1, NOW(), NOW()),  -- Citas
(7, 5, 1, NOW(), NOW());  -- Pacientes

-- =====================================================
-- 4. VERIFICAR ASIGNACIONES
-- =====================================================

-- Ver todos los módulos
SELECT * FROM module WHERE state = 1 ORDER BY id;

-- Ver permisos por rol
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

-- Ver módulos de un rol específico (cambia el 1 por el id del rol que quieras ver)
SELECT 
    m.id,
    m.name,
    m.description
FROM module m
JOIN module_x_rol mx ON m.id = mx.id_module
WHERE mx.id_rol = 1 AND mx.state = 1 AND m.state = 1
ORDER BY m.id;

-- =====================================================
-- 5. NOTAS IMPORTANTES
-- =====================================================

/*
========================================
MAPEO SIMPLIFICADO DE MÓDULOS (6 módulos)
========================================

MÓDULO 1 - ADMINISTRACIÓN:
- Gestión de usuarios (crear, editar, eliminar, listar)
- Gestión de roles y permisos
- Asignación de módulos a roles

MÓDULO 2 - CITAS:
- Ver citas (propias o todas según el rol)
- Agendar citas
- Modificar y cancelar citas
- Gestión de estados de citas

MÓDULO 3 - ANÁLISIS:
- Ver análisis clínicos (propios o todos según el rol)
- Crear y editar análisis
- Gestión de resultados
- Estados de análisis

MÓDULO 4 - REPORTES:
- Dashboard Power BI
- Reportes estadísticos
- Visualizaciones

MÓDULO 5 - PACIENTES:
- Gestionar información de pacientes
- Ver perfiles de pacientes
- Editar datos de pacientes

MÓDULO 6 - CONFIGURACIÓN:
- Tipos de documento
- Ubicaciones (departamentos, ciudades, clínicas)
- Tipos de enfermedades
- Atributos del sistema
- Otras configuraciones generales

========================================
USO EN EL FRONTEND:
========================================

// Por nombre
{#if $permissions.hasModule('Administración')}
  <button>Gestionar Usuarios</button>
{/if}

// Por ID
{#if $permissions.hasModule(1)}
  <a href="/admin">Panel Admin</a>
{/if}

// Múltiples módulos
{#if $permissions.hasAnyModule(['Citas', 'Análisis'])}
  <nav>...</nav>
{/if}

========================================
DISTRIBUCIÓN POR ROL:
========================================

ADMIN (rol 1):       Todos (1,2,3,4,5,6)
DOCTOR (rol 2):      Citas, Análisis, Reportes (2,3,4)
PACIENTE (rol 3):    Citas, Análisis (2,3)
SECRETARIA (rol 7):  Citas, Pacientes (2,5)

========================================
VENTAJAS DEL SISTEMA SIMPLIFICADO:
========================================

✓ Menos complejidad al asignar permisos
✓ Más fácil de entender para usuarios finales
✓ Mantenimiento más sencillo
✓ Agrupa funcionalidades relacionadas
✓ Escalable: puedes subdividir más adelante si es necesario
*/

-- =====================================================
-- 6. SCRIPT DE LIMPIEZA (Si necesitas resetear)
-- =====================================================

/*
-- CUIDADO: Esto borra TODOS los módulos y asignaciones
-- Solo usa esto si quieres empezar completamente de cero

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE module_x_rol;
TRUNCATE TABLE module;
SET FOREIGN_KEY_CHECKS = 1;
ALTER TABLE module AUTO_INCREMENT = 1;

-- Luego ejecuta nuevamente las secciones 2 y 3 de este script
*/
