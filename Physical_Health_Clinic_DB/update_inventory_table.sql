-- Update Inventory Table to remove TreatmentID column
-- This script updates the Inventory table to work independently without Treatment table connection

USE Pysical_Health_Clinic_DB;

-- Drop the foreign key constraint first
ALTER TABLE Inventory DROP FOREIGN KEY IF EXISTS inventory_ibfk_1;

-- Remove the TreatmentID column
ALTER TABLE Inventory DROP COLUMN IF EXISTS TreatmentID;

-- Verify the table structure
DESCRIBE Inventory;
