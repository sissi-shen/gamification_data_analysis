import json
import os
import re
import time
import unicodedata
import argparse
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, TimeoutException, StaleElementReferenceException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# Removed WebDriverWait imports - using direct element finding for speed
from webdriver_manager.chrome import ChromeDriverManager

# --- 💡 Configuration ---
# Set the number of competitions you want to process.
# To process all, set this to a very large number (e.g., 9999).
COMPETITIONS_TO_PROCESS = 9999  # Default to process all

# Tabs to scrape from AIcrowd competitions
TABS_TO_SCRAPE = ["Overview", "Rules"]

# --- Text Cleaning Functions ---
def clean_text_for_analysis(text):
    """
    Comprehensive text cleaning to optimize for token length and analysis.
    First extracts according to previous logic, then removes emojis/special chars, then applies >10 condition.
    """
    if not text:
        return ""
    
    # Step 1: Apply previous extraction logic first
    lines = text.split('\n')
    filtered_lines = []
    for line in lines:
        line = line.strip()
        # Keep lines that are not too short and don't look like UI elements (previous logic)
        if (len(line) > 10 and 
            not re.match(r'^(Home|Challenges|Leaderboard|Discussion|Insights|Rules|Overview)$', line) and
            not re.match(r'^[0-9\s\-_|]+$', line) and  # Skip lines that are mostly numbers/symbols
            not line.startswith('©') and  # Skip copyright notices
            'cookie' not in line.lower() and  # Skip cookie notices
            'privacy' not in line.lower()):  # Skip privacy notices
            filtered_lines.append(line)
    
    # Step 2: Remove emojis and special Unicode characters from filtered content
    cleaned_lines = []
    for line in filtered_lines:
        # Remove emojis and special Unicode characters
        cleaned_line = unicodedata.normalize('NFKD', line)
        cleaned_line = ''.join(c for c in cleaned_line if unicodedata.category(c) != 'So')
        
        # Apply line content cleaning (URLs, emails, excessive punctuation)
        cleaned_line = clean_line_content(cleaned_line)
        
        # Step 3: Apply >10 character condition after all cleaning
        if cleaned_line and len(cleaned_line.strip()) > 10:
            cleaned_lines.append(cleaned_line.strip())
    
    # Remove excessive whitespace and normalize
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\n\s*\n', '\n', result)
    
    return result

