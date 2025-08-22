"""
BeaScout.scouting.org scraper for Scouting America units.

Valid inputs: zip_code (string), radius (10 miles default)
Expected outputs: List of unit information dictionaries
"""
from typing import Dict, List
from playwright.async_api import async_playwright
from .base_scraper import BaseScraper


class BeaScoutScraper(BaseScraper):
    """Scraper for beascout.scouting.org unit information."""
    
    def __init__(self, delay_seconds: float = 1.5):
        """
        Initialize BeaScout scraper.
        
        Valid inputs: delay_seconds (float, default 1.5)
        Expected outputs: Configured scraper instance
        """
        super().__init__(delay_seconds)
        self.base_url = "https://beascout.scouting.org"
    
    def build_search_url(self, zip_code: str, radius: int = 10) -> str:
        """
        Build search URL for BeaScout with all unit types.
        
        Valid inputs: zip_code (5-digit string), radius (integer, default 10)
        Expected outputs: Complete search URL for all unit types
        """
        url = f"{self.base_url}/list/"
        params = [
            f"zip={zip_code}",
            "program[0]=pack",
            "program[1]=scoutsBSA", 
            "program[2]=crew",
            "program[3]=ship",
            "cubFilter=all",
            "scoutsBSAFilter=all",
            f"miles={radius}"
        ]
        return f"{url}?{'&'.join(params)}"
    
    async def scrape_zip_code(self, zip_code: str, radius: int = 10) -> List[Dict]:
        """
        Scrape all units for a zip code from BeaScout.
        
        Valid inputs: zip_code (string), radius (integer, default 10)
        Expected outputs: List of unit dictionaries with scraped information
        """
        url = self.build_search_url(zip_code, radius)
        units = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                print(f"Scraping BeaScout for {zip_code} (radius: {radius} miles)")
                await page.goto(url)
                
                # Wait for results to load
                results_loaded = await self.wait_for_results(page)
                if not results_loaded:
                    print(f"No results loaded for {zip_code}")
                    return units
                
                # Extract unit information
                units = await self.extract_units(page)
                print(f"Found {len(units)} units for {zip_code}")
                
            except Exception as e:
                print(f"Error scraping {zip_code}: {e}")
            finally:
                await browser.close()
        
        return units
    
    async def extract_units(self, page) -> List[Dict]:
        """
        Extract unit information from search results page.
        
        Valid inputs: page (Playwright Page object)
        Expected outputs: List of unit dictionaries
        """
        units = []
        
        try:
            # Wait a bit more for dynamic content
            await page.wait_for_timeout(2000)
            
            # Try multiple possible selectors for unit cards
            unit_selectors = [
                '[data-testid="unit-card"]',
                '.unit-card',
                '.unit-item', 
                '.search-result',
                '.unit-listing'
            ]
            
            unit_elements = None
            for selector in unit_selectors:
                unit_elements = await page.query_selector_all(selector)
                if unit_elements:
                    print(f"Found {len(unit_elements)} units using selector: {selector}")
                    break
            
            if not unit_elements:
                # Fallback: try to find any div containing unit information
                page_content = await page.content()
                print("No unit elements found, page content preview:")
                print(page_content[:500])
                return units
            
            for element in unit_elements:
                unit_data = await self.extract_unit_data(element)
                if unit_data:
                    units.append(unit_data)
                    
        except Exception as e:
            print(f"Error extracting units: {e}")
        
        return units
    
    async def extract_unit_data(self, element) -> Dict:
        """
        Extract data from a single unit element.
        
        Valid inputs: element (Playwright ElementHandle)
        Expected outputs: Dictionary with unit information
        """
        unit_data = {
            'source_website': 'beascout.scouting.org',
            'primary_identifier': '',
            'unit_type': '',
            'unit_number': '',
            'chartered_organization': '',
            'meeting_location': '',
            'meeting_day': '',
            'meeting_time': '',
            'contact_email': '',
            'contact_person': '',
            'phone_number': '',
            'website': '',
            'description': '',
            'unit_composition': '',
            'specialty': ''
        }
        
        try:
            # Extract text content - this will need refinement based on actual HTML structure
            text_content = await element.inner_text()
            
            # For now, store raw content for analysis
            unit_data['raw_content'] = text_content
            
            # Try to extract basic information (will refine after seeing real data)
            lines = text_content.strip().split('\n')
            if lines:
                # First line often contains unit identifier
                unit_data['primary_identifier'] = lines[0].strip()
            
            print(f"Extracted unit: {unit_data['primary_identifier'][:50]}...")
            
        except Exception as e:
            print(f"Error extracting unit data: {e}")
        
        return unit_data