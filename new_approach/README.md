# AI/ML Gamification Data Analysis - New Approach

📊 **[Results Data and Dashboard](https://docs.google.com/spreadsheets/d/131PQk-wL5ocBG08PzEwUMotFdgWREY5HHPaLAawZxOc/edit?gid=1443396908#gid=1443396908)** 

📁 **[Data on Google Drive](https://drive.google.com/drive/folders/1RFGQjZoxV-K1h0PhhCZAAnsqFrJh_d18?usp=share_link)**

This repository analyzes data science competitions across multiple popular platforms, focusing on fairness, bias, data privacy, and transparency using a modular, platform-specific approach.

---

## 💡 Overview

The new approach provides a more organized and scalable system for analyzing competitions from three major data science competition websites:

- **Kaggle**
- **AI Crowd**
- **DrivenData**

Each platform has its own dedicated module with specialized scraping and analysis scripts.

---

## 🔄 Workflow: Scraping → Analysis → Results

- Scraping: Collect competition lists and detailed pages per platform (see '📄 Data Acquisition Workflow').
- Analysis: Run ethical AI analysis using prompts and APIs (see '🤖 AI Analysis Framework').
- Results: Consolidate to CSVs and artifacts (see '📊 Data Outputs').

---

## 📁 Project Structure

```
new_approach/
├── src/                          # Source code modules
│   ├── kaggle/                   # Kaggle-specific scripts
│   │   ├── get_comp_list.py      # Scrape competition listings
│   │   ├── get_comp_details.py   # Extract competition details
│   │   └── get_comp_analysis.py  # Analyze competitions for ethics
│   ├── aicrowd/                  # AI Crowd-specific scripts
│   │   ├── get_comp_analysis.py  # Analyze competitions for ethics
│   │   └── get_comp_details.py   # Extract competition details
│   ├── datadriven/               # DrivenData-specific scripts
│   │   ├── get_comp_list.py      # Scrape competition listings
│   │   ├── get_comp_details.py   # Extract competition details
│   │   ├── get_comp_analysis.py  # Analyze competitions for ethics
│   │   └── README.md             # Platform-specific documentation
│   ├── json_to_csv.py            # Convert JSON results to CSV
│   └── prompts.py                # AI analysis prompts and definitions
├── data/                         # Data storage (excluded from git)
│   ├── kaggle/                   # Kaggle data
│   ├── aicrowd/                  # AI Crowd data
│   └── datadriven/               # DrivenData data
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 📦 Data Folder Structure

The `new_approach/data/` directory holds inputs and analysis results for each platform. It is excluded from version control via the repository `.gitignore`.

```
new_approach/data/
├── kaggle/
│   ├── inputs/
│   │   ├── kaggle_competitions_all_types.json
│   │   └── kaggle_competitions_final.json
│   └── results/
│       ├── ethical_analysis.json
│       ├── ethical_analysis_1000_09242025.csv
│       └── ethical_analysis_20_09202025.csv
├── aicrowd/
│   ├── inputs/
│   │   ├── aicrowd_competitions_final.json
│   │   └── extracted_urls.json
│   └── results/
│       ├── ethical_analysis.json
│       └── ethical_analysis.csv
├── datadriven/
│   ├── inputs/
│   │   ├── datadriven_competitions_all_types.json
│   │   └── datadriven_competitions_final.json
│   └── results/
│       └── ethical_analysis.json
├── ethical_analysis_combined_10202025.csv
├── ethical_analysis_combined_10212025.csv
└── ethical_analysis_combined_cats_09242025.csv
```

Notes:
- File names may evolve; the structure (inputs/results per platform) remains consistent.
- Large artifacts and raw data live here and are intentionally not tracked in git.

---

## 🤖 AI Analysis Framework

The analysis uses **Google's Gemini API** to evaluate competitions across multiple ethical dimensions:

### Analysis Categories

- **Category**: Field or industry (healthcare, finance, etc.)
- **Fairness & Bias**: Algorithmic bias, discrimination prevention, equitable outcomes
- **Data Privacy**: PII protection, anonymization, GDPR compliance
- **Transparency**: Reproducibility, open code, clear documentation
- **Explainability**: Model prediction explanations (SHAP, LIME, etc.)
- **Post-Competition Model Use**: Plans for winning models after competition
- **Toy Competition**: Practice/learning competitions vs. serious challenges
- **Red Teaming**: Adversarial testing, vulnerability discovery

### Prompt Engineering

The `prompts.py` file contains carefully crafted prompts that:
- Define each ethical category precisely
- Provide clear yes/no criteria
- Require specific evidence and quotes
- Generate structured JSON outputs

---

## 📄 Data Acquisition Workflow

### 1. Competition Discovery
- **Kaggle**: Scrapes Featured and Research sections
- **DrivenData**: Scrapes completed competitions
- **AI Crowd**: Uses existing competition lists

### 2. Content Extraction
- Navigates through competition pages
- Extracts detailed descriptions and rules
- Handles different page structures per platform
- Saves structured data to JSON files

### 3. Ethical Analysis
- Uses Gemini API for consistent analysis
- Applies standardized prompts across platforms
- Generates structured JSON with evidence
- Supports rate limiting and resume functionality

### 4. Data Consolidation
- Converts platform-specific JSON to unified CSV
- Combines results across all platforms
- Maintains platform attribution

---

## ⚙️ Platform-Specific Features

### Kaggle Module
- **Sections**: Featured and Research competitions
- **Pagination**: Handles infinite scroll and pagination
- **Prize Extraction**: Automatically extracts prize amounts
- **Rate Limiting**: Built-in delays for API calls

### AI Crowd Module
- **Content Extraction**: Detailed competition analysis
- **Ethical Analysis**: Comprehensive ethical evaluation
- **Resume Support**: Can continue interrupted analyses

### DrivenData Module
- **Competition Discovery**: Scrapes completed competitions
- **Navigation Handling**: Handles different page layouts
- **Content Extraction**: Extracts all relevant sections
- **Structure Validation**: Validates scraped data integrity

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Environment Setup

```bash
# Set your Google API key
export GOOGLE_API_KEY='your_gemini_api_key'
```

### Running Analysis

#### 1. Scrape Competitions (DrivenData example)
```bash
cd src/datadriven
python get_comp_list.py --limit 10
python get_comp_details.py
```

#### 2. Analyze for Ethics
```bash
python get_comp_analysis.py --limit 10
```

#### 3. Convert to CSV
```bash
cd ../..
python json_to_csv.py
```

---

## 📊 Data Outputs

### JSON Files (per platform)
- `ethical_analysis.json`: Complete analysis results
- `competitions_final.json`: Detailed competition data
- `competitions_all_types.json`: Competition listings

### CSV Files
- `ethical_analysis_combined.csv`: Unified results across platforms
- Platform-specific CSV files for individual analysis

---

## 🔧 Configuration

### Paths
Update file paths in scripts to match your directory structure:
- Data input/output directories
- API key configuration
- Platform-specific settings

### Analysis Parameters
- `--limit`: Number of competitions to process
- `--resume`: Continue from previous run
- Rate limiting and delay settings

---

## 📈 Analysis Results

The following figures are computed from `new_approach/data/*/results/ethical_analysis.json`:

- Kaggle (total 492):
  - Red teaming: 7
  - Fairness/Bias mentioned: 42
  - Data privacy mentioned: 300
  - Transparency mentioned: 489
  - Toy competitions: 87
- DrivenData (total 104):
  - Red teaming: 11
  - Fairness/Bias mentioned: 18
  - Data privacy mentioned: 67
  - Transparency mentioned: 104
  - Toy competitions: 24
- AIcrowd (total 204):
  - Red teaming: 1
  - Fairness/Bias mentioned: 10
  - Data privacy mentioned: 57
  - Transparency mentioned: 199
  - Toy competitions: 85

- Overall (total 800):
  - Red teaming: 19
  - Fairness/Bias mentioned: 70
  - Data privacy mentioned: 424
  - Transparency mentioned: 792
  - Toy competitions: 196

### Ethical Score (0–4)
- Definition: fairness + privacy + transparency + explainability (each yes=1, no=0; max 4).
- Across 800 competitions:
  - Mean score: 1.6513
  - Percentage above mean: 58.63%
  - Distribution:
    - 0: 7
    - 1: 324
    - 2: 417
    - 3: 45
    - 4: 7

---

## 🛠️ Development

### Adding New Platforms
1. Create new platform directory in `src/`
2. Implement three core scripts:
   - `get_comp_list.py` (if applicable)
   - `get_comp_details.py`
   - `get_comp_analysis.py`
3. Update `json_to_csv.py` to include new platform
4. Add platform-specific documentation

### Customizing Analysis
- Modify prompts in `prompts.py`
- Adjust analysis criteria
- Add new ethical dimensions
- Update JSON output structure

---

## 📋 Requirements

- Python 3.7+
- Selenium WebDriver
- Google Generative AI
- Chrome browser
- Platform-specific dependencies

---

## 🚀 Happy Analyzing!

This modular approach provides a scalable foundation for analyzing ethical considerations in data science competitions across multiple platforms.
