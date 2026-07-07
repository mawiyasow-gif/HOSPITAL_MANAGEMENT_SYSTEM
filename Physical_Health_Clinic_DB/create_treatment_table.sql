-- Create Treatment Table for Physical Health Clinic Record System

USE Pysical_Health_Clinic_DB;

CREATE TABLE IF NOT EXISTS Treatment (
    TreatmentID INT AUTO_INCREMENT PRIMARY KEY,
    TreatmentName VARCHAR(255) NOT NULL,
    Dosage VARCHAR(255) NOT NULL,
    Duration VARCHAR(255) NOT NULL,
    PatientID INT NOT NULL,
    WorkerID INT NOT NULL,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
    FOREIGN KEY (WorkerID) REFERENCES Health_Workers(WorkerID)
);
