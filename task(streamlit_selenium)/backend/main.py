from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time
import pandas as pd

# Headless Edge setup
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Edge(options=options)

query = "company"
driver.get(f"https://www.google.com/maps/search/{query}/@28.9080571,78.4638268,12z/data=!3m1!4b1?entry=ttu")

time.sleep(5)

data = []

#
scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
for _ in range(2):  # Scroll a few times
    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
    time.sleep(2)

cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")

for i in range(len(cards)):
    try:
        cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")  # Re-fetch the list each time
        card = cards[i]

        driver.execute_script("arguments[0].scrollIntoView();", card)
        time.sleep(1)
        card.click()
        time.sleep(4)

        # Extract Name
        try:
            name = driver.find_element(By.CLASS_NAME, "DUwDvf").text
        except:
            name = "N/A"

        # Extract Address
        try:
            address_elem = driver.find_element(By.XPATH, '//button[@data-item-id="address"]//div[contains(@class,"Io6YTe")]')
            address = address_elem.text.strip()
        except:
            address = "N/A"

        # Extract Phone
        try:
            phone_button = driver.find_element(By.XPATH, '//button[starts-with(@aria-label, "Phone:")]')
            phone = phone_button.get_attribute("aria-label").replace("Phone:", "").strip()
        except:
            phone = "N/A"

        data.append({"Name": name, "Address": address, "Phone": phone})
        print(f"{i+1}. {name} | {address} | {phone}")

        # Return to the list view
        try:
            back_button = driver.find_element(By.CLASS_NAME, "v0nnCb")
            back_button.click()
            time.sleep(3)
        except:
            pass

    except Exception as e:
        print(f"Error on card {i+1}: {e}")
        continue

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("company_data.csv", index=False)
print("\n✅ Data saved to company_data.csv")

driver.quit()
