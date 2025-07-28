import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.cursor import MySQLCursor
from config import DB_CONFIG
from typing import Optional, Union


# Define a type alias for the connection object
DBConnection = Union[MySQLConnection, PooledMySQLConnection]



def create_connection() -> Optional[DBConnection]:
    """Establishes a connection to the MySQL database."""
    # Check if all required environment variables are set
    for key, value in DB_CONFIG.items():
        if value is None:
            print(f"Error: Environment variable '{key}' is not set.")
            return None
    try:
        # Cast values to str since we've checked for None
        connection: DBConnection = mysql.connector.connect(
            host=DB_CONFIG['host'] or '',
            user=DB_CONFIG['user'] or '',
            password=DB_CONFIG['password'] or '',
            database=DB_CONFIG['database'] or ''
        )
        print("Database connection successful.")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def create_tables() -> None:
    """Creates the vehicle, customer, and rental_order tables if they don't exist."""
    vehicle_table: str = (
        """
        CREATE TABLE IF NOT EXISTS vehicle (
            id INT AUTO_INCREMENT PRIMARY KEY,
            manufacturer VARCHAR(50) NOT NULL,
            model VARCHAR(50) NOT NULL,
            type ENUM('Sedan', 'SUV', 'VAN') NOT NULL DEFAULT 'Sedan',
            year INT NOT NULL,
            license_plate VARCHAR(20) UNIQUE,
            daily_rate DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
            is_available BOOLEAN NOT NULL DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    customer_table: str = (
        """
        CREATE TABLE IF NOT EXISTS customer (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            address VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(100),
            zip_code VARCHAR(10),
            contact_channel ENUM('email', 'sms', 'whatsapp') NOT NULL DEFAULT 'email',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    rental_order_table: str = (
        """
        CREATE TABLE IF NOT EXISTS rental_order (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            vehicle_id INT NOT NULL,
            pick_up_date DATE NOT NULL,
            return_date DATE NOT NULL,
            total_amount DECIMAL(10, 2) NOT NULL,
            status ENUM('pending', 'confirmed', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE,
            FOREIGN KEY (vehicle_id) REFERENCES vehicle(id) ON DELETE CASCADE,
            CONSTRAINT chk_max_days_rental CHECK (DATEDIFF(return_date, pick_up_date) <= 7),
            CONSTRAINT chk_max_reserve_days CHECK (DATEDIFF(pick_up_date, DATE(created_at)) <= 7)
        );
        """
    )
        
    connection: Optional[DBConnection] = create_connection()
    if connection is None:
        print("Cannot create tables without a database connection. Exiting.")
        return

    cursor: Optional[MySQLCursor] = None
    try:
        cursor = connection.cursor()
        print("\nAttempting to create tables...")
        cursor.execute(vehicle_table)
        print("Table 'vehicle' processed.")
        cursor.execute(customer_table)
        print("Table 'customer' processed.")
        cursor.execute(rental_order_table)
        print("Table 'rental_order' processed.")
        connection.commit()
        print("\nAll tables processed successfully.")
    except mysql.connector.Error as err:
        print(f"Error at table creation: {err}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Database connection closed.")


def populate_tables() -> None:    
    connection: Optional[DBConnection] = create_connection()
    if connection is None:
        print("Cannot create tables without a database connection. Exiting.")
        return

    cursor: Optional[MySQLCursor] = None
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM vehicle")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO vehicle (manufacturer, model, type, year, license_plate, daily_rate, is_available) VALUES ('Toyota', 'Camry', 'Sedan', 2022, 'ABC-1234', 45.00, TRUE);")
            cursor.execute("INSERT INTO vehicle (manufacturer, model, type, year, license_plate, daily_rate, is_available) VALUES ('Honda', 'CR-V', 'SUV', 2023, 'XYZ-5678', 60.50, TRUE);")
            connection.commit()
            print("Database initialized with sample data.")
        else:
            print("Database already contains data. Skipping initialization.")

        cursor.execute("SELECT COUNT(*) FROM customer")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
            INSERT INTO customer (first_name, last_name, email, phone, address, city, state, zip_code, contact_channel) VALUES
            ('Alice', 'Smith', 'alice.smith@example.com', '555-123-4567', '123 Oak Avenue', 'Springfield', 'IL', '62704', 'email');
            """)
            cursor.execute("""
            INSERT INTO customer (first_name, last_name, email, phone, address, city, state, zip_code, contact_channel) VALUES
            ('Bob', 'Johnson', 'bob.johnson@example.net', '555-987-6543', '45 Pine Street', 'Rivertown', 'NY', '10001', 'sms');
            """)
            cursor.execute("""
            INSERT INTO customer (first_name, last_name, email, phone, address, city, state, zip_code, contact_channel) VALUES
            ('Charlie', 'Brown', 'charlie.brown@example.org', '555-555-1212', '789 Maple Lane', 'Centerville', 'CA', '90210', 'whatsapp');
            """)
            cursor.execute("""
            INSERT INTO customer (first_name, last_name, email, phone, address, city, state, zip_code, contact_channel) VALUES
            ('Diana', 'Miller', 'diana.miller@example.co', '555-222-3333', '10 Elm Road', 'Pleasantville', 'TX', '75001', 'email');
            """)
            
            connection.commit()
            print("Database initialized with sample data.")
        else:
            print("Database already contains data. Skipping initialization.")

        cursor.execute("SELECT COUNT(*) FROM rental_order")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO rental_order (customer_id, vehicle_id, pick_up_date, return_date, total_amount, status) VALUES (1, 1, '2025-07-25', '2025-07-27', 180.00, 'confirmed');")
            cursor.execute("INSERT INTO rental_order (customer_id, vehicle_id, pick_up_date, return_date, total_amount, status) VALUES (2, 2, '2025-07-26', '2025-08-01', 121.00, 'pending');")
            connection.commit()
            print("Database initialized with sample data.")
        else:
            print("Database already contains data. Skipping initialization.")

    except mysql.connector.Error as err:
        print(f"Error at table creation: {err}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("Database connection closed.")


if __name__ == "__main__":
    create_tables()
    populate_tables()

# https://g.co/gemini/share/d743c721e7c5