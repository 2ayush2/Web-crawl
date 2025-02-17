import json
import os

training_data = [
    {"prompt": "Tell me about Nabil Bank loans.", "response": "Nabil Bank offers personal, auto, and home loans."},
    {"prompt": "What is nRemit?", "response": "nRemit is Nabil Bank's remittance service for sending money to Nepal."},
    {"prompt": "How can I open an account?", "response": "You can open an account at https://nabilbank.com or visit a branch."}
]

with open("data/training_data.jsonl", "w") as f:
    for item in training_data:
        f.write(json.dumps(item) + "\n")

os.system("ollama create banking-ai -f data/training_data.jsonl")
print("✅ Ollama AI trained successfully!")
