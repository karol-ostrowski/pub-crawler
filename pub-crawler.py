from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from random import uniform
import pandas as pd
import time
import pyperclip

"""
hallucinogens OR psychedelics OR psychedelic OR "lysergic acid diethylamide" OR psilocybin OR dimethyltryptamine OR "5-MeO-DMT" OR mescaline OR ayahuasca OR LSD) AND (("purpose in life" AND "PILS") OR ("meaning in life" AND "MLQ"
"""
#wymyslic cos ze jak sie wysypie to zeby nie trzeba bylo od poczatku leciec
def scrape_search_results(driver, query, page_numer):
    #TODO
    #process seach query so it can be pasted into url
    url = f"https://scholar.google.com/scholar?start={page_numer}0&q={query}&hl=pl&as_sdt=0,5"
    driver.get(url)
    html_source = driver.page_source

    return html_source

def gather_urls(scraped_html):
    urls = set()
    soup = BeautifulSoup(scraped_html, "html.parser")
    for url in soup.find_all("a", href=True):
        if ("https" in url["href"] and 
            "google" not in url["href"] and 
            "pdf" not in url["href"]):
            urls.add(url["href"])

    return urls

def get_contents(url, driver):                          
    driver.get(url)
    time.sleep(uniform(2, 3))

    try:                                                        #to fajnie jakby bylo sczytywane z jakiegos pliku a nie bylo hardcoded
        accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept all cookies') or contains(text(), 'Accept All Cookies') or contains(text(), 'I Accept') or contains(text(), 'Accept Cookies')]")
        accept_button.click()
    except NoSuchElementException:
        print("no cookies button found")

    body = driver.find_element("tag name", "body")
    body.send_keys(Keys.CONTROL, 'a')
    time.sleep(uniform(0.2, 0.3))

    body.send_keys(Keys.CONTROL, 'c')
    time.sleep(uniform(0.1, 0.2))      
    
    content = pyperclip.paste()

    time.sleep(uniform(1, 2))
    return content

def process_with_openai_api(content):
    #TODO
    return ("abstract-text", "yes/no")

if __name__ == "__main__":
    path = Path(__file__).parent
    driver_path = r'C:\webdrivers\chromedriver.exe' #to sie powinno sczytywac skąds, np z pliku tekstowego
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    scraped_htmls_dir = Path(path / "scraped-htmls")
    scraped_htmls_dir.mkdir(exist_ok=True)
    page_contents_dir = Path(path / "page-contents")
    page_contents_dir.mkdir(exist_ok=True)
    results_df = pd.DataFrame(columns=["abstract", "if_relevant"])

    next_page = 0
    user_input_query = input("search query for google scholar:\n")
    while True:
        scraped_html = scrape_search_results(driver=driver,
                                            query=user_input_query,
                                            page_numer=str(next_page))
        next_page += 1
        urls = gather_urls(scraped_html=scraped_html)
        if len(urls) == 0:
            break
        for index, url in enumerate(urls):
            content = get_contents(url=url, driver=driver)[:10000]
            abstract, if_relevant = process_with_openai_api(content=content)
            results_df.loc[len(results_df)] = [abstract, if_relevant]
    
    driver.quit()
    no_dups_results_df = results_df.drop_duplicates(subset="abstract")
    sorted_no_dups_results_df = no_dups_results_df.sort_values(by=["if_relevant", "abstract"],
                                               ascending=[False, True])
    sorted_no_dups_results_df.to_csv("results.csv", index=False)