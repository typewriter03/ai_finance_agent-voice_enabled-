# 📘 AI Tool Usage Log

This document contains the prompt engineering strategy, AI tools used, model configurations, and code generation steps for each AI-powered component in the Multi-Agent Financial Assistant project.

---

## 🤖 LLM Usage (Language Agent)

### Tool: `LangChain + Gemini 1.5 Flash`

* **Model**: `models/gemini-1.5-flash`
* **Provider**: Google Generative AI
* **Temperature**: `0.2`

### Prompt Template:

```text
You are a financial assistant. Summarize the market data and news highlights.

Stock Info:
{stock_info}

News Highlights:
{news_info}

Generate a clear, confident morning market brief.
```

### Invocation:

```python
result = llm.invoke(final_prompt)
```

---

## 🧠 LLM Usage (Orchestrator)

### Purpose: Extract stock symbols from user query

* Used a lightweight custom LangChain chain for parsing query

### Sample Prompt:

```text
Extract the names or tickers of any stocks or companies from the following query:

"What's the latest update on Apple and Tesla?"
```

### Output:

```json
["AAPL", "TSLA"]
```

---

## 🧠 Vector Retrieval (Retriever Agent)

### Embeddings Tool: `SentenceTransformer`

* Model: `all-MiniLM-L6-v2`
* Indexing: FAISS (128-dim vectors)

### Steps:

* Scraped news → Chunked text → Embedded → Stored in FAISS index
* Query → Embedded → Top-k vector match using cosine similarity

### Code:

```python
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(dim)
```

---

## 🧏 Voice Agent

### Speech-to-Text (STT): `whisper`

* Model: `base`
* Audio format: WAV

### Text-to-Speech (TTS): `gTTS`

* Language: `en`
* Output format: MP3

### Process:

* User uploads mic input
* Transcribed via `whisper`
* Summary (text) → spoken via `gTTS`

### Code:

```python
text = whisper_model.transcribe(wav_path)
tts = gTTS(text=summary, lang='en')
tts.save("summary.mp3")
```

---

## 🔎 Stock Data Fetching (API Agent)

### Tool: `yfinance`

* Input: List of ticker symbols (e.g. \["AAPL", "TSLA"])
* Output: Current price, volume, market cap

### Code:

```python
data = yf.Ticker(symbol).info
```

---

## 📰 Market News Scraping (Scraper Agent)

### Tools:

* `requests`
* `BeautifulSoup`

### Sources: Public finance news sites (e.g. Yahoo Finance)

* Extracts title, short description

### Code:

```python
soup = BeautifulSoup(response.text, "html.parser")
news = soup.select(".news-title")
```

---

## 🧪 Prompt Engineering Strategy

* Prompts are declarative, instructive, and contain structured input placeholders
* Gemini used for summarization due to fast, low-latency inference
* Stock parsing prompt tested iteratively with 10+ variations

---

## ✅ Summary Table

| Component       | AI Tool                     | Purpose                 | Model/Lib        |
| --------------- | --------------------------- | ----------------------- | ---------------- |
| Language Agent  | Gemini + LangChain          | Summarize stock & news  | gemini-1.5-flash |
| Orchestrator    | LangChain                   | Stock symbol extraction | Custom           |
| Retriever Agent | FAISS + SentenceTransformer | Vector retrieval        | all-MiniLM-L6-v2 |
| Voice Agent     | whisper + gTTS              | STT and TTS             | base, en         |
| API Agent       | yfinance                    | Fetch stock data        | Yahoo Finance    |
| Scraper Agent   | BeautifulSoup               | Scrape market headlines | Web scraping     |

---

> *This log helps track all AI interactions and models for debugging, tuning, and reproducibility.*
