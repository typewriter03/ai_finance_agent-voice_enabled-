from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Init Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key="AIzaSyAYHaKWloNVe4uUtHzjyZZXi8E9eFVA8R4",
    temperature=0.2
)

def clean_summary(text):
    text = re.sub(r"\s+", " ", text)  # Normalize whitespace
    text = re.sub(r"(?<!\d)(\d{2,})(?!\d)", r"\1", text)  # Basic digit cleanup
    return text.strip()

def extract_stocks_from_query(query: str):
    prompt = f"""
You are a finance assistant. Extract the names or tickers of major public companies mentioned in the following query.
If no companies are mentioned but the query is general (like "top stocks" or "biggest gainers"), return ["top_gainers"].
Return them as a comma-separated list.

Query: "{query}"
Stocks:"""
    try:
        response = llm.invoke(prompt)
        stocks = [s.strip() for s in response.content.split(",") if s.strip()]
        print("📈 Extracted stocks:", stocks)
        return stocks
    except Exception as e:
        print("⚠️ LLM extraction error:", e)
        return []


app = FastAPI(title="Orchestrator Agent")

# --- CONFIG ---
RETRIEVER_URL = "http://localhost:8003"
SCRAPER_URL = "http://localhost:8002"
API_URL = "http://localhost:8001"
LANGUAGE_URL = "http://localhost:8004"
VOICE_URL = "http://localhost:8005"

# --- INPUT MODEL ---
class OrchestratorInput(BaseModel):
    query: str

@app.post("/orchestrate")
def orchestrate(data: OrchestratorInput):
    try:
        query = data.query.strip()
        if not query or len(query.split()) < 7:
            return {"summary": "⚠️ Please ask a more complete question."}

                # Extract stocks from user query via LLM
        stocks = extract_stocks_from_query(data.query)
        print(f"📈 Extracted stocks: {stocks}")

        # 1. Scrape and index
        requests.get(f"{SCRAPER_URL}/scrape_market_news")
        requests.get(f"{RETRIEVER_URL}/index_articles")

        # 2. Retrieve snippets
        retrieved = requests.get(f"{RETRIEVER_URL}/query", params={"q": data.query}).json()["results"]
        retrieved_chunks = [r["title"] for r in retrieved]

                # 3. Fetch stock data
        if stocks and all(s.isalpha() and len(s) <= 5 for s in stocks):
            # If LLM gave valid-looking tickers
            stock_data_resp = requests.post(f"{API_URL}/get_stock_data", json={"symbols": stocks})
        else:
            print("⚠️ No valid stocks extracted. Fetching top gainers...")
            stock_data_resp = requests.get(f"{API_URL}/top_gainers")

        stock_data = stock_data_resp.json().get("stocks", [])



        # 4. Generate market summary
        summary_resp = requests.post(f"{LANGUAGE_URL}/summarize", json={
        "stock_data": stock_data,
        "retrieved_chunks": retrieved_chunks
        })
        summary_data = summary_resp.json().get("summary", {})
        summary = summary_data.get("content", "⚠️ Summary failed.")
        print("✅ Final summary:", summary)



        # 5. Speak summary
        requests.post(f"{VOICE_URL}/speak", json={"text": summary})

        return {
            "query": query,
            "stocks": stocks,
            "retrieved_news": retrieved_chunks,
            "stock_data": stock_data,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Orchestrator is running"}
