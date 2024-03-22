import numpy as np
import psycopg2
from scipy.spatial.distance import cosine
from psycopg2.extras import execute_batch
import ast

# Database connection parameters
db_params = {
    "dbname": "xxxxx",
    "user": "xxxxx",
    "password": "xxxxx",
    "host": "xxxxxxx"
}

def calculate_cosine_similarity(vec_a, vec_b):
    """Ensure both vectors are 1-D numpy arrays of the same dimension and calculate cosine/Euclidean similarity."""
    vec_a = np.asarray(vec_a).reshape(-1)
    vec_b = np.asarray(vec_b).reshape(-1)
    if vec_a.shape != vec_b.shape:
        raise ValueError("Vectors must be 1-D and of the same dimension.")
    return 1 - cosine(vec_a, vec_b)

def fetch_embeddings(db_params, batch_size):
    """Fetch embeddings from the database in batches, ensuring they're 1-D numpy arrays."""
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT customer_id, embeddings FROM customer_profiles_fin;")
            while True:
                records = cur.fetchmany(batch_size)
                if not records:
                    break
                for record in records:
                    customer_id, embedding_str = record
                    # Convert string representation to numpy array, ensuring 1-D
                    embedding = np.array(ast.literal_eval(embedding_str), dtype=np.float32).reshape(-1)
                    if embedding.size != 5:
                        raise ValueError(f"Embedding for customer {customer_id} is not the correct size.")
                    yield customer_id, embedding

def update_customer_ranks(db_params, customer_ranks, batch_size):
    """Update the customer_rank column for each customer based on their calculated ranks."""
    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            query = "UPDATE customer_profiles_fin SET customer_rank_d = %s WHERE customer_id = %s;"
            batch_data = [(rank, customer_id) for customer_id, rank in customer_ranks.items()]
            for i in range(0, len(batch_data), batch_size):
                execute_batch(cur, query, batch_data[i:i+batch_size])
            conn.commit()

def main(reference_embedding, db_params, batch_size=100):
    reference_vec = np.array(reference_embedding, dtype=np.float32).reshape(-1)
    similarities = {}
    
    for customer_id, embedding in fetch_embeddings(db_params, batch_size):
        similarity = calculate_cosine_similarity(embedding, reference_vec)
        similarities[customer_id] = similarity
    
    # Sort customers by similarity and divide into 5 ranks. So ensuring that five division is similar and ranking assigne not random.
    sorted_customers = sorted(similarities, key=similarities.get, reverse=True)
    ranks = {customer_id: (i * 5 // len(sorted_customers)) + 1 for i, customer_id in enumerate(sorted_customers)}
    
    update_customer_ranks(db_params, ranks, batch_size)
    print("Database updated with customer ranks based on embedding similarity.")

if __name__ == "__main__":
    reference_embedding = [0.96604658,-0.18275761,0.05158507,-0.16845284,-0.89131986] # This is calculated by K-mean by referance embedding. One can assign multiple embedding depends upon the simiularity that they like.
    main(reference_embedding, db_params)

