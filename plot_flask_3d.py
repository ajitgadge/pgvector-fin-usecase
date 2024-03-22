from flask import Flask, send_file
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for Matplotlib
from mpl_toolkits.mplot3d import Axes3D  # Import the 3D plotting toolkit
import matplotlib.pyplot as plt
import io
import ast

app = Flask(__name__)

DATABASE_URI = 'postgresql+psycopg2://xxxxx:xxxx@xxxxx/xxxxx'
engine = create_engine(DATABASE_URI)

def fetch_embeddings():
    query = "SELECT embeddings FROM customer_profiles_fin;"
    df = pd.read_sql_query(query, engine)
    # Convert string representations of lists to numpy arrays
    df['embeddings'] = df['embeddings'].apply(lambda x: np.array(ast.literal_eval(x), dtype=np.float32))
    embeddings = np.stack(df['embeddings'].values)
    return embeddings

def reduce_dimensions(embeddings, n_components=3):
    """Reduce dimensions to 3 for 3D plotting."""
    pca = PCA(n_components=n_components)
    reduced_data = pca.fit_transform(embeddings)
    return reduced_data

def generate_plot(reduced_data):
    """Generate a 3D scatter plot of the reduced embeddings."""
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(reduced_data[:, 0], reduced_data[:, 1], reduced_data[:, 2], alpha=0.6)
    ax.set_title('3D Visualization of Embeddings')
    ax.set_xlabel('Component 1')
    ax.set_ylabel('Component 2')
    ax.set_zlabel('Component 3')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf

@app.route('/plot3d')
def plot_embeddings():
    embeddings = fetch_embeddings()
    reduced_data = reduce_dimensions(embeddings)
    buf = generate_plot(reduced_data)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