def clean_line_content(line):
    """
    Clean individual line content by removing special characters and normalizing text.
    """
    # Remove URLs
    line = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', line)
    
    # Remove email addresses
    line = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', line)
    
    # Remove dates (various formats)
    line = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '', line)  # MM/DD/YYYY, MM-DD-YYYY
    line = re.sub(r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', '', line)  # YYYY/MM/DD, YYYY-MM-DD
    line = re.sub(r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}\b', '', line, flags=re.IGNORECASE)  # DD Mon YYYY
    line = re.sub(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b', '', line, flags=re.IGNORECASE)  # Mon DD, YYYY
    line = re.sub(r'\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?\b', '', line, flags=re.IGNORECASE)  # Time formats
    line = re.sub(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4}\b', '', line, flags=re.IGNORECASE)  # Full month names
    line = re.sub(r'\b\d{4}\b', '', line)  # Years (4 digits)
    
    # Remove excessive punctuation (keep periods, commas, colons)
    line = re.sub(r'[!]{2,}', '!', line)
    line = re.sub(r'[?]{2,}', '?', line)
    line = re.sub(r'[-]{3,}', '--', line)
    line = re.sub(r'[_]{2,}', '_', line)
    
    # Remove bullet points and list markers
    line = re.sub(r'^[\s]*[•·▪▫‣⁃]\s*', '', line)
    line = re.sub(r'^[\s]*\d+[\.\)]\s*', '', line)
    line = re.sub(r'^[\s]*[a-zA-Z][\.\)]\s*', '', line)
    
    # Normalize whitespace
    line = re.sub(r'\s+', ' ', line)
    line = line.strip()
    
    return line

def deduplicate_urls(competitions):
    """
    Remove duplicate URLs from the competitions list, keeping only the first occurrence.
    """
    seen_urls = set()
    unique_competitions = []
    duplicates_removed = 0
    
    for competition in competitions:
        url = competition.get('link', '')
        if url not in seen_urls:
            seen_urls.add(url)
            unique_competitions.append(competition)
        else:
            duplicates_removed += 1
            print(f"⚠️ Removed duplicate URL: {url}")
    
    if duplicates_removed > 0:
        print(f"✅ Removed {duplicates_removed} duplicate URLs. Total unique competitions: {len(unique_competitions)}")
    
    return unique_competitions

# --- Script Setup ---
options = Options()
# options.add_argument("--headless")
options.add_experimental_option("detach", True)
options.add_argument("--disable-blink-features=AutomationControlled")

try:
    # Try to use system Chrome driver first, then fall back to ChromeDriverManager
    try:
        driver = webdriver.Chrome(options=options)
    except:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # Removed WebDriverWait - using direct element finding for speed
    print("✅ WebDriver started successfully.")
except Exception as e:
    print(f"❌ Failed to start WebDriver: {e}")
    exit()

# --- Cookie consent will be handled on each individual page ---

def main(start_index=None, limit=None):
    # --- Load and Slice the Data ---
    input_path = "/Users/manikeshmakam/Endgame 2.0/ethicalAI/data/aicrowd/inputs/extracted_urls.json"
    output_path = "/Users/manikeshmakam/Endgame 2.0/ethicalAI/data/aicrowd/inputs/aicrowd_competitions_final.json"

    # Check if output file exists first
    output_exists = os.path.exists(output_path)
    
    if output_exists:
        # Load existing output file - no need to process input data
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_competitions = json.load(f)
            print(f"✅ Loaded existing output file with {len(existing_competitions)} competitions")
            competitions = existing_competitions  # Use existing data for reference
        except:
            existing_competitions = []
            print("⚠️ Could not load existing output file, starting fresh")
            output_exists = False
    
    if not output_exists:
        # Only process input data if output file doesn't exist
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                competitions = json.load(f)
            print(f"✅ Successfully loaded {len(competitions)} total competitions from {input_path}")

            # Deduplicate URLs
            competitions = deduplicate_urls(competitions)
            
            # Create new output file with unique URLs structure - pre-populate with all URLs
            existing_competitions = []
            for comp in competitions:
                existing_competitions.append({
                    "link": comp.get("link", ""), 
                    "name": "", 
                    "context": ""
                })
            print("📝 Creating new output file with unique URLs pre-populated")
            
            # Save the initial structure with URLs
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(existing_competitions, f, indent=4, ensure_ascii=False)
            print("✅ Initial file structure saved with all URLs")
        except FileNotFoundError:
            print(f"❌ Error: The file {input_path} was not found.")
            driver.quit()
            return

    # Handle single index mode
    if start_index is not None:
        if start_index < 1 or start_index > len(competitions):
            print(f"❌ Error: start_index {start_index} is out of range. Valid range: 1-{len(competitions)}")
            driver.quit()
            return
        
        # Process only the specified index (convert from 1-based to 0-based)
        target_index = start_index - 1
        competitions_to_process = [competitions[target_index]]
        print(f"✅ Processing single competition at index {start_index} (0-based: {target_index})")
    else:
        # Process all competitions
        competitions_to_process = competitions
        print(f"✅ Processing all {len(competitions)} competitions.")

    print(f"Output will be written to {output_path}")

    # --- Main Scraping Loop ---
    total_competitions = len(competitions_to_process)
    processed_competitions = []
    
    for index, competition in enumerate(competitions_to_process):
        competition.pop("context", None)
        competition.pop("name", None)

        print(f"({index + 1}/{total_competitions}) Scraping '{competition['link']}'...")
        
        try:
            driver.get(competition['link'])
            
            # Handle cookie consent only for the first competition (index 0)
            if index == 0:
                try:
                    cookie_button = driver.find_element(By.XPATH, "//button[@class='btn btn-primary btn-sm cookies-set-accept' and text()='Accept']")
                    driver.execute_script("arguments[0].click();", cookie_button)
                    print("  ✅ Cookie consent accepted (first competition).")
                except NoSuchElementException:
                    print("  ⚠️ Cookie consent button not found or already handled.")
            else:
                print("  ⚡ Skipping cookie consent (already handled in first competition).")
                
        except Exception as e:
            print(f"  ❌ Failed to open link: {competition['link']}. Error: {e}")
            competition['context'] = f"Error: Failed to open link - {e}"
            continue

        # Extract competition name from URL or page title
        try:
            # Try to get name from page title first
            page_title = driver.title
            if page_title and page_title != "AIcrowd":
                # Extract just the middle part: "AIcrowd | Meta CRAG - MM Challenge 2025 | Challenges" -> "Meta CRAG - MM Challenge 2025"
                name = page_title.strip()
                # Remove prefix "AIcrowd |" if present
                name = re.sub(r'^AIcrowd\s*\|\s*', '', name)
                # Remove suffix "| Challenges" if present
                name = re.sub(r'\s*\|\s*Challenges.*$', '', name)
                name = name.strip()
                if name:
                    competition['name'] = name
            else:
                # Fallback: extract from URL
                url_parts = competition['link'].split('/')
                challenge_name = url_parts[-1] if url_parts[-1] else url_parts[-2]
                competition['name'] = challenge_name.replace('-', ' ').title()
        except Exception as e:
            print(f"  ⚠️ Could not extract name: {e}")
            competition['name'] = f"Unknown Competition {index + 1}"

        context_parts = []
        overview_found = False
        
        for tab_name in TABS_TO_SCRAPE:
            try:
                # Simple tab selection for Overview and Rules tabs
                if tab_name == "Overview":
                    # Overview tab is usually the default/active tab
                    tab_element = driver.find_element(By.XPATH, "//a[contains(@href, 'overview') or contains(@class, 'active')]")
                elif tab_name == "Rules":
                    # Rules tab selector - skip if not found
                    try:
                        tab_element = driver.find_element(By.XPATH, "//a[contains(@href, 'challenge_rules') or contains(text(), 'Rules')]")
                    except NoSuchElementException:
                        print(f"  - Rules tab not found. Skipping Rules tab.")
                        continue
                
                if tab_element is None:
                    print(f"  - Could not find '{tab_name}' tab. Skipping.")
                    continue
                
                # Click the tab
                driver.execute_script("arguments[0].click();", tab_element)
                print(f"  - Clicked '{tab_name}' tab.")
                
                # Try multiple selectors for content area (optimized for AIcrowd structure)
                content_selectors = [
                    "#description-wrapper .md-content",  # Main content area with markdown
                    ".challenge-description-md-content",  # Specific challenge description
                    "#description-wrapper",  # Description wrapper
                    "div[role='main']",
                    ".main-content",
                    "main"
                ]
                
                content_area = None
                for selector in content_selectors:
                    try:
                        content_area = driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if content_area is None:
                    # Fallback: get body content
                    content_area = driver.find_element(By.TAG_NAME, "body")
                    print(f"  - Using body content as fallback for '{tab_name}'.")
                else:
                    print(f"  - Found content area for '{tab_name}'.")
                
                # Get the text content
                full_text = content_area.text
                
                # Apply comprehensive text cleaning for analysis optimization
                processed_text = clean_text_for_analysis(full_text)
                
                if processed_text.strip():
                    context_parts.append(f"--- {tab_name.upper()} ---\n{processed_text}")
                    print(f"  - Captured and filtered content for '{tab_name}'.")
                    if tab_name == "Overview":
                        overview_found = True
                else:
                    print(f"  - No meaningful content found for '{tab_name}'.")
                    if tab_name == "Overview":
                        overview_found = False

            except NoSuchElementException:
                print(f"  - Could not find tab or content for '{tab_name}'. Skipping.")
            except Exception as e:
                print(f"  - An error occurred on tab '{tab_name}': {e}")

        # Check if Overview has content - if not, skip this competition
        if not overview_found:
            print(f"  ❌ No Overview content found. Skipping this competition.")
            continue
        
        competition['context'] = "\n\n".join(context_parts)
        processed_competitions.append(competition)

        # Save progress every 10 competitions or after each competition in single index mode
        if (index + 1) % 10 == 0 or (index + 1) == total_competitions or start_index is not None:
            if start_index is not None:
                # Single index mode: update the specific index in existing data
                target_index = start_index - 1
                if target_index < len(existing_competitions):
                    existing_competitions[target_index] = competition
                else:
                    # Extend the list if needed with original URLs
                    while len(existing_competitions) < target_index:
                        original_index = len(existing_competitions)
                        original_competition = competitions[original_index] if original_index < len(competitions) else {"link": ""}
                        existing_competitions.append({
                            "link": original_competition.get("link", ""), 
                            "name": "", 
                            "context": ""
                        })
                    existing_competitions.append(competition)
                final_output = existing_competitions
            else:
                # Full mode: save all processed competitions
                final_output = processed_competitions
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(final_output, f, indent=4, ensure_ascii=False)
            print(f"\n✅ Progress saved! Processed {len(processed_competitions)} valid competitions.\n")

    print(f"\n🎉 Scraping complete! Processed {len(processed_competitions)} valid competitions.")
    print(f"Updated data saved to: {output_path}")

    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape AIcrowd competitions with enhanced error handling.")
    parser.add_argument(
        "--index",
        type=int,
        help="Process only a specific competition index (1-based). If not provided, processes all competitions."
    )
    args = parser.parse_args()
    
    main(start_index=args.index)
