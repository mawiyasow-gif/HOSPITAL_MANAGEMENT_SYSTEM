from database import connect_db

def check_and_create_inventory_table():
    """Check if Inventory table exists and create it with proper structure."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Check if Inventory table exists
        cursor.execute("SHOW TABLES LIKE 'Inventory'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("📋 Inventory table exists. Checking structure...")
            cursor.execute("DESCRIBE Inventory")
            columns = cursor.fetchall()
            print("\nCurrent Inventory table structure:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Drop the existing table to recreate with correct structure
            print("\n⚠️  Dropping existing table to recreate with correct structure...")
            cursor.execute("DROP TABLE IF EXISTS Inventory")
            conn.commit()
        else:
            print("📋 Inventory table does not exist. Creating it...")
        
        # Create the Inventory table with correct structure
        create_table_query = """
        CREATE TABLE Inventory (
            InventoryID INT AUTO_INCREMENT PRIMARY KEY,
            ItemName VARCHAR(255) NOT NULL,
            Quantity INT NOT NULL,
            Stock INT NOT NULL,
            UnitPrice DECIMAL(10, 2) NOT NULL,
            ExpiryDate DATE NOT NULL
        )
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        
        # Verify the new table structure
        cursor.execute("DESCRIBE Inventory")
        columns = cursor.fetchall()
        print("\n✅ New Inventory table structure:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        conn.close()
        print("\n✅ Inventory table created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_and_create_inventory_table()
