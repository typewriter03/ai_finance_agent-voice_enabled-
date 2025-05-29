from fastapi import FastAPI
import requests

app = FastAPI(title="Scraper Agent")

API_KEY = "pub_451de9a74536487398c781a1d8649aa7"

@app.get("/")
def root():
    return {"message": "Scraper Agent is running"}

@app.get("/scrape_market_news")
def scrape_market_news():
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q=stock%20market&language=en&category=business"
    response = requests.get(url)
    data = response.json()

    articles = []
    for item in data.get("results", [])[:5]:
        articles.append({
            "title": item.get("title"),
            "link": item.get("link")
        })

    return {"articles": articles}
