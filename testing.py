import sys
from pathlib import Path
import pandas as pd

path = Path(__file__).parent

if (path / "cookies_accept_button_texts.csv").exists():
    cookies_df = pd.read_csv(path / "cookies_accept_button_texts.csv")
else:
    cookies_df = pd.DataFrame(columns=["button_text"])
    cookies_df.loc[len(cookies_df)] = ["'Accept all cookies'"]
    cookies_df.loc[len(cookies_df)] = ["'Accept All Cookies'"]
    cookies_df.loc[len(cookies_df)] = ["'I Accept'"]
    cookies_df.loc[len(cookies_df)] = ["'Accept cookies'"]
#"//button[contains(text(), 'Accept all cookies') or contains(text(), 'I Accept') or contains(text(), 'Accept Cookies')]"
processed_button_texts = "//button["
for button_text in cookies_df["button_text"]:
    processed_button_texts += f"contains(text(), {button_text}) or "
processed_button_texts = processed_button_texts[:-4]
processed_button_texts += "]"

print(processed_button_texts)