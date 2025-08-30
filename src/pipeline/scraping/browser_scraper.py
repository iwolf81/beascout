#!/usr/bin/env python3
"""
Browser Automation for BeAScout and JoinExploring

Uses Playwright to load pages with JavaScript execution, 
wait for AJAX content to load, then capture complete HTML.
"""

import time
import sys
import asyncio
import random
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Import our URL generator
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.scraping.url_generator import DualSourceURLGenerator


class BrowserScraper:
    """Browser automation for scraping BeAScout and JoinExploring sites"""
    
    def __init__(self, headless=True, wait_timeout=45000, max_retries=3):  # Increased timeout, added retries
        self.headless = headless
        self.wait_timeout = wait_timeout
        self.max_retries = max_retries
        self.playwright = None
        self.browser = None
        self.page = None
        self.url_generator = DualSourceURLGenerator()
    
    async def setup_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with appropriate options
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # Create new page with custom user agent
            self.page = await self.browser.new_page(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Hide automation indicators
            await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return True
            
        except Exception as e:
            print(f"Error setting up browser: {e}")
            return False
    
    async def retry_with_backoff(self, operation, operation_name, max_retries=None):
        """Retry an operation with exponential backoff and jitter
        
        Args:
            operation: Async function to retry
            operation_name: Human-readable name for logging
            max_retries: Override default max_retries
            
        Returns:
            Result of operation or None if all retries failed
        """
        if max_retries is None:
            max_retries = self.max_retries
            
        for attempt in range(max_retries + 1):
            try:
                print(f"{operation_name} - Attempt {attempt + 1}/{max_retries + 1}")
                result = await operation()
                print(f"{operation_name} - Success on attempt {attempt + 1}")
                return result
                
            except (PlaywrightTimeoutError, Exception) as e:
                if attempt == max_retries:
                    print(f"{operation_name} - All {max_retries + 1} attempts failed. Final error: {e}")
                    return None
                
                # Calculate exponential backoff with jitter
                base_delay = 2 ** attempt  # 1, 2, 4, 8 seconds
                jitter = random.uniform(0.5, 1.5)  # Random multiplier between 0.5 and 1.5
                delay = base_delay * jitter
                
                print(f"{operation_name} - Attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)
        
        return None
    
    async def wait_for_units_to_load(self, site_type='beascout', min_units=1):
        """Wait for unit cards to appear on the page
        
        Args:
            site_type: 'beascout' or 'joinexploring'
            min_units: Minimum number of units to wait for
            
        Returns:
            bool: True if units loaded successfully
        """
        try:
            if site_type == 'beascout':
                # Wait for BeAScout results container
                await self.page.wait_for_selector('#results', timeout=self.wait_timeout)
                
                # Wait for unit cards to load
                unit_cards = []
                for attempt in range(30):  # Try for 30 seconds
                    unit_cards = await self.page.query_selector_all('div.card-body')
                    if len(unit_cards) >= min_units:
                        print(f"BeAScout: Found {len(unit_cards)} units")
                        return True
                    await asyncio.sleep(1)
                
                print(f"BeAScout: Only found {len(unit_cards)} units, expected at least {min_units}")
                return len(unit_cards) > 0  # Accept any units found
                    
            elif site_type == 'joinexploring':
                # Wait for JoinExploring results container
                await self.page.wait_for_selector('#results', timeout=self.wait_timeout)
                
                # Try multiple selectors that might contain unit data
                selectors_to_try = [
                    'div.card-body',
                    'div.unit-card', 
                    'div[class*="card"]',
                    'div[class*="unit"]'
                ]
                
                for selector in selectors_to_try:
                    for attempt in range(30):  # Try for 30 seconds
                        unit_cards = await self.page.query_selector_all(selector)
                        if len(unit_cards) >= min_units:
                            print(f"JoinExploring: Found {len(unit_cards)} units using selector '{selector}'")
                            return True
                        await asyncio.sleep(1)
                
                # If no units found, that might be normal for some areas
                print(f"JoinExploring: No units found (may be normal for this area)")
                return True  # Don't fail if no Explorer units exist
                
        except PlaywrightTimeoutError:
            print(f"Timeout waiting for {site_type} units to load")
            return False
        except Exception as e:
            print(f"Error waiting for {site_type} units: {e}")
            return False
    
    async def scrape_beascout(self, zip_code, output_file=None):
        """Scrape BeAScout for traditional units with retry logic
        
        Args:
            zip_code: ZIP code to search
            output_file: Optional output file path
            
        Returns:
            str: HTML content or None if failed
        """
        url = self.url_generator.generate_beascout_url(zip_code)
        print(f"Scraping BeAScout: {url}")
        
        async def scrape_attempt():
            """Single scraping attempt"""
            # Create fresh page context for each attempt to avoid state issues
            if hasattr(self, '_attempt_count'):
                self._attempt_count += 1
                if self._attempt_count > 1:
                    # Create new page for retry attempts
                    if self.page:
                        await self.page.close()
                    self.page = await self.browser.new_page(
                        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    )
                    await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            else:
                self._attempt_count = 1
            
            # Navigate to page with longer timeout and different wait strategy
            await self.page.goto(url, timeout=60000, wait_until='domcontentloaded')
            
            # Wait for page to stabilize
            await asyncio.sleep(5)
            
            # Wait for units to load with extended patience
            if not await self.wait_for_units_to_load('beascout', min_units=1):
                print("No units found immediately, waiting longer...")
                await asyncio.sleep(10)  # Extra wait for slow AJAX
                
                # Check again
                if not await self.wait_for_units_to_load('beascout', min_units=0):
                    print("Still no units, but continuing with page content...")
            
            # Additional wait to ensure all content is loaded
            await asyncio.sleep(3)
            
            # Get complete page HTML
            html_content = await self.page.content()
            
            # Basic validation - check if we got meaningful content
            if len(html_content) < 10000:  # Suspiciously small page
                raise Exception(f"Page content too small ({len(html_content)} chars), likely incomplete")
            
            return html_content
        
        # Use retry mechanism
        html_content = await self.retry_with_backoff(
            scrape_attempt, 
            f"BeAScout scraping for {zip_code}"
        )
        
        # Clean up attempt counter
        if hasattr(self, '_attempt_count'):
            delattr(self, '_attempt_count')
        
        if html_content and output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"BeAScout HTML saved to: {output_path}")
        
        return html_content
    
    async def scrape_joinexploring(self, zip_code, output_file=None):
        """Scrape JoinExploring for Explorer units with retry logic
        
        Args:
            zip_code: ZIP code to search
            output_file: Optional output file path
            
        Returns:
            str: HTML content or None if failed
        """
        url = self.url_generator.generate_joinexploring_url(zip_code)
        print(f"Scraping JoinExploring: {url}")
        
        async def scrape_attempt():
            """Single scraping attempt"""
            # Create fresh page context for each attempt to avoid state issues
            if hasattr(self, '_attempt_count_je'):
                self._attempt_count_je += 1
                if self._attempt_count_je > 1:
                    # Create new page for retry attempts
                    if self.page:
                        await self.page.close()
                    self.page = await self.browser.new_page(
                        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    )
                    await self.page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            else:
                self._attempt_count_je = 1
            
            # Navigate to page with longer timeout and different wait strategy
            await self.page.goto(url, timeout=60000, wait_until='domcontentloaded')
            
            # Wait for page to stabilize
            await asyncio.sleep(5)
            
            # Wait for units to load with extended patience (may be 0 units in some areas)
            if not await self.wait_for_units_to_load('joinexploring', min_units=0):
                print("No units found immediately, waiting longer...")
                await asyncio.sleep(10)  # Extra wait for slow AJAX
                
                # Check again
                if not await self.wait_for_units_to_load('joinexploring', min_units=0):
                    print("Still no units, but continuing with page content...")
            
            # Additional wait to ensure all content is loaded
            await asyncio.sleep(5)  # Longer wait for JoinExploring
            
            # Get complete page HTML
            html_content = await self.page.content()
            
            # Basic validation - check if we got meaningful content
            if len(html_content) < 10000:  # Suspiciously small page
                raise Exception(f"Page content too small ({len(html_content)} chars), likely incomplete")
            
            return html_content
        
        # Use retry mechanism
        html_content = await self.retry_with_backoff(
            scrape_attempt, 
            f"JoinExploring scraping for {zip_code}"
        )
        
        # Clean up attempt counter
        if hasattr(self, '_attempt_count_je'):
            delattr(self, '_attempt_count_je')
        
        if html_content and output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"JoinExploring HTML saved to: {output_path}")
        
        return html_content
    
    async def scrape_both_sources(self, zip_code, output_dir="data/scraped"):
        """Scrape both BeAScout and JoinExploring for a ZIP code
        
        Args:
            zip_code: ZIP code to search
            output_dir: Directory to save HTML files
            
        Returns:
            dict: {'beascout': html_content, 'joinexploring': html_content}
        """
        results = {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Scrape BeAScout
        beascout_file = output_path / f"beascout_{zip_code}_auto.html"
        results['beascout'] = await self.scrape_beascout(zip_code, beascout_file)
        
        # Small delay between requests
        await asyncio.sleep(2)
        
        # Scrape JoinExploring  
        joinexploring_file = output_path / f"joinexploring_{zip_code}_auto.html"
        results['joinexploring'] = await self.scrape_joinexploring(zip_code, joinexploring_file)
        
        return results
    
    async def close(self):
        """Close the browser and playwright"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def __aenter__(self):
        """Async context manager entry"""
        if await self.setup_browser():
            return self
        else:
            raise RuntimeError("Failed to setup browser")
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


async def main():
    """Command-line interface"""
    if len(sys.argv) != 2:
        print("Usage: python src/scraping/browser_scraper.py <zip_code>")
        print("\nExample: python src/scraping/browser_scraper.py 01720")
        sys.exit(1)
    
    zip_code = sys.argv[1]
    
    print(f"Starting browser automation for ZIP code: {zip_code}")
    
    try:
        async with BrowserScraper(headless=True) as scraper:
            results = await scraper.scrape_both_sources(zip_code)
            
            print("\n=== SCRAPING RESULTS ===")
            for source, html_content in results.items():
                if html_content:
                    print(f"{source.upper()}: Successfully scraped ({len(html_content)} chars)")
                else:
                    print(f"{source.upper()}: Failed to scrape")
    
    except Exception as e:
        print(f"Browser automation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())