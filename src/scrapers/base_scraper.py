"""
Base scraper class for BeaScout unit information collection.

Valid inputs: zip_code (string), radius (integer)
Expected outputs: List of unit dictionaries with scraped information
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import json
import asyncio
from playwright.async_api import async_playwright, Page


class BaseScraper(ABC):
    """Abstract base class for unit information scrapers."""
    
    def __init__(self, delay_seconds: float = 1.5):
        """
        Initialize scraper with rate limiting.
        
        Valid inputs: delay_seconds (float, default 1.5)
        Expected outputs: Configured scraper instance
        """
        self.delay_seconds = delay_seconds
        self.scraped_units = []
    
    @abstractmethod
    async def scrape_zip_code(self, zip_code: str, radius: int = 10) -> List[Dict]:
        """
        Scrape units for a specific zip code and radius.
        
        Valid inputs: 
        - zip_code: 5-digit zip code string
        - radius: search radius in miles (10 or 20)
        Expected outputs: List of unit dictionaries
        """
        pass
    
    @abstractmethod
    def build_search_url(self, zip_code: str, radius: int) -> str:
        """
        Build search URL for specific zip code and radius.
        
        Valid inputs: zip_code (string), radius (integer)
        Expected outputs: Complete search URL string
        """
        pass
    
    async def wait_for_results(self, page: Page, timeout: int = 10000) -> bool:
        """
        Wait for search results to load dynamically.
        
        Valid inputs: page (Playwright Page), timeout (milliseconds)
        Expected outputs: True if results loaded, False if timeout
        """
        try:
            await page.wait_for_selector('[data-testid="unit-card"], .unit-item, .search-result', 
                                        timeout=timeout)
            return True
        except Exception as e:
            print(f"Timeout waiting for results: {e}")
            return False
    
    def save_results(self, filename: str, data: List[Dict]) -> None:
        """
        Save scraped results to JSON file.
        
        Valid inputs: filename (string), data (list of dictionaries)
        Expected outputs: JSON file written to disk
        """
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Saved {len(data)} units to {filename}")
        except Exception as e:
            print(f"Error saving results to {filename}: {e}")
            raise
    
    async def rate_limit(self) -> None:
        """
        Apply rate limiting between requests.
        
        Valid inputs: None
        Expected outputs: Delay completed
        """
        await asyncio.sleep(self.delay_seconds)