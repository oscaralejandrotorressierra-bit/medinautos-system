-- Migracion simple para SQLite: agregar campos nuevos a mecanicos

ALTER TABLE mecanicos ADD COLUMN eps TEXT;
ALTER TABLE mecanicos ADD COLUMN tipo_sangre TEXT;
ALTER TABLE mecanicos ADD COLUMN fecha_nacimiento DATE;
ALTER TABLE mecanicos ADD COLUMN contacto_emergencia_nombre TEXT;
ALTER TABLE mecanicos ADD COLUMN contacto_emergencia_parentesco TEXT;
ALTER TABLE mecanicos ADD COLUMN contacto_emergencia_telefono TEXT;
