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

# Configuration
COMPETITIONS_TO_PROCESS = 2  # Start with 2 for testing

# Script Setup
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

# Load competition data
input_path = "/Users/manikeshmakam/Endgame 2.0/ethicalAI/data/datadriven/inputs/datadriven_competitions_all_types.json"
output_path = "/Users/manikeshmakam/Endgame 2.0/ethicalAI/data/datadriven/inputs/datadriven_competitions_final.json"

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

def extract_navigation_content(competition_url):
    """
    Extract content from all navigation sections except leaderboard results
    """
    context_parts = []
    
    try:
        driver.get(competition_url)
        print(f"  - Opened competition page: {competition_url}")
        
        # Wait for page to load
        time.sleep(3)
        
        # Look for navigation section
        try:
            # First try to find the navigation section with h2
            nav_header = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[text()='Navigation']")))
            print("  - Found Navigation section")
            
            # Find the navigation list
            nav_list = driver.find_element(By.XPATH, "//h2[text()='Navigation']/following-sibling::ul")
            nav_links = nav_list.find_elements(By.TAG_NAME, "a")
            
            print(f"  - Found {len(nav_links)} navigation links")
            
            for link in nav_links:
                link_text = link.text.strip()
                link_href = link.get_attribute("href")
                
                # Skip leaderboard results
                if "leaderboard" in link_text.lower() or "results" in link_text.lower():
                    print(f"  - Skipping leaderboard link: {link_text}")
                    continue
                
                print(f"  - Processing navigation link: {link_text}")
                
                try:
                    # Click the navigation link
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(2)
                    
                    # Extract content from the main content area
                    content_area = driver.find_element(By.CSS_SELECTOR, "div[role='main'], main, .main-content, .content")
                    content_text = content_area.text
                    
                    # Filter content similar to Kaggle script
                    lines = content_text.split('\n')
                    filtered_lines = [line.strip() for line in lines if len(line.strip().split()) > 5]
                    processed_text = '\n'.join(filtered_lines)
                    
                    if processed_text.strip():
                        context_parts.append(f"--- {link_text.upper()} ---\n{processed_text}")
                        print(f"    ✅ Captured content for '{link_text}'")
                    else:
                        print(f"    ⚠️ No substantial content found for '{link_text}'")
                        
                except Exception as e:
                    print(f"    ❌ Error processing '{link_text}': {e}")
                    continue
                    
        except TimeoutException:
            print("  - Navigation section not found, trying alternative approach")
            
            # Alternative approach: look for competition links directly
            try:
                # Look for competition-specific links in the page
                competition_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/competitions/']")
                
                for link in competition_links:
                    link_text = link.text.strip()
                    link_href = link.get_attribute("href")
                    
                    # Skip if it's the current page or leaderboard
                    if (link_href == competition_url or 
                        "leaderboard" in link_text.lower() or 
                        "results" in link_text.lower() or
                        not link_text):
                        continue
                    
                    print(f"  - Processing alternative link: {link_text}")
                    
                    try:
                        driver.execute_script("arguments[0].click();", link)
                        time.sleep(2)
                        
                        # Extract content
                        content_area = driver.find_element(By.CSS_SELECTOR, "div[role='main'], main, .main-content, .content")
                        content_text = content_area.text
                        
                        # Filter content
                        lines = content_text.split('\n')
                        filtered_lines = [line.strip() for line in lines if len(line.strip().split()) > 5]
                        processed_text = '\n'.join(filtered_lines)
                        
                        if processed_text.strip():
                            context_parts.append(f"--- {link_text.upper()} ---\n{processed_text}")
                            print(f"    ✅ Captured content for '{link_text}'")
                        
                    except Exception as e:
                        print(f"    ❌ Error processing alternative link '{link_text}': {e}")
                        continue
                        
            except Exception as e:
                print(f"  ❌ Alternative approach also failed: {e}")
                
    except Exception as e:
        print(f"  ❌ Error extracting navigation content: {e}")
    
    return "\n\n".join(context_parts)

# Main scraping loop
total_competitions = len(competitions)
successfully_scraped = 0

for index, competition in enumerate(competitions):
    print(f"\n({index + 1}/{total_competitions}) Scraping '{competition['name']}'...")
    
    try:
        context = extract_navigation_content(competition['link'])
        
        # Add context field to existing competition data
        competition['context'] = context if context.strip() else "No content extracted"
        
        if context.strip():
            successfully_scraped += 1
            print(f"  ✅ Successfully scraped content for '{competition['name']}'")
        else:
            print(f"  ❌ No content extracted for '{competition['name']}'")
            
    except Exception as e:
        print(f"  ❌ Error scraping '{competition['name']}': {e}")
        competition['context'] = f"Error: {e}"
    
    # Save progress after every competition
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(competitions, f, indent=4, ensure_ascii=False)
    print(f"  💾 Progress saved. Successfully scraped: {successfully_scraped}/{index + 1}")

print(f"\n🎉 Scraping complete! Successfully scraped {successfully_scraped}/{total_competitions} competitions.")
print(f"Results saved to: {output_path}")

driver.quit()
