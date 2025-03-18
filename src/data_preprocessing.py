import pandas as pd
import numpy as np
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def load_data(file_path):
    """Load the e-commerce transactions dataset."""
    try:
        # Try the provided path first
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
        # Try in data directory
        elif os.path.exists(os.path.join('data', file_path)):
            df = pd.read_csv(os.path.join('data', file_path))
        # Try in root directory
        else:
            root_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_path)
            df = pd.read_csv(root_path)
        
        # Print column names for debugging
        print("\nAvailable columns in the dataset:")
        print(df.columns.tolist())
        print("\nFirst few rows of the dataset:")
        print(df.head())
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

def clean_data(df):
    """Clean and preprocess the data."""
    # Convert transaction date to datetime
    df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
    
    # Handle missing values
    df['Age'] = df['Age'].fillna(df['Age'].median())
    df['Country'] = df['Country'].fillna('Unknown')
    df['Payment_Method'] = df['Payment_Method'].fillna('Unknown')
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Remove outliers in numerical columns
    Q1 = df['Purchase_Amount'].quantile(0.25)
    Q3 = df['Purchase_Amount'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df['Purchase_Amount'] < (Q1 - 1.5 * IQR)) | (df['Purchase_Amount'] > (Q3 + 1.5 * IQR)))]
    
    return df

def create_database_connection():
    """Create connection to MySQL database."""
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'ecommerce_analysis')
    )
    return connection

def load_to_database(df, connection):
    """Load processed data into MySQL database."""
    cursor = connection.cursor()
    
    # Prepare data for insertion
    for _, row in df.iterrows():
        # Map the data to match our database schema
        values = (
            row['Transaction_ID'],  # transaction_id
            row['Transaction_ID'],  # customer_id (using Transaction_ID as customer_id since we don't have a separate customer_id)
            row['Transaction_Date'],  # transaction_date
            row['Transaction_ID'],  # product_id (using Transaction_ID as product_id since we don't have a separate product_id)
            row['Product_Category'],  # product_category
            1,  # quantity (default to 1 since we don't have quantity in the data)
            row['Purchase_Amount'],  # unit_price (using Purchase_Amount as unit_price)
            row['Purchase_Amount'],  # total_amount (using Purchase_Amount as total_amount)
            row['Country'],  # country
            row['Payment_Method'],  # payment_method
            row['Age']  # customer_age
        )
        
        sql = """INSERT INTO transactions 
                (transaction_id, customer_id, transaction_date, product_id, 
                product_category, quantity, unit_price, total_amount, 
                country, payment_method, customer_age)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        try:
            cursor.execute(sql, values)
        except Exception as e:
            print(f"Error inserting row: {e}")
            print(f"Values: {values}")
            raise
    
    connection.commit()
    cursor.close()

def main():
    try:
        # Load data
        print("Loading data...")
        df = load_data('ecommerce_transactions.csv')
        
        # Clean data
        print("Cleaning data...")
        df_cleaned = clean_data(df)
        
        # Create database connection
        print("Connecting to database...")
        connection = create_database_connection()
        
        # Load data to database
        print("Loading data to database...")
        load_to_database(df_cleaned, connection)
        
        # Close connection
        connection.close()
        
        print("Data preprocessing completed successfully!")
        
    except Exception as e:
        print(f"Error during data preprocessing: {e}")
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    main() 