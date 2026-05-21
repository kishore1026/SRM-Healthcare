-- ============================================
-- SRM Health Care – Database Schema
-- Database: srm_healthcare
-- Version: 2.0
-- ============================================

CREATE DATABASE IF NOT EXISTS srm_healthcare
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE srm_healthcare;

-- ============================================
-- Table: doctors
-- ============================================
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    doctor_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================
-- Table: patients
-- ============================================
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    designation VARCHAR(100) NOT NULL,
    student_id VARCHAR(50) DEFAULT NULL,
    hostel_name VARCHAR(100) DEFAULT NULL,
    room_number VARCHAR(20) DEFAULT NULL,
    staff_id VARCHAR(50) DEFAULT NULL,
    medical_history TEXT DEFAULT NULL,
    drug_allergy TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_patient_name (patient_name),
    INDEX idx_student_id (student_id),
    INDEX idx_staff_id (staff_id)
) ENGINE=InnoDB;

-- ============================================
-- Table: patient_visits
-- ============================================
CREATE TABLE IF NOT EXISTS patient_visits (
    visit_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    visit_date DATE NOT NULL,
    visit_time TIME NOT NULL,
    serial_number INT DEFAULT NULL,
    complaint TEXT DEFAULT NULL,
    diagnosis TEXT DEFAULT NULL,
    treatment TEXT DEFAULT NULL,
    doctor_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_visit_date (visit_date),
    INDEX idx_diagnosis (diagnosis(255)),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
) ENGINE=InnoDB;

-- ============================================
-- Table: prescriptions
-- ============================================
CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    visit_id INT NOT NULL,
    notes TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES patient_visits(visit_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- Table: medicines
-- ============================================
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(200) NOT NULL,
    drug_type ENUM('Tablets', 'Capsules', 'Injections', 'Eye Drops', 'Ear Drops', 'Ointments') NOT NULL,
    batch_number VARCHAR(50) DEFAULT NULL,
    expiry_date DATE NOT NULL,
    stock_added INT NOT NULL DEFAULT 0,
    stock_deducted INT NOT NULL DEFAULT 0,
    available_balance INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_medicine_name (medicine_name),
    INDEX idx_expiry_date (expiry_date)
) ENGINE=InnoDB;

-- ============================================
-- Table: prescription_items
-- ============================================
CREATE TABLE IF NOT EXISTS prescription_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT NOT NULL,
    medicine_id INT NOT NULL,
    dosage VARCHAR(100) DEFAULT NULL,
    frequency VARCHAR(100) DEFAULT NULL,
    duration VARCHAR(100) DEFAULT NULL,
    quantity INT NOT NULL DEFAULT 1,
    instructions TEXT DEFAULT NULL,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id)
) ENGINE=InnoDB;

-- ============================================
-- Table: medicine_stock_logs
-- ============================================
CREATE TABLE IF NOT EXISTS medicine_stock_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    quantity INT NOT NULL,
    remarks TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================
-- Table: audit_logs
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT DEFAULT NULL,
    action VARCHAR(100) NOT NULL,
    module VARCHAR(50) NOT NULL,
    record_id INT DEFAULT NULL,
    details TEXT DEFAULT NULL,
    ip_address VARCHAR(45) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_action (action),
    INDEX idx_audit_module (module),
    INDEX idx_audit_created (created_at),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON SET NULL
) ENGINE=InnoDB;

-- ============================================
-- Sample seed data for testing
-- ============================================

-- Note: The default doctor (admin/admin123) is auto-created by the Flask app.
-- Below is optional sample data for testing.

-- Sample medicines
INSERT INTO medicines (medicine_name, drug_type, batch_number, expiry_date, stock_added, available_balance) VALUES
('Paracetamol 500mg', 'Tablets', 'BATCH-2025-001', '2027-06-15', 500, 500),
('Amoxicillin 250mg', 'Capsules', 'BATCH-2025-002', '2027-03-20', 300, 300),
('Cetirizine 10mg', 'Tablets', 'BATCH-2025-003', '2027-09-10', 200, 200),
('Omeprazole 20mg', 'Capsules', 'BATCH-2025-004', '2026-12-01', 150, 150),
('Ibuprofen 400mg', 'Tablets', 'BATCH-2025-005', '2027-08-25', 400, 400),
('Betadine Ointment', 'Ointments', 'BATCH-2025-006', '2026-11-30', 80, 80),
('Ciprofloxacin Eye Drops', 'Eye Drops', 'BATCH-2025-007', '2026-07-15', 50, 50),
('Ofloxacin Ear Drops', 'Ear Drops', 'BATCH-2025-008', '2027-01-20', 40, 40),
('Diclofenac Injection', 'Injections', 'BATCH-2025-009', '2026-08-30', 100, 100),
('Azithromycin 500mg', 'Tablets', 'BATCH-2025-010', '2027-04-18', 250, 250),
('Metformin 500mg', 'Tablets', 'BATCH-2025-011', '2027-07-22', 300, 300),
('Dolo 650mg', 'Tablets', 'BATCH-2025-012', '2026-06-01', 8, 8),
('Vitamin B Complex', 'Tablets', 'BATCH-2025-013', '2027-05-15', 5, 5),
('Ranitidine 150mg', 'Tablets', 'BATCH-2025-014', '2026-04-10', 200, 200);
