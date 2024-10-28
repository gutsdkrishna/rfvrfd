import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service

# Initialize the WebDriver (set the correct path to your WebDriver)
webdriver_path = '/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/selenium/webdriver/common/macos/geckodriver'
driver = webdriver.Firefox(service=Service(webdriver_path))
wait_time = 30  # Adjust this wait time if necessary

# Set the number of pages to scrape
pages_to_scrape = 2  # Adjust as needed

# Function to log in and set 100 rows per page
def login_and_setup():
    driver.get('https://pradan.issdc.gov.in/ch2/protected/browse.xhtml?id=class')
    username = "krishna6773"
    password = "S@ntosh!777"
    
    # Log in
    WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.ID, 'password').submit()
    time.sleep(10)  # Added pause to wait for rows to load after selecting 100

    # Set rows per page to 100
    set_rows_per_page()

# Function to set rows per page to 100 and wait for overlay to disappear
def set_rows_per_page():
    select = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.ID, 'tableForm:lazyDocTable:j_id2'))
    )
    
    # Scroll to the dropdown and wait until it's clickable
    driver.execute_script("arguments[0].scrollIntoView();", select)
    WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable((By.ID, 'tableForm:lazyDocTable:j_id2')))
    
    # Select 100 rows per page and wait
    Select(select).select_by_value("100")
    time.sleep(10)  # Added pause to wait for rows to load after selecting 100
    
    # Wait for overlay to disappear
    WebDriverWait(driver, wait_time).until_not(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#tableForm\\:j_idt181_modal"))
    )

# Function to wait for all 100 rows to load
def wait_for_rows_to_load():
    loaded = False
    while not loaded:
        rows = driver.find_elements(By.CSS_SELECTOR, "#tableForm\\:lazyDocTable_data tr")
        if len(rows) >= 100:
            loaded = True
        else:
            print(f"Only {len(rows)} rows loaded; waiting for 100.")
            time.sleep(2)  # Wait and check again

# Function to scrape URLs from the table rows
def scrape_links():
    wait_for_rows_to_load()  # Ensure all rows are loaded
    links = []
    rows = driver.find_elements(By.CSS_SELECTOR, "#tableForm\\:lazyDocTable_data tr")

    for row in rows:
        try:
            xml_link = row.find_element(By.CSS_SELECTOR, "a[href*='.xml']").get_attribute("href")
            fits_link = row.find_element(By.CSS_SELECTOR, "a[href*='.fits']").get_attribute("href")
            links.append({"xml_link": xml_link, "fits_link": fits_link})
        except:
            print("Link not found in row, skipping.")
            continue

    return links

# Function to click 'Next' button, handling overlay if present
def go_to_next_page():
    try:
        # Wait until the overlay disappears if present
        WebDriverWait(driver, wait_time).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#tableForm\\:j_idt181_modal"))
        )
        
        # Click "Next" button
        next_button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#tableForm\\:lazyDocTable_paginator_bottom .ui-paginator-next"))
        )
        next_button.click()
        
        # Wait for the page to load and re-select 100 rows
        set_rows_per_page()
    except Exception as e:
        print(f"Could not go to the next page: {e}")

# Run the scraper with pagination
def run_scraper(pages_to_scrape):
    all_links = []
    login_and_setup()
    
    for page in range(pages_to_scrape):
        print(f"Scraping page {page + 1}")
        page_links = scrape_links()
        all_links.extend(page_links)
        
        # Save links after each page to ensure progress is recorded
        with open('scraped_links.json', 'w') as f:
            json.dump(all_links, f, indent=4)
        
        # Navigate to the next page unless it’s the last one
        if page < pages_to_scrape - 1:
            go_to_next_page()

    print("Scraping complete. Data saved in 'scraped_links.json'.")

# Start scraping
run_scraper(pages_to_scrape)

# Close the browser
driver.quit()
