"""
FutureTools.io scraper module for extracting AI tools information
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime


class FutureToolsScraper:
    """Scraper for FutureTools.io website"""

    BASE_URL = "https://www.futuretools.io"
    NEWLY_ADDED_URL = f"{BASE_URL}/newly-added"

    CATEGORIES = [
        "AI Detection", "Aggregators", "Automation & Agents", "Avatar", "Chat",
        "Copywriting", "Finance", "For Fun", "Gaming", "Generative Art",
        "Generative Code", "Generative Video", "Image Improvement", "Image Scanning",
        "Inspiration", "Marketing", "Motion Capture", "Music", "Podcasting",
        "Productivity", "Prompt Guides", "Research", "Self-Improvement",
        "Social Media", "Speech-To-Text", "Text-To-Speech", "Translation",
        "Video Editing", "Voice Modulation"
    ]

    PRICING_FILTERS = ["Free", "Freemium", "GitHub", "Google Colab", "Open Source", "Paid"]

    def __init__(self, headless: bool = True):
        """Initialize the scraper with optional headless mode"""
        self.headless = headless
        self.driver = None

    def _setup_driver(self):
        """Setup Selenium WebDriver with Chrome"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # Additional options for cloud environments
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Try to use system chromium-driver first (for Streamlit Cloud)
        import os
        import shutil

        chromium_driver_path = shutil.which("chromedriver")

        if chromium_driver_path:
            # Use system chromedriver (Streamlit Cloud)
            print(f"Using system chromedriver at: {chromium_driver_path}")
            service = Service(executable_path=chromium_driver_path)
        else:
            # Use ChromeDriverManager (local development)
            print("Using ChromeDriverManager to install chromedriver")
            service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver

    def _close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def _scroll_to_load_all(self, max_scrolls: int = 100):
        """Scroll the page to load all content with lazy loading"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        no_change_count = 0

        while scrolls < max_scrolls:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for content to load
            time.sleep(1.5)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                no_change_count += 1
                # If height hasn't changed for 3 consecutive scrolls, we're done
                if no_change_count >= 3:
                    # Try clicking "Next Page" or "Load More" button if exists
                    try:
                        load_more_buttons = self.driver.find_elements(By.XPATH,
                            "//a[contains(text(), 'Next Page')] | //button[contains(text(), 'Load More')] | //a[contains(text(), 'Load More')]")
                        if load_more_buttons and load_more_buttons[0].is_displayed():
                            load_more_buttons[0].click()
                            time.sleep(3)
                            new_height = self.driver.execute_script("return document.body.scrollHeight")
                            no_change_count = 0
                        else:
                            break
                    except:
                        break
            else:
                no_change_count = 0

            last_height = new_height
            scrolls += 1

            # Print progress every 10 scrolls
            if scrolls % 10 == 0:
                print(f"Scrolled {scrolls} times, page height: {new_height}")

    def _parse_tool_card(self, card) -> Optional[Dict]:
        """Parse a single tool card element and extract information"""
        try:
            tool_data = {}

            # Extract tool name from the text link inside div-block-62
            name_elem = card.find("a", class_=lambda x: x and "tool-item-link" in str(x) and "tool-item-link-block" not in str(x))

            if not name_elem:
                # Fallback to other possible selectors
                name_elem = card.find("h3") or card.find("h2")

            if name_elem:
                tool_data["name"] = name_elem.get_text(strip=True)
            else:
                # If still no name, skip this card
                return None

            # Extract description from the description box
            desc_elem = card.find("div", class_=lambda x: x and "tool-item-description-box" in str(x))
            if desc_elem:
                tool_data["description"] = desc_elem.get_text(strip=True)
            else:
                tool_data["description"] = ""

            # Extract categories from the collection list
            categories = []
            category_container = card.find("div", class_=lambda x: x and "collection-list-8" in str(x))
            if category_container:
                # Try multiple possible category text classes
                # text-block-53 for main page, black-text-db-gc for newly added page
                category_divs = (
                    category_container.find_all("div", class_=lambda x: x and "text-block-53" in str(x)) or
                    category_container.find_all("div", class_=lambda x: x and "black-text-db-gc" in str(x))
                )
                for cat_div in category_divs:
                    cat_text = cat_div.get_text(strip=True)
                    if cat_text and cat_text not in categories:
                        categories.append(cat_text)

            # Also try to find categories from link-block links if no categories found
            if not categories:
                category_links = card.find_all("a", href=lambda x: x and "?tags=" in str(x))
                for link in category_links:
                    cat_text = link.get_text(strip=True)
                    if cat_text and cat_text not in ['', 'category'] and cat_text not in categories:
                        categories.append(cat_text)

            tool_data["categories"] = ", ".join(categories) if categories else "Uncategorized"

            # Extract pricing info - look for pricing-related elements
            # Note: Pricing is typically only available on individual tool detail pages
            pricing = []

            # Try to find pricing info if available (rare on list pages)
            all_text = card.get_text().lower()
            pricing_keywords = {
                'paid': 'Paid',
                'free trial': 'Free Trial',
                'freemium': 'Freemium',
                'open source': 'Open Source',
                'github': 'GitHub'
            }

            for keyword, label in pricing_keywords.items():
                if keyword in all_text and label not in pricing:
                    pricing.append(label)

            # If no pricing found, check if there's "free" not part of "free trial"
            if not pricing and 'free' in all_text and 'free trial' not in all_text:
                pricing.append('Free')

            tool_data["pricing"] = ", ".join(pricing) if pricing else "Check tool page"

            # Extract URL from the link
            link_elem = card.find("a", href=lambda x: x and x.startswith("/tools/"))
            if link_elem and link_elem.get("href"):
                href = link_elem["href"]
                tool_data["url"] = self.BASE_URL + href
            else:
                tool_data["url"] = ""

            tool_data["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return tool_data
        except Exception as e:
            print(f"Error parsing tool card: {e}")
            return None

    def scrape_newly_added(self) -> List[Dict]:
        """Scrape tools added in the last 24 hours"""
        print("Scraping newly added tools...")
        tools = []

        try:
            print("Setting up Chrome driver...")
            self._setup_driver()
            print("Chrome driver setup successful!")

            print(f"Loading page: {self.NEWLY_ADDED_URL}")
            self.driver.get(self.NEWLY_ADDED_URL)

            # Wait for page to load
            print("Waiting for page to load...")
            time.sleep(3)

            # Scroll to load all content
            print("Scrolling to load content...")
            self._scroll_to_load_all(max_scrolls=10)

            # Get page source and parse with BeautifulSoup
            print("Parsing page content...")
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Try multiple possible selectors for tool cards
            tool_cards = (
                soup.find_all("div", class_=lambda x: x and "tool" in str(x) and "w-dyn-item" in str(x)) or
                soup.find_all("div", class_="tool-card") or
                soup.find_all("div", class_="tool-item") or
                soup.find_all("div", class_="collection-item") or
                soup.find_all("article")
            )

            print(f"Found {len(tool_cards)} tool cards")

            for card in tool_cards:
                tool_data = self._parse_tool_card(card)
                if tool_data:
                    tools.append(tool_data)

        except Exception as e:
            import traceback
            print(f"Error scraping newly added tools: {e}")
            print(f"Traceback: {traceback.format_exc()}")
        finally:
            self._close_driver()

        print(f"Scraped {len(tools)} newly added tools")
        return tools

    def scrape_by_category(self, categories: List[str] = None, pricing_filters: List[str] = None) -> List[Dict]:
        """
        Scrape tools filtered by categories and pricing

        Args:
            categories: List of categories to filter by
            pricing_filters: List of pricing filters to apply
        """
        if categories is None:
            categories = self.CATEGORIES

        print(f"Scraping tools for categories: {categories}")
        all_tools = []

        try:
            self._setup_driver()
            self.driver.get(self.BASE_URL)

            # Wait for page to load
            time.sleep(3)

            # Scroll to load all content
            self._scroll_to_load_all()

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Try multiple possible selectors for tool cards
            tool_cards = (
                soup.find_all("div", class_=lambda x: x and "tool" in str(x) and "w-dyn-item" in str(x)) or
                soup.find_all("div", class_="tool-card") or
                soup.find_all("div", class_="tool-item") or
                soup.find_all("div", class_="collection-item") or
                soup.find_all("article")
            )

            print(f"Found {len(tool_cards)} total tool cards")

            for card in tool_cards:
                tool_data = self._parse_tool_card(card)
                if tool_data:
                    # Filter by category if specified
                    if categories and categories != self.CATEGORIES:
                        tool_categories = tool_data.get("categories", "").split(", ")
                        if not any(cat in categories for cat in tool_categories):
                            continue

                    # Filter by pricing if specified
                    if pricing_filters:
                        tool_pricing = tool_data.get("pricing", "").split(", ")
                        if not any(price in pricing_filters for price in tool_pricing):
                            continue

                    all_tools.append(tool_data)

        except Exception as e:
            print(f"Error scraping tools by category: {e}")
        finally:
            self._close_driver()

        print(f"Scraped {len(all_tools)} tools after filtering")
        return all_tools

    def scrape_all_tools(self, max_pages: int = None) -> List[Dict]:
        """
        Scrape all tools from the website

        Args:
            max_pages: Maximum number of pages to scrape (None for all)
        """
        print("Scraping all tools from FutureTools.io...")
        all_tools = []

        try:
            print("Setting up Chrome driver...")
            self._setup_driver()
            print("Chrome driver setup successful!")

            print(f"Loading page: {self.BASE_URL}")
            self.driver.get(self.BASE_URL)

            # Wait for page to load
            print("Waiting for page to load...")
            time.sleep(3)

            # Scroll to load all content
            print("Loading all tools... This may take several minutes.")
            self._scroll_to_load_all()

            # Get page source and parse with BeautifulSoup
            print("Parsing page content...")
            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            # Try multiple possible selectors for tool cards
            tool_cards = (
                soup.find_all("div", class_=lambda x: x and "tool" in str(x) and "w-dyn-item" in str(x)) or
                soup.find_all("div", class_="tool-card") or
                soup.find_all("div", class_="tool-item") or
                soup.find_all("div", class_="collection-item") or
                soup.find_all("article")
            )

            print(f"Found {len(tool_cards)} total tool cards")

            # Parse all tools without filtering
            print("Extracting tool information...")
            for card in tool_cards:
                tool_data = self._parse_tool_card(card)
                if tool_data:
                    all_tools.append(tool_data)

        except Exception as e:
            import traceback
            print(f"Error scraping all tools: {e}")
            print(f"Traceback: {traceback.format_exc()}")
        finally:
            self._close_driver()

        print(f"Successfully scraped {len(all_tools)} tools")
        return all_tools


def save_to_csv(tools: List[Dict], filename: str = "futuretools_data.csv"):
    """Save scraped tools to CSV file"""
    if not tools:
        print("No tools to save")
        return

    df = pd.DataFrame(tools)
    df.to_csv(filename, index=False)
    print(f"Saved {len(tools)} tools to {filename}")


def load_from_csv(filename: str = "futuretools_data.csv") -> List[Dict]:
    """Load tools from CSV file"""
    try:
        df = pd.read_csv(filename)
        return df.to_dict('records')
    except FileNotFoundError:
        print(f"File {filename} not found")
        return []


if __name__ == "__main__":
    # Test the scraper
    scraper = FutureToolsScraper(headless=True)

    # Test newly added tools
    print("\n=== Testing Newly Added Tools ===")
    newly_added = scraper.scrape_newly_added()
    print(f"Found {len(newly_added)} newly added tools")
    if newly_added:
        print(f"Sample tool: {newly_added[0]}")

    # Test category filtering
    print("\n=== Testing Category Filtering ===")
    test_categories = ["Chat", "Copywriting"]
    filtered_tools = scraper.scrape_by_category(categories=test_categories)
    print(f"Found {len(filtered_tools)} tools in categories: {test_categories}")
