from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

app = FastAPI(title="Language Agent")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash",
    google_api_key="AIzaSyAYHaKWloNVe4uUtHzjyZZXi8E9eFVA8R4",
    temperature=0.2
)

class LanguageInput(BaseModel):
    stock_data: List[dict]
    retrieved_chunks: List[str]

@app.get("/")
def root():
    return {"message": "Language Agent is running"}

@app.post("/summarize")
def summarize(data: LanguageInput):
    prompt = PromptTemplate.from_template("""
You are a financial assistant tasked with summarizing market data and news highlights in a natural, engaging style.

- Clearly mention each stock's current price and percentage change in the summary.
- Highlight top gainers and losers by comparing the change percentages.
- Note any relevant earnings surprises if mentioned in the news.
- Write a confident, professional morning market brief without repeating numbers or phrases unnecessarily.

Stock Info:
{stock_info}

News Highlights:
{news_info}

Generate the market summary now:
""")

    stock_info = "\n".join(
        f"{s['symbol']}: Price {s['current_price']}, Previous Close {s['previous_close']}, Change {s['change_pct']}%"
        for s in data.stock_data
    )

    final_prompt = prompt.format(
        stock_info=stock_info,
        news_info="\n".join(data.retrieved_chunks)
    )

    try:
        result = llm.invoke(final_prompt)
        return {"summary": result}
    except Exception as e:
        print("🚨 LLM Error:", str(e))
        return {"error": "Language Agent failed", "details": str(e)}

