from flask import Flask, request, render_template_string
import pandas as pd
import boto3
import joblib
import numpy as np

app = Flask(__name__)

s3_client = boto3.client('s3')
bucket_name = "scg-cts2375"

# S3 download
s3_client.download_file(bucket_name, "instacart-model/recommender.pkl", "model.pkl")
s3_client.download_file(bucket_name, "products.csv", "products.csv")

# load the "model" - it is just a dictionary
model = joblib.load("model.pkl")
products_df = pd.read_csv("products.csv")



# Recommends based on product_id - uses cosine similarities
def recommend_products(product_id, top_n=5):

    # Check product exists in index_map - not all products exists
    if product_id not in model["product_index_map"]:
        return [(None, "ERROR: Product ID not found in model", 0.0)]

    item_factors = model["item_factors"]
    idx = model["product_index_map"][product_id]     # lookup index
    item_vec = item_factors[idx]                     # target vector

    # Compute cosine
    norms = np.linalg.norm(item_factors, axis=1) * np.linalg.norm(item_vec)
    similarities = np.dot(item_factors, item_vec) / norms

    #top products - self
    similar_indexes = np.argsort(similarities)[::-1][1:top_n+1]

    results = []
    for i in similar_indexes:
        row = model["products_full"].iloc[i]
        results.append((
            int(row["product_id"]),
            row["product_name"],
            float(similarities[i])
        ))
    return results


def get_product_name(product_id):
    try:
        row = model["products_full"][model["products_full"]["product_id"] == product_id].iloc[0]
        return row["product_name"]
    except:
        return "Unknown Product"



#Flask Stuff
@app.route("/")
def index():
    valid_ids = sorted(model["product_index_map"].keys())[:100]#Show first 100 possible product IDs, just so people know what can be entered
    return render_template_string("""
        <h1>Enter Product ID</h1>
        <form action="/recommend" method="post">
            <label>Product ID:</label>
            <input type="number" name="product_id" required>
            <button type="submit">Get Recommendations</button>
        </form>
        
        <hr>
        <h3> Example valid product IDs:</h3>
        <p>{{ ids }}</p>
        <p><i>(Showing first 100 of {{ total }} available)</i></p>
    """, ids=valid_ids, total=len(model["product_index_map"]))


@app.route("/recommend", methods=["POST"])
def recommend():
    pid = int(request.form["product_id"])

    if pid not in model["product_index_map"]:
        valid_range = f"{min(model['product_index_map'])} - {max(model['product_index_map'])}"
        return render_template_string(f"""
            <h2> Product ID {pid} is not in this model</h2>
            <p>Try an ID between <b>{valid_range}</b></p>
            <a href="/">Back</a>
        """)

    product_name = get_product_name(pid)
    recs = recommend_products(pid, top_n=5)

    return render_template_string("""
        <h2>Top 5 Recommendations for:</h2>
        <h3>{{ pid }} — {{ name }}</h3>  <!-- Shows actual name -->
        <hr>
        <ul>
        {% for r in recs %}
            <li><b>{{ r[1] }}</b> (ID {{ r[0] }} — similarity {{ r[2]|round(3) }})</li>
        {% endfor %}
        </ul>
        <a href="/"> Back</a>
    """, pid=pid, name=product_name, recs=recs)



#Run
if __name__ == "__main__":
    #Runs on port 8
    app.run(host="0.0.0.0", port=80)
