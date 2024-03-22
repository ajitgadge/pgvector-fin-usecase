from sqlalchemy import create_engine
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
from sqlalchemy import text

# Use sqlalchemy as pandas works better with this connector

# Database connection parameters
db_url = "postgresql+psycopg2://xxxx:xxxxxx@xxxxx/xxxxx"
engine = create_engine(db_url)

# Batch size for processing and updating
batch_size = 100

def fetch_data(engine):
    query = "SELECT customer_id, age, income, spending, target_savings_goal,risk_tolerance FROM customer_profiles_fin"
    return pd.read_sql_query(query, engine)

def apply_pca(data):
    features = data[['age', 'income', 'spending', 'target_savings_goal','risk_tolerance']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    pca = PCA(n_components=5)  # Choosing 5 dimensions for embeddings as i only have 5 dimention numeric data.
    embeddings = pca.fit_transform(features_scaled) #Use PCA for embedding as it is better for shorter dimension
    return embeddings

def update_embeddings(engine, data, embeddings):
    # Use SQLAlchemy's text() to prepare the raw SQL query
    update_stmt = text("""
    UPDATE customer_profiles_fin SET embeddings = :embedding WHERE customer_id = :customer_id
    """)

    with engine.begin() as conn:  # Begin a new transaction
        for index, row in data.iterrows():
            # Convert the numpy array to list for embedding and ensure customer_id is an int
            embedding_list = embeddings[index].tolist()
            # Execute the SQL command, passing the parameters as a dictionary
            conn.execute(update_stmt, {'embedding': embedding_list, 'customer_id': int(row['customer_id'])})
            print(f"Progres Of Batch...{index}")
            print (f"Embedding...{embedding_list}")

def main():
    # Fetch the data
    data = fetch_data(engine)
    
    # Apply PCA to generate embeddings
    embeddings = apply_pca(data)
    #print(f"Engine ...{engine}")
    # Update the database with embeddings
    update_embeddings(engine, data, embeddings)
    print("Embeddings updated successfully.")

if __name__ == "__main__":
    main()

