import json
import csv
import os

# --- Configuration ---
INPUT_FILE = "data/ethical_analysis.json"
OUTPUT_FILE = "data/ethical_analysis.csv"

def convert_json_to_csv():
    """
    Reads the JSON output from the Gemini analyzer and converts it into a CSV file.
    """
    # --- Load Source JSON Data ---
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} records from {INPUT_FILE}")
    except FileNotFoundError:
        print(f"❌ Input file not found: {INPUT_FILE}")
        print("Please run the gemini_analyzer.py script first to generate the JSON file.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON from {INPUT_FILE}. The file might be empty or corrupted.")
        return

    if not data:
        print("🟡 The JSON file is empty. Nothing to convert.")
        return

    # --- Prepare for CSV Writing ---
    # Define the headers based on the keys in your structured_record
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
    ]

    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write the header row
            writer.writerow(headers)
            
            # --- Write Data Rows ---
            for record in data:
                # Create a list of values in the same order as the headers
                row = [record.get(header, "") for header in headers]
                writer.writerow(row)
        
        print(f"🎉 Success! Converted {len(data)} records to {OUTPUT_FILE}.")

    except IOError as e:
        print(f"❌ An error occurred while writing to the CSV file: {e}")


if __name__ == "__main__":
    convert_json_to_csv()
