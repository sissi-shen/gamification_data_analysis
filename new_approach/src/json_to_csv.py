import json
import csv
import os

KAGGLE_JSON = "../data/kaggle/results/ethical_analysis.json"
AICROWD_JSON = "../data/aicrowd/results/ethical_analysis.json"
DATADRIVEN_JSON = "../data/datadriven/results/ethical_analysis.json"
COMBINED_CSV = "../data/ethical_analysis_combined.csv"

def load_json_safely(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"🟡 Expected a list in {file_path}, got {type(data).__name__}. Skipping.")
            return []
        print(f"✅ Loaded {len(data)} records from {file_path}")
        return data
    except FileNotFoundError:
        print(f"🟠 File not found: {file_path}. Treating as empty.")
        return []
    except json.JSONDecodeError:
        print(f"🔴 JSON decode error in {file_path}. Treating as empty.")
        return []

def convert_jsons_to_combined_csv():
    # Load all three datasets
    kaggle_records = load_json_safely(KAGGLE_JSON)
    aicrowd_records = load_json_safely(AICROWD_JSON)
    datadriven_records = load_json_safely(DATADRIVEN_JSON)

    if not kaggle_records and not aicrowd_records and not datadriven_records:
        print("🟡 No input records found in any JSON. Nothing to convert.")
        return

    # Add platform field
    for rec in kaggle_records:
        rec["platform"] = "kaggle"
    for rec in aicrowd_records:
        rec["platform"] = "aicrowd"
    for rec in datadriven_records:
        rec["platform"] = "datadriven"

    combined = kaggle_records + aicrowd_records + datadriven_records

    # Headers in desired order, with platform as the last column
    headers = [
        "name",
        "url",
        "category",
        "fairness_bias_mentioned",
        "how_fairness",
        "data_privacy",
        "how_data_privacy",
        "transparency_mentioned",
        "how_transparency",
        "data_explainability",
        "how_explainability",
        "post_competition_model_use",
        "how_model_use",
        "toy",
        "how_toy",
        "red_team",
        "how_red_team",
        "platform",
    ]

    # Ensure output directory exists
    os.makedirs(os.path.dirname(COMBINED_CSV), exist_ok=True)

    try:
        with open(COMBINED_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for record in combined:
                row = [record.get(header, "") for header in headers]
                writer.writerow(row)
        print(f"🎉 Success! Wrote {len(combined)} records to {COMBINED_CSV}.")
    except IOError as e:
        print(f"❌ Error writing CSV: {e}")


if __name__ == "__main__":
    convert_jsons_to_combined_csv()
