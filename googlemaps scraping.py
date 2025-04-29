import re
import time
import logging
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

# Output file name
output_file_name = 'googlemapResults.csv'

# Chrome options
chrome_options = Options()
# chrome_options.add_argument("--headless")  
user_agent = "ali/2021.44.30.15-b917dc"
chrome_options.add_argument(f"--user-agent={user_agent}")
driver = webdriver.Chrome(options=chrome_options)
actions = ActionChains(driver)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s : %(message)s"
)

def googlemapDetails():
    result = {"success": 0, "data": {}, "message": "", "error_code": "0"}
    driver.implicitly_wait(30)  # Max wait for page to load
    keyword_data = []

    keyword = input("Enter a keyword to search:")
    # Open URL
    try:
        driver.get(f"https://www.google.com/maps/search/{keyword}/")
        logging.info("URL loaded successfully.")
    except Exception as e:
        result["message"] = f"Can't load URL! {str(e)}"
        result["error_code"] = "1"
        logging.error(result)
        return result

    time.sleep(3)

    # load some data
    count = 0
    # increase number to load more results
    while count < 1:
        try: 
            data = driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK') # class of results
            count = count + 1
            
            for result in data:
                driver.execute_script("arguments[0].scrollIntoView(true)", result)
                time.sleep(0.5)

            time.sleep(2)

        except Exception as e:
            result["message"] = f"Can't load more results. {e}"
            result["error_code"] = "1.1"
            logging.error(result)

        except KeyboardInterrupt:
            break

    # Fetch all data
    try:
        responses = driver.find_elements(By.CSS_SELECTOR, "div.Nv2PK") # class of results
        logging.info(f"Fetched {len(responses)} results.")
    except Exception as e:
        result["message"] = f"Can't fetch results: {str(e)}"
        result["error_code"] = "2"
        logging.error(result)
        return result

    # Process each response
    if len(responses) > 0:
        for response in responses:

            # hover over element
            try:
                actions.move_to_element(response).perform()   
            except Exception as e:
                logging.warning(f"Could not move to element: {str(e)}")
                result["message"] = f"Couldn't move to element {e}"
                result["error_code"] = "2.1"
                return result

            # get name of response
            try:
                title = response.find_element(By.CSS_SELECTOR, "div.fontHeadlineSmall").text
            except Exception as e:
                title = "N/A"
                logging.warning(f"No title found: {str(e)}")

            # get link of response
            try:
                link_element = response.find_element(By.CSS_SELECTOR, 'div a.hfpxzc')
                link = link_element.get_attribute('href')
            except Exception as e:
                link = "N/A"
                logging.warning(f"No link found: {str(e)}")

            # get response ratings
            try:
                rating = response.find_element(By.CSS_SELECTOR, "span.MW4etd").text
            except Exception as e:
                rating = "N/A"
                logging.warning(f"No rating found: {str(e)}")

            # get no of reviews
            try:
                no_of_reviews = response.find_element(By.CSS_SELECTOR, "span.UY7F9").text
                no_of_reviews = no_of_reviews.replace("(", "").replace(")", "")
            except Exception as e:
                no_of_reviews = "N/A"
                logging.warning(f"No reviews found: {str(e)}")

            # get phone number
            try:
                link_element.click()
                elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"RcCsl"))) # class of similar blocks
                phone_number = "N/A"

                for element in elements:
                    content = element.text[1:] # to remove the  icon from phone_number
                    if re.match(r'^\+?[0-9\s\-\(\)]+$', content.strip()): 
                        phone_number = content.strip()
                        break

                logging.info(f"Number: {phone_number}\n\n")

            except Exception as e:
                phone_number = "N/A"
                logging.warning(f"No phone number found: {str(e)}")

            # Append data
            try:
                keyword_data.append([title, rating, no_of_reviews, phone_number, link])
                logging.info(f"Appended data for: {title}")
            except Exception as e:
                logging.warning(f"Error appending data to {output_file_name} : {e}")

    else:
        result["message"] = "No responses found!"
        result["error_code"] = "2.1"
        logging.error(result)
        return result

    # Write data to CSV file
    try:
        df = pd.DataFrame(keyword_data, columns=["Title", "Rating", "Reviews", "Phone Number", "Link"])
        df.to_csv(output_file_name, index=False, encoding='utf-8')
        logging.info(f"Data written to {output_file_name}")
    except Exception as e:
        logging.error(f"Error writing to CSV: {str(e)}")

    driver.quit()
    return {"success": 1, "data": keyword_data, "message": "Data fetched successfully.", "error_code": "0"}

def main():
    try:
        result = googlemapDetails()
        logging.info(result)
    except Exception as e:
        logging.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()