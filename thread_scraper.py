from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import urllib.parse
import re
import threading
import os
import time
from queue import Queue
from colorama import Fore, Style, init
import subprocess

# Initialize colorama
init(autoreset=True)

# Configuration
chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"  # Update if needed
chrome_profile = "C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"
debugging_port = 9222
num_pages = 100
output_dir = "emails"

# List of countries
countries = [
    "Denmark", "Austria", "Belgium", "Bulgaria", "Croatia", "Finland", "Iceland",
    "Italy", "Latvia", "Luxembourg", "Malta", "Netherlands", "Poland", "Romania", "Portugal", "Spain",
    "United States", "Mexico", "Panama", "Argentina", "Chile", "Colombia", "Ecuador", "Paraguay", "Australia",
    "New Zealand", "India", "Pakistan", "Japan", "Saudi Arabia", "UAE", "Kuwait", "Qatar", "Iran"
]

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Thread-safe queue for countries
country_queue = Queue()
for country in countries:
    country_queue.put(country)

def setup_driver():
    """Set up Selenium WebDriver with Chrome in debugging mode."""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debugging_port}")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def fetch_emails(driver, location, start_page=1):
    """Fetch emails from GitHub profiles for a specific location."""
    output_file = os.path.join(output_dir, f"email_addresses({location}).txt")

    # Load progress if available
    if os.path.exists(output_file):
        with open(output_file, "r") as file:
            processed_pages = len(file.readlines())
    else:
        processed_pages = 0

    total_emails = 0
    with open(output_file, "a") as file:
        for page_num in range(start_page, num_pages + 1):
            if page_num <= processed_pages:
                continue

            encoded_location = urllib.parse.quote(location)
            url = f"https://github.com/search?q=location%3A{encoded_location}&type=users&s=joined&o=desc&p={page_num}"
            driver.get(url)
            time.sleep(10)

            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "search-results-page"))
                )
            except Exception as e:
                print(Fore.RED + f"Error loading search results for page {page_num}: {e}")
                continue

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            profile_links = [a["href"] for a in soup.select("div.search-title a") if a.get("href")]

            for profile_link in profile_links:
                driver.get(f"https://github.com{profile_link}")
                time.sleep(10)
                profile_html = driver.page_source
                email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
                emails = re.findall(email_pattern, profile_html)
                for email in emails:
                    file.write(f"{email}\n")
                    print(f"{email} - {country}\n")
                    total_emails += 1

            # Display progress
            progress = (page_num / num_pages) * 100
            print(Fore.CYAN + f"{location}: {progress:.2f}% completed. Emails so far: {Fore.YELLOW}{total_emails}")

    # Remove duplicates
    with open(output_file, "r") as file:
        unique_emails = set(file.read().splitlines())

    with open(output_file, "w") as file:
        for email in unique_emails:
            file.write(f"{email}\n")

def worker():
    """Worker function to process countries from the queue."""
    driver = setup_driver()
    while not country_queue.empty():
        try:
            country = country_queue.get_nowait()
            print(Fore.GREEN + f"Processing country: {country}")
            fetch_emails(driver, country)
        except Exception as e:
            print(Fore.RED + f"Error processing {country}: {e}")
        finally:
            country_queue.task_done()
    driver.quit()

if __name__ == "__main__":
    # Start Chrome in debugging mode
    # os.system(f"{chrome_path} --remote-debugging-port={debugging_port} --user-data-dir={chrome_profile}")
    # Launch Chrome in debugging mode
    subprocess.Popen([
        chrome_path,
        f"--remote-debugging-port={debugging_port}",
        f"--user-data-dir={chrome_profile}"
    ])
    time.sleep(5)

    # Start worker threads
    num_threads = 1
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    print(Fore.MAGENTA + "Scraping completed.")