from fastapi import FastAPI, Request
import requests
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppress most TensorFlow logs

app = FastAPI(title="Retriever Agent")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize FAISS index
embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
index = faiss.IndexFlatL2(embedding_dim)
stored_articles = []

@app.get("/")
def root():
    return {"message": "Retriever Agent is running"}

@app.get("/index_articles")
def index_articles():
    # Fetch articles from scraping agent
    response = requests.get("http://localhost:8002/scrape_market_news")
    articles = response.json()["articles"]

    texts = [article["title"] + ". " + article["link"] for article in articles]
    embeddings = model.encode(texts)

    index.add(np.array(embeddings).astype("float32"))
    stored_articles.extend(articles)

    return {"message": f"Indexed {len(articles)} articles."}

@app.get("/query")
def query_articles(q: str):
    query_embedding = model.encode([q])
    D, I = index.search(np.array(query_embedding).astype("float32"), k=3)

    results = [stored_articles[i] for i in I[0] if i < len(stored_articles)]
    return {"query": q, "results": results}
