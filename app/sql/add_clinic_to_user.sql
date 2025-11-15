-- Agregar columna id_clinic a la tabla user
ALTER TABLE user ADD COLUMN id_clinic INT DEFAULT NULL;

-- Opcional: Agregar índice para mejorar el rendimiento de consultas
CREATE INDEX idx_user_clinic ON user(id_clinic);

-- Opcional: Si quieres establecer una relación con la tabla clinics del servicio externo
-- (esto es solo documentativo, ya que las tablas están en bases de datos diferentes)
-- La relación se maneja a nivel de aplicación
