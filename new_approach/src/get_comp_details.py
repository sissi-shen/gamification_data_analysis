import json
import os
import re
import time
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, TimeoutException, StaleElementReferenceException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# --- 💡 Configuration ---
# Set the number of competitions you want to process.
# To process all, set this to a very large number (e.g., 9999).
COMPETITIONS_TO_PROCESS = 1002

TABS_TO_SCRAPE = ["Overview", "Data", "Rules"]
CONTENT_AREA_SELECTOR = "div[role='main']"

# --- Script Setup ---
options = Options()
# options.add_argument("--headless")
options.add_experimental_option("detach", True)
options.add_argument("--disable-blink-features=AutomationControlled")

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)
    print("✅ WebDriver started successfully.")
except Exception as e:
    print(f"❌ Failed to start WebDriver: {e}")
    exit()

# --- Handle Cookie Consent ---
driver.get("https://www.kaggle.com")
print("Navigated to Kaggle to handle cookie consent.")
try:
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='OK, Got it.']"))).click()
    print("✅ Cookie consent given.")
except TimeoutException:
    print("⚠️ Cookie consent button not found or already handled.")
time.sleep(1)

# --- Load and Slice the Data ---
input_path = "data/kaggle_competitions_all_types.json"
output_path = "data/kaggle_competitions_final.json"

try:
    with open(input_path, "r", encoding="utf-8") as f:
        competitions = json.load(f)
    print(f"✅ Successfully loaded {len(competitions)} total competitions from {input_path}")

    # Slice the list to process only the specified number of competitions
    competitions = competitions[:COMPETITIONS_TO_PROCESS]
    print(f"✅ Sliced the list to process the first {len(competitions)} competitions.")
    print(f"Output will be written to {output_path}, overwriting if it exists.")

except FileNotFoundError:
    print(f"❌ Error: The file {input_path} was not found.")
    driver.quit()
    exit()

# --- Main Scraping Loop ---
total_competitions = len(competitions)
for index, competition in enumerate(competitions):
    competition.pop("context", None)

    print(f"({index + 1}/{total_competitions}) Scraping '{competition['name']}'...")
    
    try:
        driver.get(competition['link'])
    except Exception as e:
        print(f"  ❌ Failed to open link: {competition['link']}. Error: {e}")
        competition['context'] = f"Error: Failed to open link - {e}"
        continue

    context_parts = []
    
    for tab_name in TABS_TO_SCRAPE:
        try:
            tab_selector = f"a[href$='/{tab_name.lower()}']"
            tab_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, tab_selector)))
            driver.execute_script("arguments[0].click();", tab_button)
            print(f"  - Clicked '{tab_name}' tab.")
            
            content_area = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, CONTENT_AREA_SELECTOR)))
            time.sleep(1)
            
            full_text = content_area.text
            parts = re.split(r'Overview\nData\n.*?\nRules', full_text, maxsplit=1, flags=re.DOTALL)

            if len(parts) > 1:
                full_text_no_header = parts[1]  # RIGHT side of the split
            else:
                full_text_no_header = full_text
            lines = full_text_no_header.split('\n')
            filtered_lines = [line.strip() for line in lines if len(line.strip().split()) > 5]
            processed_text = '\n'.join(lines)
            
            context_parts.append(f"--- {tab_name.upper()} ---\n{processed_text}")
            print(f"  - Captured and filtered content for '{tab_name}'.")

        except TimeoutException:
            print(f"  - Could not find tab or content for '{tab_name}'. Skipping.")
        except Exception as e:
            print(f"  - An error occurred on tab '{tab_name}': {e}")

    competition['context'] = "\n\n".join(context_parts)

    if (index + 1) % 10 == 0 or (index + 1) == total_competitions:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(competitions, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Progress saved! Scraped {index + 1}/{total_competitions} competitions.\n")

print(f"\n🎉 Scraping complete! All {total_competitions} competitions processed.")
print(f"Updated data saved to: {output_path}")

driver.quit()