import pandas as pd
import os

# Define file paths
raw_data_path = "data/scraped_data.csv"
cleaned_data_path = "data/cleaned_data.csv"

# Ensure raw data exists
if not os.path.exists(raw_data_path):
    print("❌ Error: scraped_data.csv not found! Run Scrapy first.")
    exit()

# Check if file is empty
if os.stat(raw_data_path).st_size == 0:
    print("❌ Error: scraped_data.csv is empty! Check Scrapy selectors.")
    exit()

# Load raw data with error handling
try:
    df = pd.read_csv(raw_data_path, encoding="utf-8", quotechar='"', skipinitialspace=True)
except Exception as e:
    print(f"❌ Error loading CSV: {e}")
    exit()

# Check initial row count
initial_rows = df.shape[0]

# Normalize column names (strip spaces & convert to lowercase)
df.columns = df.columns.str.strip().str.lower()

# Remove duplicate rows (BUT LOG HOW MANY ARE REMOVED)
df = df.drop_duplicates()
duplicates_removed = initial_rows - df.shape[0]

# Keep rows even if some columns are empty (Fill missing with N/A)
df = df.fillna("N/A")

# Strip spaces from text columns
for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].str.strip()

# Save cleaned data
df.to_csv(cleaned_data_path, index=False, encoding="utf-8")

# Print processing summary
print("✅ Data cleaning completed successfully!")
print(f"📌 Rows before cleaning: {initial_rows}")
print(f"📌 Duplicates removed: {duplicates_removed}")
print(f"📌 Final row count: {df.shape[0]}")
print(f"✅ Cleaned data saved to {cleaned_data_path}")
