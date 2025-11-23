-- =====================================================
-- CONFIGURACIÓN DE MÓDULOS PARA SISTEMA DE PERMISOS
-- =====================================================
-- Módulos simplificados según funcionalidad real
-- =====================================================

-- =====================================================
-- PASO 1: LIMPIAR DATOS EXISTENTES
-- =====================================================
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM module_x_rol;
DELETE FROM module;
ALTER TABLE module AUTO_INCREMENT = 1;
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- PASO 2: CREAR MÓDULOS BASE DEL SISTEMA
-- =====================================================
-- 4 módulos que coinciden con la funcionalidad real

INSERT INTO module (id, name, description, state, created_at, updated_at) VALUES
(1, 'Administración', 'Gestión completa de usuarios y roles (crear, editar, eliminar usuarios y configurar roles)', 1, NOW(), NOW()),
(2, 'Citas', 'Gestión de citas médicas (agendar, ver, modificar, cancelar)', 1, NOW(), NOW()),
(3, 'Análisis', 'Gestión de análisis clínicos (subir, ver resultados, gestionar)', 1, NOW(), NOW()),
(4, 'Ver Usuarios', 'Solo visualización de lista de usuarios (sin permisos de edición)', 1, NOW(), NOW());

-- =====================================================
-- PASO 3: ASIGNAR MÓDULOS A ROLES BASE
-- =====================================================

-- ========================================
-- ROL 1: ADMINISTRADOR
-- ========================================
-- Panel /admin con tabs: Usuarios, Crear Usuario, Crear Rol, Ver Roles
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(1, 1, 1, NOW(), NOW()),  -- Administración (CRUD usuarios + gestión roles)
(1, 2, 1, NOW(), NOW()),  -- Citas (ver y gestionar todas)
(1, 3, 1, NOW(), NOW());  -- Análisis (ver y gestionar todos)

-- ========================================
-- ROL 2: DOCTOR
-- ========================================
-- Panel /doctor con tabs: Dashboard, Citas, Análisis
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(2, 2, 1, NOW(), NOW()),  -- Citas (ver citas asignadas)
(2, 3, 1, NOW(), NOW());  -- Análisis (gestionar análisis de pacientes)

-- ========================================
-- ROL 3: PACIENTE
-- ========================================
-- Panel /patient con tabs: Subir Imagen, Resultados, Agendar Cita, Perfil
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(3, 2, 1, NOW(), NOW()),  -- Citas (agendar y ver propias)
(3, 3, 1, NOW(), NOW());  -- Análisis (subir y ver resultados)

-- ========================================
-- ROL 4: SECRETARIA
-- ========================================
-- Panel /secretary con tabs: Lista Citas, Agendar Nueva Cita
INSERT INTO module_x_rol (id_rol, id_module, state, created_at, updated_at) VALUES
(4, 2, 1, NOW(), NOW()),  -- Citas (gestión completa)
(4, 4, 1, NOW(), NOW());  -- Ver Usuarios (para seleccionar al agendar)

-- =====================================================
-- PASO 4: VERIFICACIÓN
-- =====================================================

-- Ver módulos creados
SELECT id, name, description FROM module WHERE state = 1 ORDER BY id;

-- Ver asignaciones por rol
SELECT 
    r.id as rol_id,
    r.name as rol_name,
    GROUP_CONCAT(m.name ORDER BY m.id SEPARATOR ', ') as modulos
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
ROLES BASE (IDs FIJOS)
========================================

ROL 1 - ADMIN → /admin
Módulos: Administración, Citas, Análisis
Tabs visibles:
  • Usuarios (UserTable con DataTable CRUD completo)
  • Crear Usuario (UserForm)
  • Crear Rol (RoleForm)
  • Ver Roles (RolePermissionsTable para asignar módulos)

