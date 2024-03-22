import psycopg2
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Database connection parameters
db_params = {
    "dbname": "xxxxxx",
    "user": "xxxxxxx",
    "password": "xxxxxxx",
    "host": "xxxxxxxxx"
}

def fetch_data(db_params, query):
    """Fetch data from the PostgreSQL database."""
    with psycopg2.connect(**db_params) as conn:
        df = pd.read_sql_query(query, conn)
    return df

def preprocess_data(df):
    """Standardize the data."""
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)
    return df_scaled

def apply_clustering(df_scaled, n_clusters=5):
    """Apply K-means clustering and return cluster labels."""
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)  #random_state=42 use as seed value so that everytime we generarte vector , it is same.
    labels = kmeans.fit_predict(df_scaled)
    return labels, kmeans.cluster_centers_

def main(db_params):
    # SQL query to fetch relevant data
    query = """
    SELECT age, income, spending,target_savings_goal,risk_tolerance
    FROM customer_profiles_fin;
    """
    
    # Fetch and preprocess data
    df = fetch_data(db_params, query)
    df_scaled = preprocess_data(df)
    
    # Apply clustering
    n_clusters = 5 # becuase we have 5 dimension.
    labels, centroids = apply_clustering(df_scaled, n_clusters)
    
    # Determine the largest cluster
    largest_cluster_label = pd.Series(labels).mode()[0]
    
    # Reference embedding: Centroid of the largest cluster
    reference_embedding = centroids[largest_cluster_label]
    
    print("Reference Embedding (Centroid of Largest Cluster):", reference_embedding)

if __name__ == "__main__":
    main(db_params)

