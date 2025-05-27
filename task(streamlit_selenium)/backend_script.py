from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import time
import pandas as pd
from pathlib import Path
try:
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
except ImportError:
    print("webdriver-manager not installed. Falling back to manual WebDriver if available.")

def call(query='company'):
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    query = quote(query.strip())  

    output_dir = Path(__file__).resolve().parent
    output_file = output_dir / "company_data.csv"

    # Headless Edge 

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # project directory
    manual_driver_path = output_dir / "msedgedriver.exe"
    if manual_driver_path.exists():
        print(f"Using manual WebDriver at {manual_driver_path}")
        service = Service(str(manual_driver_path))
    else:
        try:
            service = Service(EdgeChromiumDriverManager().install())
        except Exception as e:
            raise Exception(f"Failed to initialize Edge WebDriver: {str(e)}. Try placing msedgedriver.exe in {output_dir}.")

    try:
        driver = webdriver.Edge(service=service, options=options)
    except Exception as e:
        raise Exception(f"Failed to initialize Edge WebDriver: {str(e)}")

    data = []
    try:
        print(f"Searching for: {query}")
        driver.get(f"https://www.google.com/maps/search/{query}")
        
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
            )
        except Exception as e:
            print(f"Error loading Google Maps page for query '{query}': {str(e)}")
            return []

        scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
        max_scrolls = 1
        scroll_count = 0
        last_height = 0

        #  scrolling
        while scroll_count < max_scrolls:
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            new_height = driver.execute_script('return arguments[0].scrollHeight', scrollable_div)
            if new_height == last_height:
                break
            last_height = new_height
            scroll_count += 1
            print(f"Scroll {scroll_count}/{max_scrolls}")


        cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        print(f"Found {len(cards)} cards")

        if not cards:
            print(f"No results found for query '{query}'. Try a more specific term.")
            return []

        for i, card in enumerate(cards):
            try:
                # Scroll to card and click
                driver.execute_script("arguments[0].scrollIntoView();", card)
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(card))
                card.click()
                time.sleep(3)

                #  Name
                try:
                    name = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "DUwDvf"))
                    ).text.strip()
                except:
                    name = "N/A"

                #  Address
                try:
                    address_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//button[@data-item-id="address"]//div[contains(@class, "Io6YTe")]'))
                    )
                    address = address_elem.text.strip()
                except:
                    address = "N/A"

                #  Phone
                try:
                    phone_button = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//button[starts-with(@aria-label, "Phone:")]'))
                    )
                    phone = phone_button.get_attribute("aria-label").replace("Phone:", "").strip()
                except:
                    phone = "N/A"

                data.append({"Name": name, "Address": address, "Phone": phone})
                print(f"{i+1}. {name} | {address} | {phone}")

                try:
                    back_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "v0nnCb"))
                    )
                    back_button.click()
                    time.sleep(2)
                except:
                    print(f"Could not return to list view for card {i+1}")
                    pass

            except Exception as e:
                print(f"Error processing card {i+1}: {str(e)}")
                continue

        # Save to CSV
        if data:
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False)
            print(f"\n Data saved to {output_file}")
        else:
            print("\n No data collected")

        return data

    except Exception as e:
        print(f"Unexpected error in backend: {str(e)}")
        return []

    finally:
        driver.quit()