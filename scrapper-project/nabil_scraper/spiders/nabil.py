import scrapy
import pandas as pd
import requests
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

class NabilSpider(scrapy.Spider):
    name = "nabil"
    allowed_domains = [
        "nabilbank.com",
        "nbankhome.nabilbank.com",
        "nabilinvest.com.np",
        "nabilsecurities.com.np",
        "mutualfund.nabilinvest.com.np",
        "nabilremit.com",
        "nabilstockdealer.com"
    ]
    start_urls = [
        "https://nabilbank.com/",
        "https://nbankhome.nabilbank.com/",
        "https://nabilinvest.com.np/",
        "https://nabilsecurities.com.np/",
        "https://mutualfund.nabilinvest.com.np/",
        "https://nabilremit.com/",
        "https://nabilstockdealer.com/"
    ]

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920x1080")

        # Initialize driver once
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def process_with_ollama(self, text):
        """Enhance extracted text using Ollama AI (Gamme 2B)"""
        url = "http://localhost:11434/api/generate"

        prompt = f"""
        You are an AI assistant processing banking website content.
        Structure the text into:
        - A short, clear title
        - A well-organized summary
        - Key action points

        **Extracted Text:** {text}
        """

        payload = {
            "model": "gamme-2b",
            "prompt": prompt,
            "stream": False
        }
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json().get("response", text)
        except requests.exceptions.RequestException:
            return text

    def scroll_page(self):
        """Scrolls the page to load all dynamically loaded content."""
        body = self.driver.find_element(By.TAG_NAME, "body")
        for _ in range(5):  # Scroll multiple times
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

    def parse(self, response):
        try:
            self.driver.get(response.url)
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.scroll_page()

            # Extract all text content
            all_text = self.driver.find_elements(By.XPATH, "//body//*[not(self::script or self::style)]")
            extracted_text = "\n".join([elem.text.strip() for elem in all_text if elem.text.strip()])

            # Extract links
            links = [elem.get_attribute("href") for elem in self.driver.find_elements(By.TAG_NAME, "a") if elem.get_attribute("href")]

            # Extract images
            images = [elem.get_attribute("src") for elem in self.driver.find_elements(By.TAG_NAME, "img") if elem.get_attribute("src")]

            # Extract structured sections
            structured_data = []
            sections = self.driver.find_elements(By.CSS_SELECTOR, "div, section, article, table")

            for section in sections:
                try:
                    title_element = section.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4")
                    content_element = section.find_elements(By.CSS_SELECTOR, "p, span, li, td")

                    title = title_element[0].text.strip() if title_element else None
                    content = "\n".join([el.text.strip() for el in content_element if el.text.strip()]) if content_element else None

                    if title and content:
                        enhanced_content = self.process_with_ollama(content)
                        structured_data.append({"title": title, "content": enhanced_content})
                except NoSuchElementException:
                    continue

            os.makedirs("data", exist_ok=True)

            # Save structured data
            extracted_data = {
                "url": response.url,
                "full_text": extracted_text,
                "links": links,
                "images": images,
                "structured_content": structured_data
            }

            df = pd.DataFrame([extracted_data])
            df.to_csv("data/scraped_data.csv", mode='a', index=False, encoding="utf-8")

            self.log(f"✅ Data extracted and saved from: {response.url}")

        except TimeoutException:
            self.log(f"⚠️ Timeout while loading {response.url}")
        except Exception as e:
            self.log(f"❌ Error scraping {response.url}: {str(e)}")

    def closed(self, reason):
        """Ensure driver is closed properly after execution."""
        self.driver.quit()
