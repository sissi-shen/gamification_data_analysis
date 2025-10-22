import json
import os
import re
import time
import argparse
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException, StaleElementReferenceException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# 0. CLI Args
parser = argparse.ArgumentParser(description="Scrape Kaggle competitions by sections (Featured, Research)")
parser.add_argument("--featured_limit", type=int, default=0, help="Number of Featured to collect (0 = all pages)")
parser.add_argument("--research_limit", type=int, default=0, help="Number of Research to collect (0 = all pages)")
parser.add_argument("--limit", type=int, default=0, help="[Deprecated] Total limit; use --featured_limit and --research_limit instead")
args = parser.parse_args()

# 1. Configure Chrome
options = Options()
# options.add_argument("--headless")
options.add_experimental_option("detach", True)
options.add_argument("--disable-blink-features=AutomationControlled")

# 2. Start Chrome
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)
except Exception as e:
    print(f"❌ Failed to start WebDriver: {e}")
    exit()

# 3. Open Kaggle and Navigate
driver.get("https://www.kaggle.com")
print("✅ Kaggle opened successfully.")

try:
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='OK, Got it.']"))).click()
    print("✅ Cookie consent given.")
except TimeoutException:
    print("⚠️ Cookie consent button not found or already handled.")

wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Competitions"))).click()
print("✅ Clicked on Competitions tab.")

def click_section(section_label: str):
    try:
        el = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//span[normalize-space()='{section_label}' or normalize-space()='{section_label.upper()}']")
            )
        )
        try:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", el)
        except Exception:
            pass
        try:
            el.click()
            print(f"✅ Clicked on '{section_label}'.")
        except Exception:
            print(f"✅ '{section_label}' section detected (no click needed).")
    except TimeoutException:
        print(f"⚠️ '{section_label}' indicator not found; proceeding with current view.")





# 9. Main Extraction and Pagination Helpers
results = []
list_container_locator = (By.CSS_SELECTOR, "ul[role='list']")

# Prepare output path upfront so we can persist after every page
output_dir = "/Users/manikeshmakam/Endgame 2.0/ethicalAI/data/kaggle/inputs"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "kaggle_competitions_all_types.json")

def save_progress(page_number: int, section_name: str):
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"💾 Saved after {section_name} page {page_number}. Total competitions: {len(results)}")
    except Exception as e:
        print(f"⚠️ Failed to save progress after page {page_number} ({section_name}): {e}")

def scrape_current_listing(section_name: str, section_limit: int):
    page_number = 1
    reached_limit = False
    while True:
        print(f"\n--- Scraping {section_name} Page {page_number} ---")
        try:
            wait.until(EC.visibility_of_element_located(list_container_locator))
            
            # Scroll to load all items
            li_elements = driver.find_elements(list_container_locator[0], list_container_locator[1] + " > li")
            prev_count = 0
            while len(li_elements) > prev_count:
                prev_count = len(li_elements)
                if li_elements:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", li_elements[-1])
                time.sleep(1.5)
                li_elements = driver.find_elements(list_container_locator[0], list_container_locator[1] + " > li")
            
            print(f"✅ Found {len(li_elements)} competition entries on this page.")

            # Loop through each competition card
            for li_element in li_elements:
                try:
                    link_node = li_element.find_element(By.CSS_SELECTOR, "a[href*='/competitions/']")
                    link = link_node.get_attribute("href")
                    name = link_node.get_attribute("aria-label")
                    
                    # Prize extraction (optional)
                    prize = 0
                    try:
                        prize_node = li_element.find_element(By.XPATH, ".//a/following-sibling::div//div[contains(text(), '$')]")
                        prize_text = prize_node.text
                        digits_only = re.sub(r"[^\d]", "", prize_text)
                        if digits_only:
                            prize = int(digits_only)
                    except NoSuchElementException:
                        pass
                    
                    if name and link:
                        results.append({"name": name, "link": link, "prize": prize, "section": section_name})

                    if section_limit and section_limit > 0 and sum(1 for r in results if r.get("section") == section_name) >= section_limit:
                        reached_limit = True
                        break

                except (NoSuchElementException, StaleElementReferenceException):
                    continue
            
            if reached_limit:
                print(f"🟡 Limit of {section_limit} for {section_name} reached on page {page_number}. Stopping {section_name}.")
                save_progress(page_number, section_name)
                break
            
            # Save after successfully scraping a full page
            save_progress(page_number, section_name)
            
            # Pagination
            try:
                next_page_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Go to next page']")
                driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", next_page_button)
                time.sleep(0.5)
                next_page_button.click()
                print("✅ Navigating to next page...")

                time.sleep(1)
                wait.until(EC.visibility_of_element_located(list_container_locator))
                page_number += 1

            except (TimeoutException, NoSuchElementException):
                print(f"✅ No more pages found for {section_name}.")
                break

        except Exception as e:
            print(f"⚠️ An error occurred on {section_name} page {page_number}: {e}")
            break

# Scrape Featured
click_section("Featured")
scrape_current_listing("Featured", args.featured_limit)

# Scrape Research
driver.get("https://www.kaggle.com")
print("✅ Returned to Kaggle home.")
wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Competitions"))).click()
print("✅ Clicked on Competitions tab.")
click_section("Research")
scrape_current_listing("Research", args.research_limit)

# 10. Save the final results
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\n✅ Extracted a total of {len(results)} competitions (Featured: {sum(1 for r in results if r.get('section')=='Featured')}, Research: {sum(1 for r in results if r.get('section')=='Research')}) and saved to {output_path}")

# driver.quit()