import subprocess
import time
import psutil
import sys
from datetime import datetime

print("Using Python executable:", sys.executable)
print("Python version:", sys.version)

# Paths
chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"  # Update as needed
chrome_profile = "C:\\Users\\Administrator\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"  # Replace with your profile path
debugging_port = 9222
error_log_path = "error_log.txt"  # Path to the error log file

def log_error(error_message):
    """Log error with timestamp to error_log.txt."""
    with open(error_log_path, "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {error_message}\n")

def kill_process_by_name(name):
    """Kill all processes that contain the specified name."""
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if name.lower() in (process.info['name'] or '').lower() or name.lower() in ' '.join(process.info.get('cmdline', [])).lower():
                print(f"Attempting to terminate process: {process.info['name']} (PID: {process.info['pid']})")
                process.terminate()
                process.wait(timeout=5)
                print(f"Terminated process: {process.info['name']} (PID: {process.info['pid']})")
        except Exception as e:
            error_message = f"Error terminating process {name}: {e}"
            print(error_message)
            log_error(error_message)

def kill_chrome_debug_process():
    """Kill any running Chrome processes started for debugging."""
    for process in psutil.process_iter(['name', 'cmdline']):
        try:
            if process.info['name'] == "chrome.exe" and f"--remote-debugging-port={debugging_port}" in " ".join(process.info['cmdline']):
                process.terminate()
                process.wait(timeout=5)  # Ensure process terminates
                print(f"Killed Chrome debug process: PID {process.pid}")
        except Exception as e:
            error_message = f"Error killing Chrome debug process: {e}"
            print(error_message)
            log_error(error_message)

def start_chrome_debug_browser():
    """Start Chrome in debug mode."""
    try:
        print("Starting Chrome debug browser...")
        subprocess.Popen([
            chrome_path,
            f"--remote-debugging-port={debugging_port}",
            f"--user-data-dir={chrome_profile}"
        ])
        time.sleep(5)  # Give Chrome time to start
    except Exception as e:
        error_message = f"Error starting Chrome debug browser: {e}"
        print(error_message)
        log_error(error_message)

while True:
    try:
        # Kill Astrill VPN process
        print("Stopping Astrill VPN...")
        kill_process_by_name("Astrill")

        # Kill any existing Chrome debug processes
        print("Stopping Chrome debug browser...")
        kill_chrome_debug_process()

        # Restart Chrome debug browser
        # start_chrome_debug_browser()

        print("Starting the scraper...")
        # Start the scraper process
        scraper_script_path = "scraper.py"

        with open(scraper_script_path, "r") as script_file:
            code = script_file.read()
            exec(code)  # Execute the scraper code

        print("Scraper process exited. Restarting in 10 seconds...")
        time.sleep(10)
    except Exception as e:
        error_message = f"Monitor encountered an error: {e}"
        print(error_message)
        log_error(error_message)
        print("Retrying in 10 seconds...")
        time.sleep(10)
