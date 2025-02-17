import pandas as pd
import requests
import json
import os

# Define file paths
cleaned_data_path = "data/cleaned_data.csv"
enhanced_data_path = "data/enhanced_data.csv"

# Ensure cleaned data exists
if not os.path.exists(cleaned_data_path):
    print("❌ Error: cleaned_data.csv not found! Run preprocessing first.")
    exit()

# Load cleaned data
df = pd.read_csv(cleaned_data_path, encoding="utf-8")

# Define Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"

# Function to enhance text using Ollama
def enhance_text(text):
    prompt = f"""
    You are an AI assistant processing bank website content.
    Structure the text into:
    - A short, clear title
    - A well-organized summary
    - Key action points
    - Emojis for readability

    **Text:** {text}
    """

    payload = {"model": "gamme-2b", "prompt": prompt, "stream": False}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(OLLAMA_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json().get("response", text)
        else:
            return text  # Return original text if API fails
    except requests.exceptions.RequestException:
        return text  # Return original text in case of connection failure

# Enhance each row of the dataset
df["enhanced_content"] = df["full_text"].apply(lambda x: enhance_text(x) if isinstance(x, str) else "N/A")

# Save enhanced data
df.to_csv(enhanced_data_path, index=False, encoding="utf-8")

print(f"✅ Enhanced data saved to {enhanced_data_path}")
