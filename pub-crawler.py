from bs4 import BeautifulSoup
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from random import uniform
from openai import OpenAI
import pandas as pd
import time
import pyperclip
import sys

def scrape_search_results(driver, query, page_numer):
    """
    space = +
    " = %22
    ( = %28
    ) = %29
    """
    query = query.replace(" ", "+")
    query = query.replace("\"", "%22")
    query = query.replace("(", "%28")
    query = query.replace(")", "%29")
    url = f"https://scholar.google.com/scholar?start={page_numer}0&q={query}&hl=pl&as_sdt=0,5"
    driver.get(url)
    time.sleep(uniform(2, 3))
    html_source = driver.page_source
    return html_source

def gather_urls(scraped_html, dataframe):
    soup = BeautifulSoup(scraped_html, "html.parser")
    if not len(soup):
        return 1
    for url in soup.find_all("a", href=True):
        if ("https" in url["href"] and 
            "google" not in url["href"] and 
            "pdf" not in url["href"]):
            dataframe.loc[len(dataframe)] = [url["href"]]

    return dataframe

def process_cookies_button_texts():
    if (path / "cookies_accept_button_texts.csv").exists():
        cookies_df = pd.read_csv(path / "cookies_accept_button_texts.csv")
    else:
        cookies_df = pd.DataFrame(columns=["button_text"])
        cookies_df.loc[len(cookies_df)] = ["'Accept all cookies'"]
        cookies_df.loc[len(cookies_df)] = ["'Accept All Cookies'"]
        cookies_df.loc[len(cookies_df)] = ["'I Accept'"]
        cookies_df.loc[len(cookies_df)] = ["'Accept cookies'"]
        cookies_df.to_csv(path / "cookies_accept_button_texts.csv", index=False)

    processed_cookies_button_texts = "//button["
    for button_text in cookies_df["button_text"]:
        processed_cookies_button_texts += f"contains(text(), {button_text}) or "
    processed_cookies_button_texts = processed_cookies_button_texts[:-4]
    processed_cookies_button_texts += "]"

    return processed_cookies_button_texts

def get_contents(url, driver, processed_cookies_button_texts, operating_system):                          
    driver.get(url)
    time.sleep(uniform(2, 3))

    try:
        accept_button = driver.find_element(By.XPATH, processed_cookies_button_texts)
        accept_button.click()
    except NoSuchElementException:
        if (path / "cache" / "cookies_button_not_found.csv").exists():
            cookies_button_not_found_df = pd.read_csv(path / "cache" / "cookies_button_not_found.csv", header=0, index_col=False)
        else:
            cookies_button_not_found_df = pd.DataFrame(columns=["url"])
        cookies_button_not_found_df.loc[len(cookies_button_not_found_df)] = [url]
        cookies_button_not_found_df.to_csv(path / "cache" / "cookies_button_not_found.csv", index=False)

    body = driver.find_element("tag name", "body")

    if operating_system == "macos":
        body.send_keys(Keys.COMMAND, 'a')
        time.sleep(uniform(0.2, 0.3))
        body.send_keys(Keys.COMMAND, 'c')
        time.sleep(uniform(0.1, 0.2))     

    elif operating_system == "windows":
        body.send_keys(Keys.CONTROL, 'a')
        time.sleep(uniform(0.2, 0.3))
        body.send_keys(Keys.CONTROL, 'c')
        time.sleep(uniform(0.1, 0.2))
    
    else:
        raise "OSInfoError"

    content = pyperclip.paste()

    time.sleep(uniform(1, 2))
    return content

def process_with_openai_api(content, additional_requirements):
    client = OpenAI()

    completion1 = client.chat.completions.create(
    model="gpt-4o-mini",
    max_completion_tokens=3000,
    messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": f"After this sentence ends I will provide you a text with a lot of noise and an abstract of a scientific paper and your job is to provide the abstract exactly as it is, 1:1 without any changes and additional words and comments.\n{content}"}])
    
    #compose requirements
    reqs = str()
    for i, v in enumerate(additional_requirements):
        reqs += f"{i + 1}. {v} "

    completion2 = client.chat.completions.create(
    model="gpt-4o-mini",
    max_completion_tokens=1000,
    messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": f"given this response in double square brackets [[{completion1.choices[0].message}]], do you think this abstract matches requirements provided in the single square brackets?:[{reqs[:-1]}] your answer has to be just one word, either yes or no"}])

    return completion1.choices[0].message.content, completion2.choices[0].message.content

if __name__ == "__main__":
    path = Path(__file__).parent
    if (path / "chromedriver_path.txt").exists():
        with open(path / "chromedriver_path.txt", "r") as f:
            ChromeDriverPath = f.read()
    else:
        raise "MissingChromeDriverPathError"
    
    driver_path = Path(ChromeDriverPath)
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

    cache_path = Path(path / "cache")
    cache_path.mkdir(exist_ok=True)

    if (path / "cache" / "results.csv").exists():
        results_df = pd.read_csv(path / "cache" / "results.csv", header=0, index_col=False)
    else:
        results_df = pd.DataFrame(columns=["abstract", "if_relevant", "url"])


    if not (path / "cache" / "next_page.txt").exists():
        (path / "cache" / "next_page.txt").touch(exist_ok=True)
    with open(path / "cache" / "next_page.txt", "r") as f:
        content = f.read().strip()
        if content:
            next_page = int(content)
        else:
            next_page = 0
    user_input_query = sys.argv[1]
    additional_requirements = sys.argv[2:]

    if (path / "cache" / "urls.csv").exists():
        urls_df = pd.read_csv(path / "cache" / "urls.csv", header=0, index_col=False)
    else:
        urls_df = pd.DataFrame(columns=["url"])

    processed_cookies_button_texts = process_cookies_button_texts()

    if (path / "os.txt").exists():
        with open(path / "os.txt", "r") as f:
            operating_system = f.read()
    else:
        raise "MissingOSPathError"

    while True:
        if not len(urls_df):
            scraped_html = scrape_search_results(driver=driver,
                                                query=user_input_query,
                                                page_numer=str(next_page))
            next_page += 1
            with open(path / "cache" / "next_page.txt", "w") as f:
                f.write(str(next_page))
            urls_df = gather_urls(scraped_html=scraped_html, dataframe=urls_df)
            if not isinstance(urls_df, pd.DataFrame):
                break
            urls_df.to_csv(path / "cache" / "urls.csv", index=False)
        while len(urls_df):
            url = urls_df["url"][0]
            urls_df = urls_df.drop(index=0).reset_index(drop=True)
            urls_df.to_csv(path / "cache" / "urls.csv", index=False)
            content = get_contents(url=url,
                                   driver=driver,
                                   processed_cookies_button_texts=processed_cookies_button_texts[:10000],
                                   operating_system=operating_system)
            abstract, if_relevant = process_with_openai_api(content=content,
                                                            additional_requirements=additional_requirements)
            results_df.loc[len(results_df)] = [abstract, if_relevant, url]
            no_dups_results_df = results_df.drop_duplicates(subset=["abstract", "url"])
            sorted_no_dups_results_df = no_dups_results_df.sort_values(by=["if_relevant", "abstract"],
                                                                       ascending=[False, True])
            sorted_no_dups_results_df.to_csv("./cache/results.csv", index=False)
    
    driver.quit()