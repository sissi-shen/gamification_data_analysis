import json
import os
import re
import time
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException, StaleElementReferenceException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

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

# 6. Search for "data science"
wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search competitions']"))).send_keys("data science")
print("✅ Searched for 'data science'.")


# --- FILTERING LOGIC REMOVED ---
# The following lines that applied the monetary filter have been removed.
print("✅ Monetary filter skipped to include all competition types.")


# 9. Main Extraction and Pagination Loop
results = []
page_number = 1
list_container_locator = (By.CSS_SELECTOR, "ul[role='list']")

while True:
    print(f"\n--- Scraping Page {page_number} ---")
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
                
                # --- MODIFIED PRIZE LOGIC ---
                # Gracefully handle competitions without a monetary prize
                prize = 0
                try:
                    prize_node = li_element.find_element(By.XPATH, ".//a/following-sibling::div//div[contains(text(), '$')]")
                    prize_text = prize_node.text
                    digits_only = re.sub(r"[^\d]", "", prize_text)
                    if digits_only:
                        prize = int(digits_only)
                except NoSuchElementException:
                    # This is expected for "Knowledge" competitions, prize remains 0
                    pass
                
                # Add the competition to results regardless of prize amount
                if name and link:
                    results.append({"name": name, "link": link, "prize": prize})

            except (NoSuchElementException, StaleElementReferenceException):
                continue
        
        # --- DEFINITIVE PAGINATION LOGIC ---
        try:
            next_page_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Go to next page']")
            driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", next_page_button)
            time.sleep(0.5)
            next_page_button.click()
            print("✅ Navigating to next page...")

            time.sleep(1)
            wait.until(EC.url_contains(f"page={page_number + 1}"))
            wait.until(EC.visibility_of_element_located(list_container_locator))
            
            page_number += 1

        except (TimeoutException, NoSuchElementException):
            print("✅ No more pages found. Scraping complete.")
            break

    except Exception as e:
        print(f"⚠️ An error occurred on page {page_number}: {e}")
        break

# 10. Save the final results
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "kaggle_competitions_all_types.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\n✅ Extracted a total of {len(results)} competitions and saved to {output_path}")

# driver.quit()