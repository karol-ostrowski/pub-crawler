from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from pynput.keyboard import Key, Controller
from urllib.parse import urlparse
import time

"""
hallucinogens OR psychedelics OR psychedelic OR "lysergic acid diethylamide" OR psilocybin OR dimethyltryptamine OR "5-MeO-DMT" OR mescaline OR ayahuasca OR LSD) AND (("purpose in life" AND "PILS") OR ("meaning in life" AND "MLQ"
"""
#wymyslic cos ze jak sie wysypie to zeby nie trzeba bylo od poczatku leciec
def scrape_search_results(path):
    directory = Path(path / "scraped-htmls")
    directory.mkdir(exist_ok=True)

    return directory

def gather_urls(path):
    
    urls = set()

    for _, html_file in enumerate(list(path.glob("*.html"))):
        with open(html_file, "r", encoding="utf-8") as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")

        for url in soup.find_all("a", href=True):
            if ("https" in url["href"] and 
                "google" not in url["href"] and 
                "pdf" not in url["href"]):

                urls.add(url["href"])

    return urls

def get_contents(url, driver):
    
    keyboard = Controller()
                          
    try:
        driver.get('chrome://settings/content/clipboard')
        time.sleep(2)
        body = driver.find_element("tag name", "body")
        for i in range(4):
            body.send_keys(Keys.TAB)
            time.sleep(0.1)
        time.sleep(0.1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(0.1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(0.1)
        parsed_url = urlparse(url)
        if ("www.ncbi.nlm.nih.gov" not in parsed_url or
            "https://search.proquest.com/" not in parsed_url):
            root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        elif "www.ncbi.nlm.nih.gov" in parsed_url:
            root_url = "https://pmc.ncbi.nlm.nih.gov/"
        elif "https://search.proquest.com/" in parsed_url:
            root_url = "https://proquest.com/"
        keyboard.type(root_url)
        time.sleep(0.1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(0.1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(0.1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(0.1)

        driver.get(url)
        time.sleep(2)

        try:
            accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept all cookies') or contains(text(), 'Accept All Cookies') or contains(text(), 'I Accept') or contains(text(), 'Accept Cookies')]")
            accept_button.click()
        except NoSuchElementException:
            print("no cookies button found")

        body = driver.find_element("tag name", "body")
        body.send_keys(Keys.CONTROL, 'a')
        time.sleep(0.2)

        body.send_keys(Keys.CONTROL, 'c')
        time.sleep(0.1)      
      
        content = driver.execute_script("return navigator.clipboard.readText();")
        
        return content

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

def process_with_chat_gpt():
    pass

if __name__ == "__main__":
    path = Path(__file__).parent

    scraped_htmls_dir = scrape_search_results(path=path)
    urls = gather_urls(path=scraped_htmls_dir)
    for url in urls:
        print(url)
    print(len(urls))
    directory = Path(path / "page-contents")
    directory.mkdir(exist_ok=True)

    '''driver_path = r'C:\webdrivers\chromedriver.exe'
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    for index, url in enumerate(urls):
        content = get_contents(url=url, driver=driver)[:10000]
        with open(Path(path / "page-contents" / f"contents{index + 1}.txt"), 'w', encoding='utf-8') as file:
            file.write(content)'''