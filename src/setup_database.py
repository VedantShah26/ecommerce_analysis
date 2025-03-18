import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_database(connection):
    """Create the database if it doesn't exist."""
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'ecommerce_analysis')}")
        print(f"Database {os.getenv('DB_NAME', 'ecommerce_analysis')} created successfully")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
    finally:
        cursor.close()

def create_tables(connection):
    """Create all necessary tables."""
    cursor = connection.cursor()
    
    # First, create the transactions table with all necessary indexes
    transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id VARCHAR(50) PRIMARY KEY,
        customer_id VARCHAR(50),
        transaction_date DATETIME,
        product_id VARCHAR(50),
        product_category VARCHAR(100),
        quantity INT,
        unit_price DECIMAL(10,2),
        total_amount DECIMAL(10,2),
        country VARCHAR(100),
        payment_method VARCHAR(50),
        customer_age INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_customer_id (customer_id),
        INDEX idx_transaction_date (transaction_date),
        INDEX idx_product_category (product_category),
        INDEX idx_country (country)
    )
    """
    
    # Create customer_segments table with foreign key
    customer_segments_table = """
    CREATE TABLE IF NOT EXISTS customer_segments (
        customer_id VARCHAR(50),
        segment_name VARCHAR(50),
        rfm_score INT,
        cluster_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (customer_id),
        CONSTRAINT fk_customer_id FOREIGN KEY (customer_id) 
            REFERENCES transactions(customer_id) 
            ON DELETE CASCADE 
            ON UPDATE CASCADE
    )
    """
    
    # Create product_recommendations table
    product_recommendations_table = """
    CREATE TABLE IF NOT EXISTS product_recommendations (
        product_id VARCHAR(50),
        recommended_product_id VARCHAR(50),
        confidence_score DECIMAL(5,2),
        support_score DECIMAL(5,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (product_id, recommended_product_id)
    )
    """
    
    # Create predictive_models table
    predictive_models_table = """
    CREATE TABLE IF NOT EXISTS predictive_models (
        model_id INT AUTO_INCREMENT PRIMARY KEY,
        model_name VARCHAR(100),
        model_type VARCHAR(50),
        accuracy_score DECIMAL(5,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    try:
        # Drop existing tables in reverse order to handle foreign key constraints
        cursor.execute("DROP TABLE IF EXISTS customer_segments")
        cursor.execute("DROP TABLE IF EXISTS product_recommendations")
        cursor.execute("DROP TABLE IF EXISTS predictive_models")
        cursor.execute("DROP TABLE IF EXISTS transactions")
        
        # Create tables in correct order
        cursor.execute(transactions_table)
        cursor.execute(customer_segments_table)
        cursor.execute(product_recommendations_table)
        cursor.execute(predictive_models_table)
        
        connection.commit()
        print("Tables and indexes created successfully")
        
    except mysql.connector.Error as err:
        print(f"Error creating tables: {err}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    # Create connection to MySQL server (without database)
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '')
    )
    
    try:
        # Create database
        create_database(connection)
        
        # Close the initial connection
        connection.close()
        
        # Create new connection to the created database
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'ecommerce_analysis')
        )
        
        # Create tables
        create_tables(connection)
        
        print("\nDatabase setup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error during database setup: {err}")
    
    finally:
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    main() 