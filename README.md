# AI/ML Gamification Data Analysis

This repository analyzes data science competitions across multiple popular platforms, focusing on fairness, bias, data privacy, and transparency.

---

## 💡 Overview

The project scrapes recent competitions from three major data science competition websites:

- **Kaggle** — 300 competitions
- **AI Crowd** — 221 competitions
- **DrivenData** — 66 competitions

Total competitions analyzed: **587 (as of June 2025).**

---

## 📄 Data Acquisition

The `scraping` script uses **Selenium** to collect detailed information from each platform. Specifically, it retrieves:

- Competition overview
- Dataset description
- Evaluation details

The script intelligently handles different page structures and navigation styles across all three sites to extract the most complete and relevant information.

---

## 🤖 GPT Analysis

The `gpt_test` script leverages the **OpenAI API** (ChatGPT) to analyze the competition information. It asks the model to:

- Identify the **category** or field of each competition
- Detect if **fairness and bias issues** are mentioned or addressed
- Identify potential **data privacy concerns**
- Examine **transparency requirements** or mentions
- Determine if the competition is a **red teaming challenge**
- Classify competitions as "toy" or serious

---

## 📎 Pattern Matching

The `pattern_match` script searches competition information for keyword matches relating to key ethics areas, to validate the results of the GPT analysis. For each ethical category (fairness/bias, data privacy, red_teaming, transparency/interpretability, toy competition), it:

- Extracts the **competition name** and **url**
- For each ethical category, flags if any keyword in exists in the competition description
- Shows which keywords are present

---

## ⚖️ Validate Outputs

The `validate_outputs` script compares ethical flags of gpt results with pattern matching results, to identify any discrepencies or hallucinations of the LLM:

- Identifies rows where discrepencies exist
- For each discrepency, a human reviewer reads the competition description throughly and makes a judgement about which analysis result is accurate
- Results are updated in the gpt results accordingly

---

## 📌 Summary Stats

The `summary_stats` script performs basic EDA of the results, providing visualizations and statistical summaries for the following questions:

- Out of all competitions, how many mention (1) bias and/or fairness (2) data privacy (3) transparency and/or interpretability?
- Out of all competitions, how many are (1) red-teaming competitions (2) toy/practice competitions?
- Out of all red-teaming competitions, how many mention (1) bias and/or fairness (2) data privacy (3) transparency and/or interpretability?
- Out of all red-teaming competitions, how many are toy/practice competitions?

All results are saved formally as csvs in the `Results` directory.

---

## 📁 Data Structure

Raw results are stored under the `Data` folder.  
Inside each competition site sub-folder (`kaggle_results`, `aicrowd_results`, `drivendata_results`), you will find:

- `fairness_bias.json`: Competitions mentioning fairness or bias
- `data_privacy.json`: Competitions with data privacy issues
- `transparency.json`: Competitions discussing model transparency
- `red_teaming.json`: Competitions classified as red teaming challenges
- `all_processed_results.json`: Complete structured gpt outputs for all competitions
- `all_pattern_match_results.json`: Complete structured pattern matching results for all competitions

Scripts are stored under the `Data Aquisition` folder.

Validated results and summary stats (in csv format) are stored under the `Results` folder.

---

## ✅ How to Run

1. Clone the repository.
2. Install requirements (Selenium, OpenAI Python SDK).
3. Provide your OpenAI API key in environment variables or script settings.
4. Run `scraping` scripts to collect competition data.
5. Run `gpt_test` script to analyze the collected data.
6. Run `pattern_match` script to extract ethical keywords
7. Run `validate_outputs` to validate gpt and pattern matching results
8. Run `summary_stats` for EDA to see visualizations and generate csvs with the validated results

---

## 📊 Project Status

- ✅ Data scraping and acquisition complete
- ✅ Competition analysis with ChatGPT complete
- ✅ Pattern matching complete
- ✅ Categorized structured gpt outputs JSON files generated
- ⚠️ NEED TO REVISIT: GPT validation with pattern matching results
- ✅ Summary statistics & EDA
- ✅ Data analysis complete, begin writing

---

## 💬 Contact

For questions, please open an issue or contact the maintainer.

---

### 🚀 Happy analyzing!
