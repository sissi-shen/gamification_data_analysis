# AI/ML Gamification Data Analysis

This repository analyzes data science competitions across multiple popular platforms, focusing on fairness, bias, data privacy, and transparency.

---

## 💡 Overview

The project scrapes recent competitions from three major data science competition websites:

- **Kaggle** — 300 competitions
- **AI Crowd** — 221 competitions
- **DrivenData** — 65 competitions

Total competitions analyzed: **586 (as of June 2025).**

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

## 📁 Data Structure

All results are stored under the `Data` folder.  
Inside each competition site sub-folder (`kaggle_results`, `aicrowd_results`, `drivendata_results`), you will find:

- `fairness_bias.json`: Competitions mentioning fairness or bias
- `data_privacy.json`: Competitions with data privacy issues
- `transparency.json`: Competitions discussing model transparency
- `red_teaming.json`: Competitions classified as red teaming challenges
- `all_processed_results.json`: Complete structured outputs for all competitions

---

## ✅ How to Run

1. Clone the repository.
2. Install requirements (Selenium, OpenAI Python SDK).
3. Provide your OpenAI API key in environment variables or script settings.
4. Run `scraping` scripts to collect competition data.
5. Run `gpt_test` script to analyze the collected data.

---

## 📊 Project Status

- ✅ Data scraping and acquisition complete
- ✅ Competition analysis with ChatGPT complete
- ✅ Categorized structured JSON files generated

---

## 💬 Contact

For questions, please open an issue or contact the maintainer.

---

### 🚀 Happy analyzing!
