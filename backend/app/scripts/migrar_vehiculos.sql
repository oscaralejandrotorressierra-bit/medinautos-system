-- Migracion simple para SQLite: agregar campos nuevos a vehiculos
-- Ejecutar una sola vez sobre medinautos.db

ALTER TABLE vehiculos ADD COLUMN cilindraje INTEGER;
ALTER TABLE vehiculos ADD COLUMN clase TEXT;
ALTER TABLE vehiculos ADD COLUMN km_actual INTEGER;
