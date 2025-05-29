from fastapi import FastAPI
from pydantic import BaseModel
import yfinance as yf
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="API Agent - Market Data")

class StockRequest(BaseModel):
    symbols: list[str]  # e.g. ["TSM", "AAPL", "INFY"]

@app.get("/")
def root():
    return {"message": "API Agent is running"}

@app.post("/get_stock_data")
def get_stock_data(request: StockRequest):
    result = []
    for symbol in request.symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) < 2:
                continue
            today = hist.iloc[-1]
            yesterday = hist.iloc[-2]

            change_pct = ((today["Close"] - yesterday["Close"]) / yesterday["Close"]) * 100

            result.append({
                "symbol": symbol,
                "current_price": round(today["Close"], 2),
                "previous_close": round(yesterday["Close"], 2),
                "change_pct": round(change_pct, 2)
            })
        except Exception as e:
            result.append({"symbol": symbol, "error": str(e)})
    return {"stocks": result}

@app.get("/top_gainers")
def top_gainers():
    url = "https://finance.yahoo.com/gainers"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    gainers = []
    rows = soup.select("table tbody tr")[:5]  # Top 5 gainers
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            symbol = cols[0].text.strip()
            gainers.append(symbol)

    return get_stock_data(StockRequest(symbols=gainers))
