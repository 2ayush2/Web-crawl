# app/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import ollama
import os

app = FastAPI()

# Static Files (for serving HTML, CSS, JavaScript)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates (for rendering HTML with dynamic content)
templates = Jinja2Templates(directory="templates")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production!
    allow_methods=["*"],
    allow_headers=["*"],
)

CRAWLED_DATA_PATH = "data/enhanced_data.csv" # relative path

def generate_answer(user_question, scraped_data, model_name="qwen2.5:72b"):
    ai_prompt = f"Based on the following crawled data:\n{scraped_data}\nAnswer the question: {user_question}"
    try:
        # Use the ollama.generate function to interact with the Ollama model
        model_response = ollama.generate(model=model_name, prompt=ai_prompt)
        return model_response["response"]
    except Exception as e:
        return f"Error communicating with the AI model: {str(e)}"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/get-data")
async def get_crawled_data():
    try:
        df = pd.read_csv(CRAWLED_DATA_PATH)
        return df.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{CRAWLED_DATA_PATH}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    user_question = data.get("question", "").strip()
    if not user_question:
        return {"answer": "Please enter a question."}  # Handle empty questions

    try:
        df = pd.read_csv(CRAWLED_DATA_PATH)
        scraped_data = ""
        if 'enhanced_content' in df.columns:
            for index, row in df.iterrows():
                scraped_data += row['enhanced_content'] + "\n"
        else:
            scraped_data = "No enhanced content available." # Or handle the missing column appropriately
    except FileNotFoundError:
        scraped_data = "No data available."
    except Exception as e:
        scraped_data = f"Error loading crawled data: {str(e)}"

    answer = generate_answer(user_question, scraped_data)
    return {"answer": answer}

# if __name__ == "__main__": #This section is not required. Uvicorn is called by the CMD in the Dockerfile.
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)