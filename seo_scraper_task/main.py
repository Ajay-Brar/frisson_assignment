from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import pandas as pd
import time
import os


options = uc.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = uc.Chrome(options=options)
query = "web development companies"
driver.get(f"https://www.google.com/search?q={query}")
time.sleep(5)

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

data = []
seen = set()

results = soup.select("div.tF2Cxc") 
for idx, result in enumerate(results):
    title_tag = result.find('span',class_="VuuXrf")        
    link_tag = result.find("a")

    if title_tag and link_tag:
        name = title_tag.text.strip()
        url = link_tag.get("href")

        if name not in seen:
            seen.add(name)
            data.append({
                "Ranking": idx + 1,
                "Name": name,
                "Site": url
            })

print(f"Total companies scraped: {len(data)}")
print(data[:5])

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("seo_f.csv", index=False)
print("Scraping completed. Saved to:", os.path.abspath("seo.csv"))
