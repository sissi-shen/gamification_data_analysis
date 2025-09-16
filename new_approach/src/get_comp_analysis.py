import google.generativeai as genai
import json
import os
import time
import argparse

# --- Configuration ---
INPUT_FILE = "data/kaggle_competitions_final.json"
OUTPUT_FILE = "data/ethical_analysis.json"

# --- Gemini API Setup ---
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    print("✅ Gemini API configured successfully.")
except KeyError:
    print("❌ ERROR: GOOGLE_API_KEY environment variable not found.")
    print("Please set the key using: export GOOGLE_API_KEY='your_key'")
    exit()

generation_config = {"response_mime_type": "application/json"}
model = genai.GenerativeModel(
    "gemini-2.5-pro", generation_config=generation_config
)

# --- Final, Strict System Prompt ---
SYSTEM_PROMPT = """
You are an expert AI assistant specializing in analyzing text for specific ethical and practical characteristics of data science competitions. Your task is to analyze the user-provided 'context' and generate a single, valid JSON object with a specific, flat structure.

**CRITICAL RULES:**
1.  Your entire response MUST be a single, valid JSON object. Do not include any text, explanations, or markdown formatting outside of the JSON.
2.  The JSON object MUST have a flat structure. DO NOT use nested JSON objects.
3.  Your analysis MUST be based ONLY on the provided 'context'. Do not infer or use external knowledge.
4.  For each topic, you will provide a "yes" or "no" answer for the boolean key (e.g., `fairness_bias_mentioned`).
5.  If the answer is "yes", you MUST provide a brief explanation and directly quote the relevant text in the corresponding 'how' key (e.g., `how_fairness`).
6.  If the answer is "no", the corresponding 'how' key MUST be an empty string ("").

**REQUIRED JSON OUTPUT STRUCTURE (MUST FOLLOW EXACTLY):**

```json
{
  "fairness_bias_mentioned": "no",
  "how_fairness": "",
  "data_privacy": "yes",
  "how_data_privacy": "The relevant quote and explanation for why data privacy is mentioned.",
  "toy": "yes",
  "how_toy": "The relevant quote and explanation for why it's a toy competition.",
  "red_team": "no",
  "how_red_team": "",
  "transparency_mentioned": "yes",
  "how_transparency": "The relevant quote and explanation for why transparency is mentioned."
}
```

**DEFINITIONS FOR ANALYSIS:**
-   *fairness_bias_mentioned*: Yes if fairness, algorithmic bias, discrimination prevention, or equitable AI outcomes are discussed. No if fairness refers to unrelated topics like prices or competition rules.
-   *data_privacy*: Yes if privacy, PII protection, anonymization, secure data handling, or compliance (e.g. GDPR) is mentioned. No if it only talks about generic data use or storage.
-   *toy*: Yes if competition is mainly for learning or practice (keywords: playground, getting started, educational) or has very low/no prize. No if serious prizes or deployment goals are mentioned.
-   *red_team*: Yes if focus is on adversarial testing, finding vulnerabilities, stress-testing models, or harm discovery. No if just normal model evaluation.
-   *transparency_mentioned*: Yes if transparency, explainability, reproducibility, open code, or clear documentation are mentioned for model/data/evaluation. No if transparency is only about logistics like rules or pricing.
"""

def analyze_competition_context(context, competition_name):
    """
    Sends the competition context to the Gemini API and returns the structured analysis.
    """
    print(f"  - Sending '{competition_name}' to Gemini API for analysis...")
    prompt = f"Here is the context for the competition '{competition_name}':\n\n{context}"
    
    try:
        response = model.generate_content([SYSTEM_PROMPT, prompt])
        return json.loads(response.text)
    except Exception as e:
        print(f"  ❌ An error occurred with the Gemini API: {e}")
        return None

def main(start_index):
    # --- Load Source Data ---
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            source_competitions = json.load(f)
        print(f"✅ Loaded {len(source_competitions)} competitions from {INPUT_FILE}")
    except FileNotFoundError:
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    # --- Handle Overwrite vs. Resume Logic ---
    if start_index > 0:
        # RESUME MODE: Load existing results to append to them.
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                final_results = json.load(f)
            print(f"✅ RESUMING. Loaded {len(final_results)} previously analyzed competitions.")
        except FileNotFoundError:
            print(f"❌ ERROR: You specified --start_index {start_index}, but '{OUTPUT_FILE}' was not found to resume from.")
            return
    else:
        # OVERWRITE MODE: Start with an empty list.
        final_results = []
        print(f"✅ Starting a new analysis session. '{OUTPUT_FILE}' will be overwritten upon completion.")

    # --- Main Processing Loop ---
    total_competitions = len(source_competitions)
    processed_in_this_run = 0
    for index, competition in enumerate(source_competitions):
        if index < start_index:
            continue
            
        print(f"\n({index + 1}/{total_competitions}) Processing: {competition['name']}")

        analysis_data = analyze_competition_context(competition.get("context", ""), competition['name'])
        
        if analysis_data:
            processed_in_this_run += 1
            structured_record = {
                "name": competition.get("name"),
                "url": competition.get("link"),
                "fairness_bias_mentioned": analysis_data.get("fairness_bias_mentioned", "no"),
                "how_fairness": analysis_data.get("how_fairness", ""),
                "data_privacy": analysis_data.get("data_privacy", "no"),
                "how_data_privacy": analysis_data.get("how_data_privacy", ""),
                "toy": analysis_data.get("toy", "no"),
                "how_toy": analysis_data.get("how_toy", ""),
                "red_team": analysis_data.get("red_team", "no"),
                "how_red_team": analysis_data.get("how_red_team", ""),
                "transparency_mentioned": analysis_data.get("transparency_mentioned", "no"),
                "how_transparency": analysis_data.get("how_transparency", ""),
            }
            final_results.append(structured_record)

            # Save progress after every single record.
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(final_results, f, indent=4, ensure_ascii=False)
            print(f"  - ✅ Success! Progress saved. Total records: {len(final_results)}")
            
            # Rate Limiting: Pause for 60 seconds after every 3 calls.
            if processed_in_this_run % 3 == 0 and (index + 1) < total_competitions:
                print(f"\n--- Pausing for 60 seconds to respect API rate limits... ---")
                time.sleep(60)
            else:
                time.sleep(1) # Standard 1-second pause between calls

        else:
            # --- Fallback System ---
            print(f"  - Fallback triggered due to API error.")
            print(f"🔴 To resume from this point, run the script again with the command:")
            print(f"   python {os.path.basename(__file__)} --start_index {index}")
            return 

    print(f"\n🎉 Analysis complete! All {len(final_results)} records have been processed and saved to {OUTPUT_FILE}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Kaggle competitions using Gemini API.")
    parser.add_argument(
        "--start_index",
        type=int,
        default=0,
        help="The index (0-based) to start processing from. Use this to resume a failed run."
    )
    args = parser.parse_args()
    
    main(args.start_index)

