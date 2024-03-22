from flask import Flask, send_file
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import io
import ast

app = Flask(__name__)

DATABASE_URI = 'postgresql+psycopg2://xxxx:xxxx@xxxxx/xxxxx'
engine = create_engine(DATABASE_URI)

def fetch_embeddings():
    query = "SELECT embeddings FROM customer_profiles_fin;"
    df = pd.read_sql_query(query, engine)
    # Assuming embeddings are stored as text and represent lists
    df['embeddings'] = df['embeddings'].apply(lambda x: np.array(ast.literal_eval(x), dtype=np.float32))
    return df['embeddings']

def generate_5d_plot(embeddings):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Use the first 3 dimensions for the axes
    xs = embeddings.apply(lambda x: x[0])
    ys = embeddings.apply(lambda x: x[1])
    zs = embeddings.apply(lambda x: x[2])
    # Use the 4th dimension for color
    color = embeddings.apply(lambda x: x[3])
    # Use the 5th dimension for size
    size = embeddings.apply(lambda x: x[4])*20  # Scale factor for better visualization

    sc = ax.scatter(xs, ys, zs, c=color, s=size, cmap='viridis', alpha=0.5)
    
    # Color bar
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label('Target Saving Goal')

    # Labels
    ax.set_xlabel('Age')
    ax.set_ylabel('Income')
    ax.set_zlabel('Spending')
    ax.set_title('5D Visualization: Age, Income, Spending, Target Saving Goal(Color), Risk Tolerance (DOT Size) ')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf

@app.route('/plot5d')
def plot_5d_embeddings():
    embeddings = fetch_embeddings()
    buf = generate_5d_plot(embeddings)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

