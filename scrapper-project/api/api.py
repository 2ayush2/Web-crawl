from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scraped Data File Path
SCRAPED_DATA_PATH = "data/scraped_data.csv"

# DeepSeek API URL
DEEPSEEK_API_URL = "http://localhost:11434/api/generate"

@app.get("/")
async def root():
    return {"message": "API is running successfully!"}

@app.get("/get-data")
async def get_scraped_data():
    """Fetch scraped data"""
    try:
        df = pd.read_csv(SCRAPED_DATA_PATH)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_data(query: str):
    """Search scraped data"""
    try:
        df = pd.read_csv(SCRAPED_DATA_PATH)
        filtered_data = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
        return filtered_data.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

@app.post("/ask")
async def ask(question: dict):
    """Ask AI a question using scraped data"""
    user_question = question.get("question", "")

    # Load scraped data
    try:
        df = pd.read_csv(SCRAPED_DATA_PATH)
        scrapped_data = df.to_string(index=False)
    except Exception:
        scrapped_data = "No relevant data available."

    # AI Prompt
    ai_prompt = f"Based on the following banking data:\n{scrapped_data}\nAnswer the question: {user_question}"

    # Request to DeepSeek AI
    response = requests.post(
        DEEPSEEK_API_URL,
        json={"model": "deepseek-r1:1.5b", "prompt": ai_prompt, "stream": False}
    )

    if response.status_code == 200:
        answer = response.json().get("response", "AI could not generate a response.")
    else:
        answer = "Error connecting to AI model."

    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)