ROL 2 - DOCTOR → /doctor
Módulos: Citas, Análisis
Tabs visibles:
  • Dashboard (resumen)
  • Citas (AppointmentsTable - solo sus pacientes)
  • Análisis (AnalysesTable - solo sus pacientes)

ROL 3 - PATIENT → /patient
Módulos: Citas, Análisis
Tabs visibles:
  • Subir Imagen (AnalysisUpload)
  • Mis Resultados (AnalysisList)
  • Agendar Cita (AppointmentsForm)
  • Mi Perfil (PatientInfoCard)
  • Actualizar (PatientInfoForm)

ROL 7 - SECRETARY → /secretary
Módulos: Citas, Ver Usuarios
Tabs visibles:
  • Lista de Citas (AppointmentsTable - todas)
  • Agendar Nueva Cita (AppointmentForm - puede ver usuarios)

========================================
ROLES DINÁMICOS → /dinamico
========================================

Para crear rol "Ayudante" con permisos limitados:

1. Crear rol:
   INSERT INTO rol (name, description, state) 
   VALUES ('Ayudante', 'Apoyo administrativo', 1);

2. Asignar módulos (ejemplo: solo ver citas):
   INSERT INTO module_x_rol (id_rol, id_module, state) VALUES
   (8, 2, 1),  -- Citas (solo ver)
   (8, 4, 1);  -- Ver Usuarios

3. Usuario con rol 8 será redirigido a /dinamico
   donde verá sidebar con "Citas" y "Ver Usuarios"

========================================
MAPEO MÓDULOS → COMPONENTES
========================================

1. ADMINISTRACIÓN
   Componentes: UserTable, UserForm, RoleForm, RolePermissionsTable
   Acciones: CRUD completo usuarios + roles
   
2. CITAS
   Componentes: AppointmentsTable, AppointmentsForm
   Acciones: Ver, agendar, editar, cancelar citas
   
3. ANÁLISIS
   Componentes: AnalysesTable, AnalysisUpload, AnalysisList
   Acciones: Ver, subir, gestionar análisis
   
4. VER USUARIOS
   Componentes: UserTable (solo lectura)
   Acciones: Solo visualizar (para seleccionar al agendar)

========================================
NORMALIZACIÓN EN FRONTEND
========================================

Store permissions.js normaliza:
- 'Administración' → 'administracion'
- 'Citas' → 'citas'
- 'Análisis' → 'analisis'
- 'Ver Usuarios' → 'ver_usuarios'

Uso en componentes:
{#if $permissions.hasModule('administracion')}
  <UserCRUD />
{/if}

{#if $permissions.hasModule('citas')}
  <AppointmentsTable />
{/if}

========================================
NOTAS IMPORTANTES
========================================

✓ Ciudades/ubicaciones son servicio EXTERNO (API Express)
  No se gestionan desde admin, solo se consultan

✓ Admin tiene acceso a Citas y Análisis para supervisión

✓ Secretary necesita "Ver Usuarios" para agendar citas
  (debe seleccionar paciente y doctor del dropdown)

✓ Roles dinámicos van a /dinamico con UI adaptativa

✓ Permisos granulares (crear/editar/eliminar) se pueden
  agregar después con tabla module_permission

========================================
COMANDOS ÚTILES
========================================

-- Ver permisos de un usuario
SELECT 
    u.user_name,
    r.name as rol,
    GROUP_CONCAT(m.name) as modulos
FROM user u
JOIN rol r ON u.id_rol = r.id
LEFT JOIN module_x_rol mx ON r.id = mx.id_rol AND mx.state = 1
LEFT JOIN module m ON mx.id_module = m.id
WHERE u.id = 1
GROUP BY u.id;

-- Copiar permisos de Admin a nuevo rol
INSERT INTO module_x_rol (id_rol, id_module, state)
SELECT 9, id_module, state  -- 9 = nuevo rol
FROM module_x_rol
WHERE id_rol = 1 AND state = 1;

*/
