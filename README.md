# 🧠 Multi-Agent Financial Assistant

This project is a multi-agent voice-enabled financial assistant that understands voice or text-based queries about the stock market, fetches real-time data, retrieves relevant news, summarizes it using an LLM, and responds back with both text and synthesized speech.

Note: The Streamlit frontend is deployed separately, while the Orchestrator and other agents—API Agent, Retriever Agent, Scraper Agent, Language Agent, and Voice Agent—are all deployed live on Render.
Demo Of Project:https://youtu.be/PdxWSEtlPVU
---

## 📂 Directory Structure

```
.
├── agents/
│   ├── api_agent/
│   ├── language_agent/
│   ├── scraper_agent/
│   ├── retriever_agent/
│   ├── voice_agent/
│   └── orchestrator/  ← Coordination happens here
├── streamlit_app/      ← Frontend app for interaction
├── docs/
│   └── ai_tool_usage.md
├── docker-compose.yml
├── README.md
└── requirements.txt
```

---

## ⚙️ Agents Overview

### 🛰️ Orchestrator (FastAPI)

* Accepts user query
* Extracts stock symbols (via LLM)
* Coordinates all other agents
* Endpoint: `/orchestrate`

### 📈 API Agent

* Fetches live stock data using `yfinance`
* Endpoint: `/get_stock_data` (POST)

### 📰 Scraper Agent

* Scrapes real-time market news headlines
* Endpoint: `/scrape_market_news`

### 📚 Retriever Agent

* Uses `SentenceTransformer` and `FAISS` to retrieve news chunks
* Indexing Endpoint: `/index_articles`
* Query Endpoint: `/query?q=...`

### 🧠 Language Agent

* Uses `LangChain` + Gemini 1.5 Flash model
* Summarizes stock data and news
* Endpoint: `/summarize`

### 🎙️ Voice Agent

* Uses `whisper` for STT and `gTTS` for TTS
* Accepts voice input, returns mp3

---

## 💻 Streamlit Frontend

* Records audio via mic
* Sends query to orchestrator
* Displays text summary and optionally plays back the audio

---

## 🐳 Docker Configuration

Each agent has its own Dockerfile and exposed port. A `docker-compose.yml` file brings all services up together.

### To Start All Services:

```bash
docker-compose up --build
```

> ⚠️ Ensure you're not using the C: drive if it's full. Use Docker Desktop settings → Resources → Disk image location to change location.

---

## 🚀 Deployment

* You can deploy only the `streamlit_app` using [Streamlit Community Cloud](https://streamlit.io/cloud)
* Or self-host using a cloud VM (e.g. Render, Railway, EC2)

---

## 📊 Toolkit Comparison

| Task                  | Toolkit/Library              |
| --------------------- | ---------------------------- |
| LLM Summarization     | LangChain + Gemini           |
| STT/TTS               | Whisper + gTTS               |
| Vector Search         | FAISS + SentenceTransformers |
| API and Orchestration | FastAPI                      |
| Stock Data Fetching   | yfinance                     |
| Frontend Interface    | Streamlit + SoundDevice      |

---

## 📈 Sample Architecture Diagram

           ┌────────────────────────────┐
           │      🎤 User Input         │
           │  (Voice/Text via Streamlit)│
           └────────────┬───────────────┘
                        ↓
           ┌────────────────────────────┐
           │    Streamlit Frontend      │
           │ - Records voice            │
           │ - Sends to Orchestrator    │
           └────────────┬───────────────┘
                        ↓
           ┌────────────────────────────┐
           │     🛰️ Orchestrator Agent   │
           │  (FastAPI - Main Router)   │
           │ - Extracts stock symbols   │
           │ - Coordinates all agents   │
           └──────┬────┬────┬────┬──────┘
                  │    │    │    │
      ┌───────────┘    │    │    └────────────┐
      ↓                ↓    ↓                 ↓
┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│ 📈 API Agent│ │📰 Scraper Agent│ │📚 Retriever  │ │🎙️ Voice Agent│
│ (yfinance) │ │ (News scrape)│ │ (FAISS + ST)│ │(Whisper/gTTS)│
└────┬───────┘ └────┬────────┘ └────┬───────┘ └────┬────────┘
     │              │               │              │
     └──────────────┴──────┬────────┴──────────────┘
                           ↓
               ┌────────────────────────────┐
               │  🧠 Language Agent (LLM)     │
               │ (LangChain + Gemini 1.5)   │
               │ - Summarizes stock + news  │
               └────────────┬───────────────┘
                            ↓
               ┌────────────────────────────┐
               │ Text Summary + Audio Reply │
               │ Sent back to Streamlit     │
               └────────────────────────────┘
```

---

## 📈 Performance Benchmarks *(optional)*

* Query time: \~15-18s for stock + news + summary
* LLM: Gemini 1.5 Flash (Best free available LLM)
* STT: Whisper tiny (\~3-4s audio)

---

## 📁 Requirements

* Docker
* Docker Compose
* (Optional) WSL2 (if using Windows, but not mandatory)

---

## ✅ Status

* ✅ Modular agents (FastAPI-based)
* ✅ Working voice + text query
* ✅ End-to-end functional orchestrator
* ✅ Dockerized
* ✅ Streamlit frontend connected
* ✅ Ready for GitHub and deployment

---

## 📝 Authors

* Abhay Sharma

---

## 🔗 Useful Commands

```bash
# Build and run all services
$ docker-compose up --build

# Run only one agent for testing
$ docker-compose up api_agent

# Check logs for orchestrator
$ docker-compose logs orchestrator
```

---

## 📹 Optional Demo

A Demo Video is Uploaded of the functioning of Project.

> *Thanks for reading!* ✨
