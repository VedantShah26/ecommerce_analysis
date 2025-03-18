import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_database_connection():
    """Create connection to MySQL database."""
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'ecommerce_analysis')
    )
    return connection

def get_transaction_data(connection):
    """Get transaction data for analysis."""
    query = """
    SELECT 
        customer_id,
        transaction_date,
        total_amount,
        product_category,
        country,
        payment_method
    FROM transactions
    """
    return pd.read_sql(query, connection)

def analyze_customer_behavior(df):
    """Analyze and visualize customer behavior."""
    # Create visualizations directory if it doesn't exist
    if not os.path.exists('visualizations'):
        os.makedirs('visualizations')
    
    # 1. Purchase Amount Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='total_amount', bins=50)
    plt.title('Distribution of Purchase Amounts')
    plt.xlabel('Purchase Amount')
    plt.ylabel('Count')
    plt.savefig('visualizations/purchase_distribution.png')
    plt.close()
    
    # 2. Payment Method Distribution
    plt.figure(figsize=(10, 6))
    payment_counts = df['payment_method'].value_counts()
    plt.pie(payment_counts, labels=payment_counts.index, autopct='%1.1f%%')
    plt.title('Distribution of Payment Methods')
    plt.savefig('visualizations/payment_methods.png')
    plt.close()
    
    # 3. Product Category Analysis
    plt.figure(figsize=(12, 6))
    category_counts = df['product_category'].value_counts()
    sns.barplot(x=category_counts.values, y=category_counts.index)
    plt.title('Product Category Distribution')
    plt.xlabel('Number of Transactions')
    plt.savefig('visualizations/product_categories.png')
    plt.close()
    
    # 4. Customer Purchase Frequency
    customer_frequency = df.groupby('customer_id').size()
    plt.figure(figsize=(10, 6))
    sns.histplot(customer_frequency, bins=30)
    plt.title('Customer Purchase Frequency')
    plt.xlabel('Number of Purchases')
    plt.ylabel('Number of Customers')
    plt.savefig('visualizations/purchase_frequency.png')
    plt.close()
    
    # 5. Geographic Distribution
    plt.figure(figsize=(12, 6))
    country_counts = df['country'].value_counts()
    sns.barplot(x=country_counts.values, y=country_counts.index)
    plt.title('Geographic Distribution of Sales')
    plt.xlabel('Number of Transactions')
    plt.savefig('visualizations/geographic_distribution.png')
    plt.close()
    
    # 6. Time Series Analysis
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    daily_sales = df.groupby('transaction_date')['total_amount'].sum().reset_index()
    plt.figure(figsize=(15, 6))
    plt.plot(daily_sales['transaction_date'], daily_sales['total_amount'])
    plt.title('Daily Sales Over Time')
    plt.xlabel('Date')
    plt.ylabel('Total Sales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/daily_sales.png')
    plt.close()

def main():
    try:
        # Create database connection
        print("Connecting to database...")
        connection = create_database_connection()
        
        # Get transaction data
        print("Getting transaction data...")
        df = get_transaction_data(connection)
        
        # Perform analysis
        print("Creating visualizations...")
        analyze_customer_behavior(df)
        
        print("Analysis completed successfully! Check the 'visualizations' folder for results.")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    main() 