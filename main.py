import sys
import os
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib.parse
import re
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess

# List of countries to scrape
country_list = [
    "Denmark", "Austria", "Belgium", "Bulgaria", "Croatia", 
    "Finland", "Iceland", "Italy", "Latvia", "Luxembourg", "Malta", "Netherlands", "Poland", 
    "Romania", "Portugal", "Spain", "United States", "Mexico", "Panama", "Argentina", "Chile", 
    "Colombia", "Ecuador", "Paraguay", "Australia", "New Zealand", "India", "Pakistan", "Japan", 
    "Saudi Arabia", "UAE", "Kuwait", "Qatar", "Iran"
]

# File paths for tracking progress
last_page_file = "last_page.txt"
last_country_file = "last_country.txt"

# Function to read the last processed country
def get_last_country():
    if os.path.exists(last_country_file):
        with open(last_country_file, "r") as file:
            return file.read().strip()
    return None

# Function to save the last processed country
def save_last_country(country):
    with open(last_country_file, "w") as file:
        file.write(country)

# Function to read the last page index
def get_last_page():
    if os.path.exists(last_page_file):
        with open(last_page_file, "r") as file:
            return int(file.read().strip())
    return 1

# Function to save the last page index
def save_last_page(page):
    with open(last_page_file, "w") as file:
        file.write(str(page))

# Determine the starting country
last_country = get_last_country()
if last_country and last_country in country_list:
    start_country_index = country_list.index(last_country)
else:
    start_country_index = 0

# Path to Chrome executable
chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# Path to Chrome profile
chrome_profile = "C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"

# Remote debugging port
debugging_port = 9222

# Launch Chrome in debugging mode
subprocess.Popen([
    chrome_path,
    f"--remote-debugging-port={debugging_port}",
    f"--user-data-dir={chrome_profile}"
])

# Wait for Chrome to launch
time.sleep(5)

# Set up Selenium options
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

# Iterate through countries starting from the last processed one
for i in range(start_country_index, len(country_list)):
    country = country_list[i]
    print(f"Scraping data for country: {country}")

    # Save the current country to file
    save_last_country(country)

    # Open file for saving emails
    file_path = f"email_addresses({country}).txt"
    with open(file_path, "a") as file:
        last_page = get_last_page()

        # Scrape pages starting from the last processed page
        for page_num in range(last_page, 101):  # Example: Scrape the first 100 pages
            save_last_page(page_num)  # Save the current page number
            encoded_location = urllib.parse.quote(country)
            url = f"https://github.com/search?q=location%3A{encoded_location}&type=users&s=joined&o=desc&p={page_num}"
            driver.get(url)
            time.sleep(10)  # Adjust based on your network speed

            # Wait for search results to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "search-results-page"))
            )

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            divs = soup.find_all("div", class_="search-title")  # Update this based on actual link class

            print(f"Checking the HTML page for country {country}, page {page_num}...")

            for div in divs:
                link = div.find("a")
                if link:
                    username = link.get_text(strip=True)
                    user_url = link["href"]
                    print(f"Checking profile: {username} ({user_url})")

                    driver.get("https://github.com" + user_url)
                    time.sleep(10)  # Allow time for the profile page to load
                    profile_html = driver.page_source

                    # Find email addresses
                    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
                    emails = re.findall(email_pattern, profile_html)

                    if emails:
                        for email in emails:
                            print(f"Found email: {email}")
                            file.write(f"{email}\n")

        # Reset the last page to 1 for the next country
        save_last_page(1)

# Cleanup: Delete the last country file when all countries are processed
if os.path.exists(last_country_file):
    os.remove(last_country_file)

print("Scraping completed for all countries.")
driver.quit()
