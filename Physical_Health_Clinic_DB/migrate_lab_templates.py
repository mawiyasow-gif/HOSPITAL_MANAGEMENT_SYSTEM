# migrate_lab_templates.py
import json
from database import connect_db

def ensure_lab_templates_table():
    """Ensure laboratory_templates table exists and default templates are present without dropping any existing database tables or patient records."""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # 1. Create Laboratory_Tests table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Laboratory_Tests (
                TestID INT AUTO_INCREMENT PRIMARY KEY,
                TestName VARCHAR(100) NOT NULL UNIQUE,
                Price DECIMAL(10, 2) NOT NULL
            )
        """)

        # 2. Create laboratory_templates table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS laboratory_templates (
                TemplateID INT AUTO_INCREMENT PRIMARY KEY,
                TestID INT NOT NULL,
                TemplateName VARCHAR(150) NOT NULL,
                TemplateDescription TEXT,
                TemplateFields JSON,
                ReferenceRanges JSON,
                MeasurementUnits JSON,
                DefaultComments TEXT,
                LogoPath VARCHAR(255),
                Status ENUM('Active', 'Inactive') DEFAULT 'Active',
                CreatedBy INT,
                CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UpdatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (TestID) REFERENCES Laboratory_Tests(TestID) ON DELETE CASCADE
            )
        """)

        # 2. Seed standard Laboratory Tests & Default Active Templates if missing
        lab_tests_data = [
            (
                "Complete Blood Count (CBC)", 80000.00,
                "Standard hematology panel analyzing white cells, red cells, hemoglobin, and platelets.",
                [
                    {"name": "White Blood Cells (WBC)", "unit": "x10^9/L", "range": "4.5 - 11.0", "default": ""},
                    {"name": "Red Blood Cells (RBC)", "unit": "x10^12/L", "range": "4.2 - 5.8", "default": ""},
                    {"name": "Hemoglobin (HGB)", "unit": "g/dL", "range": "13.5 - 17.5", "default": ""},
                    {"name": "Hematocrit (HCT)", "unit": "%", "range": "38.5 - 50.0", "default": ""},
                    {"name": "Platelets (PLT)", "unit": "x10^9/L", "range": "150 - 450", "default": ""}
                ],
                "Results correlate with clinical findings. Recheck recommended if abnormal."
            ),
            (
                "Urinalysis", 25000.00,
                "Physical, chemical, and microscopic urine examination panel.",
                [
                    {"name": "Color", "unit": "Visual", "range": "Pale Yellow / Yellow", "default": "Straw Yellow"},
                    {"name": "Appearance", "unit": "Visual", "range": "Clear", "default": "Clear"},
                    {"name": "pH", "unit": "pH", "range": "4.6 - 8.0", "default": "6.0"},
                    {"name": "Specific Gravity", "unit": "SG", "range": "1.005 - 1.030", "default": "1.015"},
                    {"name": "Protein", "unit": "Dipstick", "range": "Negative", "default": "Negative"},
                    {"name": "Glucose", "unit": "Dipstick", "range": "Negative", "default": "Negative"},
                    {"name": "Ketones", "unit": "Dipstick", "range": "Negative", "default": "Negative"},
                    {"name": "Leukocyte Esterase", "unit": "Dipstick", "range": "Negative", "default": "Negative"}
                ],
                "Normal urinary dipstick and physical parameters."
            ),
            (
                "Widal Test", 35000.00,
                "Serological slide agglutination for Salmonella antibodies.",
                [
                    {"name": "Salmonella Typhi O", "unit": "Titer", "range": "< 1:80", "default": "1:40"},
                    {"name": "Salmonella Typhi H", "unit": "Titer", "range": "< 1:80", "default": "1:40"},
                    {"name": "Salmonella Paratyphi AH", "unit": "Titer", "range": "< 1:80", "default": "1:20"},
                    {"name": "Salmonella Paratyphi BH", "unit": "Titer", "range": "< 1:80", "default": "1:20"}
                ],
                "Agglutination titers below 1:80 are considered clinically non-significant."
            ),
            (
                "Malaria Parasite", 30000.00,
                "Microscopic blood smear / RDT for Plasmodium detection.",
                [
                    {"name": "RDT Result", "unit": "Qualitative", "range": "Negative", "default": "Negative"},
                    {"name": "Microscopy Smear", "unit": "Visual", "range": "No Parasite Seen", "default": "No Parasite Seen"},
                    {"name": "Parasite Density", "unit": "parasites/uL", "range": "0", "default": "0"}
                ],
                "Giemsa-stained thick and thin blood films examined under 100x oil immersion."
            ),
            (
                "Blood Sugar", 35000.00,
                "Fasting or Random Blood Glucose estimation.",
                [
                    {"name": "Fasting Blood Glucose", "unit": "mg/dL", "range": "70 - 99", "default": ""},
                    {"name": "Random Blood Glucose", "unit": "mg/dL", "range": "< 140", "default": ""},
                    {"name": "HbA1c", "unit": "%", "range": "4.0 - 5.6", "default": ""}
                ],
                "Enzymatic hexokinase/glucose oxidase method."
            ),
            (
                "HIV Test", 30000.00,
                "Qualitative rapid antibody screening test.",
                [
                    {"name": "HIV 1&2 Rapid Screen", "unit": "Qualitative", "range": "Non-Reactive", "default": "Non-Reactive"},
                    {"name": "Confirmatory Assay", "unit": "Qualitative", "range": "Non-Reactive", "default": "Non-Reactive"}
                ],
                "Client provided pre- and post-test counseling as per national protocol."
            ),
            (
                "Hepatitis B", 35000.00,
                "Hepatitis B Surface Antigen (HBsAg) detection.",
                [
                    {"name": "HBsAg Rapid Test", "unit": "Qualitative", "range": "Negative", "default": "Negative"}
                ],
                "Immunochromatographic assay for qualitative detection of HBsAg."
            ),
            (
                "Pregnancy Test", 20000.00,
                "Urinary human Chorionic Gonadotropin (hCG) qualitative test.",
                [
                    {"name": "Urine hCG", "unit": "Qualitative", "range": "Negative", "default": "Negative"}
                ],
                "Sensitivity: 25 mIU/mL hCG."
            ),
            (
                "Stool Analysis", 25000.00,
                "Macroscopic and microscopic stool examination.",
                [
                    {"name": "Consistency", "unit": "Visual", "range": "Formed", "default": "Formed"},
                    {"name": "Color", "unit": "Visual", "range": "Brown", "default": "Brown"},
                    {"name": "Ova / Parasites", "unit": "Microscopic", "range": "None Seen", "default": "None Seen"},
                    {"name": "Pus Cells", "unit": "/HPF", "range": "0 - 2", "default": "0-1"}
                ],
                "Saline and iodine wet mounts examined microscopically."
            ),
            (
                "Liver Function Test", 90000.00,
                "Comprehensive hepatic enzyme and bilirubin profile.",
                [
                    {"name": "ALT (SGPT)", "unit": "U/L", "range": "7 - 56", "default": ""},
                    {"name": "AST (SGOT)", "unit": "U/L", "range": "10 - 40", "default": ""},
                    {"name": "ALP", "unit": "U/L", "range": "44 - 147", "default": ""},
                    {"name": "Total Bilirubin", "unit": "mg/dL", "range": "0.1 - 1.2", "default": ""},
                    {"name": "Direct Bilirubin", "unit": "mg/dL", "range": "0.0 - 0.3", "default": ""},
                    {"name": "Total Protein", "unit": "g/dL", "range": "6.0 - 8.3", "default": ""},
                    {"name": "Albumin", "unit": "g/dL", "range": "3.5 - 5.0", "default": ""}
                ],
                "Automated spectrophotometric analyzer."
            ),
            (
                "Kidney Function Test", 85000.00,
                "Renal function biochemical profile.",
                [
                    {"name": "Serum Creatinine", "unit": "mg/dL", "range": "0.6 - 1.2", "default": ""},
                    {"name": "Blood Urea Nitrogen (BUN)", "unit": "mg/dL", "range": "7 - 20", "default": ""},
                    {"name": "Uric Acid", "unit": "mg/dL", "range": "3.5 - 7.2", "default": ""},
                    {"name": "Sodium (Na+)", "unit": "mmol/L", "range": "135 - 145", "default": ""},
                    {"name": "Potassium (K+)", "unit": "mmol/L", "range": "3.5 - 5.0", "default": ""}
                ],
                "Biochemical ion-selective electrode / colorimetric assay."
            )
        ]

        for t_name, price, desc, fields, default_comment in lab_tests_data:
            cursor.execute("SELECT TestID FROM Laboratory_Tests WHERE LOWER(TestName) = LOWER(%s)", (t_name,))
            res = cursor.fetchone()
            if res:
                test_id = res[0]
            else:
                cursor.execute("INSERT INTO Laboratory_Tests (TestName, Price) VALUES (%s, %s)", (t_name, price))
                test_id = cursor.lastrowid

            # Check if template already exists
            cursor.execute("SELECT TemplateID FROM laboratory_templates WHERE TestID = %s", (test_id,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO laboratory_templates (
                        TestID, TemplateName, TemplateDescription, TemplateFields, 
                        ReferenceRanges, MeasurementUnits, DefaultComments, Status, CreatedBy
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active', 1)
                """, (
                    test_id,
                    f"{t_name} Standard Template",
                    desc,
                    json.dumps(fields),
                    json.dumps({f["name"]: f["range"] for f in fields}),
                    json.dumps({f["name"]: f["unit"] for f in fields}),
                    default_comment
                ))

        conn.commit()
        conn.close()
        print("✅ Safe Laboratory Templates migration complete!")
    except Exception as e:
        print(f"Migration Notice: {e}")

if __name__ == "__main__":
    ensure_lab_templates_table()
