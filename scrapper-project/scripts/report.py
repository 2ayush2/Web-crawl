import pandas as pd
import matplotlib.pyplot as plt
import os

# Define file paths
enhanced_data_path = "data/enhanced_data.csv"

# Ensure enhanced data exists
if not os.path.exists(enhanced_data_path):
    print("❌ Error: enhanced_data.csv not found! Run enhancement first.")
    exit()

# Load enhanced data
df = pd.read_csv(enhanced_data_path, encoding="utf-8")

# Count occurrences of key terms
keywords = ["Loan", "Banking", "Investment", "SIP", "Remit", "Security", "Account"]
keyword_counts = {keyword: df["enhanced_content"].str.contains(keyword, case=False, na=False).sum() for keyword in keywords}

# Convert to DataFrame
keyword_df = pd.DataFrame(list(keyword_counts.items()), columns=["Category", "Count"])

# Generate a bar chart
plt.figure(figsize=(10, 5))
plt.bar(keyword_df["Category"], keyword_df["Count"], color="blue")
plt.xlabel("Categories")
plt.ylabel("Frequency")
plt.title("Keyword Analysis from Extracted Banking Data")
plt.xticks(rotation=45)
plt.savefig("data/keyword_analysis.png")
plt.show()

print("✅ Report generated successfully!")
