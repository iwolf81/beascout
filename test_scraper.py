#!/usr/bin/env python3
"""
Quick test script for BeaScout scraper.

Valid inputs: None (hardcoded test zip codes)
Expected outputs: JSON files with scraped unit data
"""
import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.beascout_scraper import BeaScoutScraper


async def test_scraper():
    """
    Test scraper with Acton, MA zip code.
    
    Valid inputs: None
    Expected outputs: JSON file with scraped units
    """
    scraper = BeaScoutScraper(delay_seconds=2.0)
    
    # Test with Acton, MA - 10 mile radius
    test_zip = "01720"
    print(f"Testing scraper with zip code: {test_zip}")
    
    try:
        units = await scraper.scrape_zip_code(test_zip, radius=10)
        
        if units:
            output_file = f"data/raw/beascout_{test_zip}_test.json"
            scraper.save_results(output_file, units)
            print(f"\nScraping completed! Found {len(units)} units.")
            print(f"Results saved to: {output_file}")
            
            # Print first unit for quick inspection
            if units:
                print(f"\nFirst unit preview:")
                first_unit = units[0]
                for key, value in first_unit.items():
                    if key == 'raw_content':
                        print(f"  {key}: {str(value)[:100]}...")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("No units found. Check if website structure has changed.")
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Install playwright browsers if needed
    print("Starting BeaScout scraper test...")
    print("Note: If this fails, run: playwright install")
    
    asyncio.run(test_scraper())