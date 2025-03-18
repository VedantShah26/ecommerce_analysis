import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration parameters
KMEANS_N_CLUSTERS = 5  # Number of customer segments to create
DBSCAN_EPS = 0.5      # Maximum distance between samples to be considered neighbors
DBSCAN_MIN_SAMPLES = 5  # Minimum number of samples in a neighborhood to form a cluster

def get_customer_features(connection):
    """Extract customer features from database."""
    query = """
    SELECT 
        customer_id,
        COUNT(DISTINCT transaction_id) as transaction_count,
        SUM(total_amount) as total_spent,
        AVG(total_amount) as avg_transaction_value,
        MAX(transaction_date) as last_purchase_date,
        COUNT(DISTINCT product_category) as unique_categories
    FROM transactions
    GROUP BY customer_id
    """
    
    df = pd.read_sql(query, connection)
    return df

def prepare_features(df):
    """Prepare features for clustering."""
    # Calculate days since last purchase
    df['days_since_last_purchase'] = (pd.Timestamp.now() - pd.to_datetime(df['last_purchase_date'])).dt.days
    
    # Select features for clustering
    features = ['transaction_count', 'total_spent', 'avg_transaction_value', 
                'days_since_last_purchase', 'unique_categories']
    
    # Scale features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[features])
    
    return scaled_features, features

def perform_kmeans_clustering(scaled_features, n_clusters=KMEANS_N_CLUSTERS):
    """Perform K-means clustering.
    
    Parameters:
    -----------
    scaled_features : array-like
        Scaled feature matrix
    n_clusters : int, default=5
        Number of clusters to form. This determines the number of customer segments.
        A value of 5 is recommended for e-commerce analysis as it provides a good
        balance between granularity and interpretability.
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans_labels = kmeans.fit_predict(scaled_features)
    
    # Calculate clustering metrics
    silhouette = silhouette_score(scaled_features, kmeans_labels)
    calinski = calinski_harabasz_score(scaled_features, kmeans_labels)
    
    return kmeans_labels, silhouette, calinski

def perform_dbscan_clustering(scaled_features, eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES):
    """Perform DBSCAN clustering.
    
    Parameters:
    -----------
    scaled_features : array-like
        Scaled feature matrix
    eps : float, default=0.5
        The maximum distance between two samples for them to be considered
        as in the same neighborhood. A smaller value will create more clusters
        but might miss some patterns.
    min_samples : int, default=5
        The number of samples in a neighborhood for a point to be considered
        as a core point. A higher value will make the clustering more strict
        and might identify more noise points.
    """
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    dbscan_labels = dbscan.fit_predict(scaled_features)
    
    # Calculate clustering metrics (excluding noise points)
    mask = dbscan_labels != -1
    if sum(mask) > 1:  # Need at least 2 clusters for metrics
        silhouette = silhouette_score(scaled_features[mask], dbscan_labels[mask])
        calinski = calinski_harabasz_score(scaled_features[mask], dbscan_labels[mask])
    else:
        silhouette = calinski = 0
    
    return dbscan_labels, silhouette, calinski

def save_segments_to_database(df, kmeans_labels, dbscan_labels, connection):
    """Save clustering results to database."""
    cursor = connection.cursor()
    
    for idx, row in df.iterrows():
        # Determine segment name based on cluster characteristics
        kmeans_segment = f"KMeans_Segment_{kmeans_labels[idx]}"
        dbscan_segment = f"DBSCAN_Segment_{dbscan_labels[idx]}" if dbscan_labels[idx] != -1 else "Noise"
        
        sql = """INSERT INTO customer_segments 
                (customer_id, segment_name, cluster_id)
                VALUES (%s, %s, %s)"""
        
        # Save K-means segment
        cursor.execute(sql, (row['customer_id'], kmeans_segment, int(kmeans_labels[idx])))
        
        # Save DBSCAN segment
        cursor.execute(sql, (row['customer_id'], dbscan_segment, int(dbscan_labels[idx])))
    
    connection.commit()
    cursor.close()

def analyze_segments(df, labels, algorithm_name):
    """Analyze and print segment characteristics."""
    df['cluster'] = labels
    
    print(f"\n{algorithm_name} Clustering Results:")
    print("-" * 50)
    
    for cluster in np.unique(labels):
        if cluster == -1 and algorithm_name == "DBSCAN":
            print("\nNoise Points:")
        else:
            print(f"\nCluster {cluster}:")
        
        cluster_data = df[df['cluster'] == cluster]
        print(f"Number of customers: {len(cluster_data)}")
        print(f"Average transaction count: {cluster_data['transaction_count'].mean():.2f}")
        print(f"Average total spent: ${cluster_data['total_spent'].mean():.2f}")
        print(f"Average days since last purchase: {cluster_data['days_since_last_purchase'].mean():.2f}")
        print(f"Average unique categories: {cluster_data['unique_categories'].mean():.2f}")

def main():
    # Create database connection
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'ecommerce_analysis')
    )
    
    # Get customer features
    df = get_customer_features(connection)
    
    # Prepare features for clustering
    scaled_features, features = prepare_features(df)
    
    # Perform K-means clustering
    kmeans_labels, kmeans_silhouette, kmeans_calinski = perform_kmeans_clustering(scaled_features)
    analyze_segments(df, kmeans_labels, "K-means")
    
    # Perform DBSCAN clustering
    dbscan_labels, dbscan_silhouette, dbscan_calinski = perform_dbscan_clustering(scaled_features)
    analyze_segments(df, dbscan_labels, "DBSCAN")
    
    # Save results to database
    save_segments_to_database(df, kmeans_labels, dbscan_labels, connection)
    
    # Print clustering metrics
    print("\nClustering Metrics:")
    print("-" * 50)
    print("K-means:")
    print(f"Silhouette Score: {kmeans_silhouette:.4f}")
    print(f"Calinski-Harabasz Score: {kmeans_calinski:.4f}")
    print("\nDBSCAN:")
    print(f"Silhouette Score: {dbscan_silhouette:.4f}")
    print(f"Calinski-Harabasz Score: {dbscan_calinski:.4f}")
    
    connection.close()
    print("\nCustomer segmentation completed successfully!")

if __name__ == "__main__":
    main() 