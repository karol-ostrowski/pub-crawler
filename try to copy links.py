from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

driver_path = r'C:\webdrivers\chromedriver.exe'
service = Service(driver_path) 
driver = webdriver.Chrome(service=service)

# Load the webpage
url = "https://www.pw.edu.pl"
driver.get(url)
time.sleep(2)
url = "https://www.example.com"
driver.get(url)
time.sleep(2)
# Get the full HTML source code of the page
#html_source = driver.page_source

# Optionally, save the HTML to a file
'''with open("page_source.html", "w", encoding="utf-8") as file:
    file.write(html_source)'''

# Close the browser when done
driver.quit()