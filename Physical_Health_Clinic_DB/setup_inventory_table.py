from database import connect_db

def update_inventory_table():
    """Update the Inventory table to remove TreatmentID column."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Drop foreign key constraint if it exists
        try:
            cursor.execute("ALTER TABLE Inventory DROP FOREIGN KEY inventory_ibfk_1")
            print("✅ Foreign key constraint dropped.")
        except Exception as e:
            print(f"⚠️  No foreign key constraint to drop or error: {e}")
        
        # Remove TreatmentID column if it exists
        try:
            cursor.execute("ALTER TABLE Inventory DROP COLUMN TreatmentID")
            print("✅ TreatmentID column removed.")
        except Exception as e:
            print(f"⚠️  TreatmentID column doesn't exist or error: {e}")
        
        conn.commit()
        
        # Verify the table structure
        cursor.execute("DESCRIBE Inventory")
        columns = cursor.fetchall()
        print("\n📋 Current Inventory table structure:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        conn.close()
        print("\n✅ Inventory table updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating Inventory table: {e}")

if __name__ == "__main__":
    update_inventory_table()
