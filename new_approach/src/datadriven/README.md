# DataDriven Competition Scraping System

This directory contains scripts for scraping and analyzing DataDriven competitions for ethical AI research.

## Overview

The system consists of three main scripts that work together to:
1. Scrape competition listings from DataDriven
2. Extract detailed content from each competition
3. Analyze competitions for ethical characteristics using AI

## Scripts

### 1. `get_comp_list.py` - Competition List Scraper
Scrapes the list of completed competitions from DataDriven.

**Usage:**
```bash
python get_comp_list.py --limit 2
```

**Features:**
- Scrapes from https://www.drivendata.org/competitions/search/?tab=status_completed
- Extracts competition metadata (name, link, prize, host, etc.)
- Supports limit parameter for testing
- Saves results to `data/datadriven/inputs/datadriven_competitions_all_types.json`

### 2. `get_comp_details.py` - Competition Details Scraper
Extracts detailed content from each competition by navigating through the competition pages.

**Usage:**
```bash
python get_comp_details.py
```

**Features:**
- Processes competitions from the list scraper
- Navigates through competition navigation sections
- Extracts content from all sections except leaderboard results
- Handles both standard navigation and alternative link structures
- Saves results to `data/datadriven/inputs/datadriven_competitions_final.json`

### 3. `get_comp_analysis.py` - Ethical Analysis
Analyzes competition content for ethical characteristics using Google's Gemini API.

**Usage:**
```bash
# Set API key first
export GOOGLE_API_KEY='your_key'

# Run analysis
python get_comp_analysis.py --limit 2
```

**Features:**
- Analyzes competition content for ethical characteristics
- Uses the same analysis framework as Kaggle competitions
- Supports resume functionality and rate limiting
- Saves results to `data/datadriven/results/ethical_analysis.json`

### 4. `json_to_csv.py` - CSV Converter
Converts JSON analysis results to CSV format for easier analysis.

**Usage:**
```bash
python json_to_csv.py
```

### 5. `test_structure.py` - Structure Validator
Tests that scraped data has the expected structure.

**Usage:**
```bash
python test_structure.py
```

## Data Flow

```
1. get_comp_list.py → datadriven_competitions_all_types.json
2. get_comp_details.py → datadriven_competitions_final.json
3. get_comp_analysis.py → ethical_analysis.json
4. json_to_csv.py → ethical_analysis.csv
```

## Directory Structure

```
src/datadriven/
├── get_comp_list.py      # Scrape competition list
├── get_comp_details.py   # Extract competition details
├── get_comp_analysis.py  # Analyze for ethical characteristics
├── json_to_csv.py        # Convert to CSV
├── test_structure.py     # Validate data structure
└── README.md            # This file

data/datadriven/
├── inputs/
│   ├── datadriven_competitions_all_types.json
│   └── datadriven_competitions_final.json
└── results/
    ├── ethical_analysis.json
    └── ethical_analysis.csv
```

## Requirements

- Python 3.7+
- Selenium WebDriver
- Google Generative AI (for analysis)
- Chrome browser

## Installation

```bash
pip install selenium webdriver-manager google-generativeai
```

## Testing

To test with a small sample (2 competitions):

```bash
# 1. Scrape competition list
python get_comp_list.py --limit 2

# 2. Extract details
python get_comp_details.py

# 3. Validate structure
python test_structure.py

# 4. Analyze (requires API key)
export GOOGLE_API_KEY='your_key'
python get_comp_analysis.py --limit 2

# 5. Convert to CSV
python json_to_csv.py
```

## Notes

- The scraper handles DataDriven's specific page structure
- Navigation content extraction works for both standard and alternative page layouts
- Rate limiting is built into the analysis script
- All scripts support resuming from interruptions


