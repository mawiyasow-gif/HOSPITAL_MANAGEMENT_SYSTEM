import mysql.connector

def connect_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="Alhaji",
        password="123456789",
        database="Pysical_Health_Clinic_DB"
    )
    return conn