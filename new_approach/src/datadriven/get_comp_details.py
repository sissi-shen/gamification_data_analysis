import argparse
import json
import os
import re
import sys
import time
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, TimeoutException, StaleElementReferenceException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Configuration - Parse command line arguments
parser = argparse.ArgumentParser(description='Scrape DataDriven competition details')
parser.add_argument('--limit', type=int, help='Limit the number of competitions to process (default: process all)')
args = parser.parse_args()

COMPETITIONS_TO_PROCESS = args.limit
if COMPETITIONS_TO_PROCESS:
    print(f"✅ Using limit: {COMPETITIONS_TO_PROCESS}")
else:
    print("✅ No limit provided. Will process all competitions")

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
    print(f"Output will be written to {output_path}, overwriting if it exists.")

except FileNotFoundError:
    print(f"❌ Error: The file {input_path} was not found.")
    driver.quit()
    exit()

def flatten_competitions(competitions):
    """
    Flatten competitions structure to include all standalone competitions and child competitions
    Excludes parent links where available (only keeps child links)
    """
    flattened = []
    
    for competition in competitions:
        # If competition has children, add only the children (not the parent)
        if 'children' in competition and competition['children']:
            for child in competition['children']:
                flattened.append({
                    'name': child['name'],
                    'link': child['link'],
                    'prize': child['prize'],
                    'parent_name': competition['name'],  # Keep track of parent for reference
                    'parent_link': competition['link']   # Keep track of parent link for reference
                })
        else:
            # Standalone competition without children
            flattened.append({
                'name': competition['name'],
                'link': competition['link'],
                'prize': competition['prize'],
                'parent_name': None,
                'parent_link': None
            })
    
    return flattened

def extract_navigation_content(competition_url):
    """
    Extract content from all navigation sections except leaderboard results
    Simple approach: collect all hrefs first, then navigate to each one
    """
    context_parts = []
    sections_successfully_scraped = 0
    
    try:
        driver.get(competition_url)
        print(f"  - Opened competition page: {competition_url}")
        
        # Wait for page to load
        time.sleep(1)
        
        # Find navigation section and collect all links
        nav_links_data = []
        
        try:
            nav_list = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-unstyled.m-0")))
            nav_links = nav_list.find_elements(By.TAG_NAME, "a")
            print("  ✓ Navigation section found")
            
            # Collect all link data while we're still on the page
            for link in nav_links:
                try:
                    link_text = link.text.strip()
                    link_href = link.get_attribute("href")
                    nav_links_data.append((link_text, link_href))
                except Exception as e:
                    continue
                    
        except TimeoutException:
            print("  ✗ Could not find navigation section")
            return ""
        
        if not nav_links_data:
            print("  ✗ No navigation links found")
            return ""
        
        print(f"  📋 Found {len(nav_links_data)} navigation links")
        
        # Now process each link by navigating directly to it
        for link_text, link_href in nav_links_data:
            # Skip leaderboard results, data download, and participants
            skip_terms = ["leaderboard results", "data download", "participants"]
            should_skip = any(term in link_text.lower() for term in skip_terms) or "leaderboard" in link_href.lower()
            
            if should_skip:
                print(f"  ⏭️  Skipping: {link_text}")
                continue
            
            # Skip empty links
            if not link_text or not link_href:
                continue
            
            try:
                # Handle relative URLs by converting to absolute URLs
                if link_href.startswith('/'):
                    base_url = f"{urlparse(competition_url).scheme}://{urlparse(competition_url).netloc}"
                    full_url = urljoin(base_url, link_href)
                else:
                    full_url = link_href
                
                # Navigate directly to the URL
                driver.get(full_url)
                time.sleep(1)
                
                # Extract content
                try:
                    content_area = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[role='main'], main, .main-content, .content")))
                    full_text = content_area.text
                except TimeoutException:
                    # Fallback to body text
                    full_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Filter content
                lines = full_text.split('\n')
                filtered_lines = [line.strip() for line in lines if len(line.strip().split()) > 5]
                processed_text = '\n'.join(filtered_lines)
                
                if processed_text.strip():
                    context_parts.append(f"--- {link_text.upper()} ---\n{processed_text}")
                    print(f"  ✅ {link_text} ({len(processed_text)} chars)")
                    sections_successfully_scraped += 1
                else:
                    print(f"  ⚠️  {link_text} (no content)")
                    
            except Exception as e:
                print(f"  ❌ {link_text} (error)")
                continue
        
        print(f"  📊 Scraped {sections_successfully_scraped}/{len(nav_links_data)} sections")
                
    except Exception as e:
        print(f"  ❌ Error extracting navigation content: {e}")
    
    return "\n\n".join(context_parts)

# Flatten the competitions structure
flattened_competitions = flatten_competitions(competitions)
print(f"✅ Flattened {len(competitions)} competitions into {len(flattened_competitions)} individual competitions to process")

# Apply limit AFTER flattening
if COMPETITIONS_TO_PROCESS is not None:
    flattened_competitions = flattened_competitions[:COMPETITIONS_TO_PROCESS]
    print(f"✅ Applied limit: processing first {len(flattened_competitions)} flattened competitions")
else:
    print(f"✅ No limit applied: processing all {len(flattened_competitions)} flattened competitions")

# Main scraping loop
total_competitions = len(flattened_competitions)
successfully_scraped = 0

for index, competition in enumerate(flattened_competitions):
    print(f"\n({index + 1}/{total_competitions}) Scraping '{competition['name']}'...")
    
    if competition['parent_name']:
        print(f"  - Parent competition: {competition['parent_name']}")
    
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
        json.dump(flattened_competitions, f, indent=4, ensure_ascii=False)
    print(f"  💾 Progress saved. Successfully scraped: {successfully_scraped}/{index + 1}")

print(f"\n🎉 Scraping complete! Successfully scraped {successfully_scraped}/{total_competitions} competitions.")
print(f"Results saved to: {output_path}")
print(f"\nUsage: python get_comp_details.py [--limit N]")
print(f"  - No limit: Process all competitions")
print(f"  - With limit: Process first N competitions (e.g., python get_comp_details.py --limit 5)")

driver.quit()
