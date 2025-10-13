#!/usr/bin/env python3
"""
Multi-Zip Scraper
Scrapes BeAScout and JoinExploring for multiple ZIP codes with timestamped output
Implements respectful rate limiting to avoid detection/blocking
"""

import json
import time
import random
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add current directory to path for imports (assumes running from beascout/ directory)
# When running "python src/scripts/multi_zip_scraper.py" from beascout/, 
# we need the beascout directory in the path
current_dir = Path.cwd()
sys.path.insert(0, str(current_dir))

from src.pipeline.acquisition.browser_scraper import BrowserScraper


class MultiZipScraper:
    """
    Multi-zip scraper with aggressive rate limiting to prevent blocking
    
    Strategy:
    - Process zip codes in small batches with long cooling periods
    - Limit requests per browser session
    - Monitor for failure patterns indicating detection
    - Fallback to manual intervention if needed
    """
    
    def __init__(self):
        self.config = {
            # Conservative timing (essential)
            'zip_delay_range': (12, 18),      # 12-18 seconds between zip codes
            'batch_size': 8,                   # Process 8 zips, then cool down
            'batch_cooldown': (120, 180),      # 2-3 minute cooldown between batches
            'session_limit': 20,               # Max requests per browser session
            
            # Failure detection (essential)
            'max_consecutive_failures': 3,    # Stop if 3 failures in a row
            'success_rate_threshold': 0.7,    # Stop if success rate drops below 70%
            
            # Removed unnecessary restrictions
            'daily_limit': None,               # No daily limit - run when needed
            'allowed_hours': None,             # No time restrictions
            'weekend_processing': True,        # Allow anytime processing
        }
        
        self.session_stats = {
            'requests_in_session': 0,
            'successful_zips': 0,
            'failed_zips': 0,
            'consecutive_failures': 0,
            'start_time': None
        }
    
    def is_processing_allowed(self) -> bool:
        """Check if processing is allowed (always True now - removed time restrictions)"""
        return True
    
    def calculate_delay(self, base_range: tuple, jitter_factor: float = 0.3) -> float:
        """Calculate random delay with jitter"""
        min_delay, max_delay = base_range
        base_delay = random.uniform(min_delay, max_delay)
        jitter = random.uniform(-jitter_factor, jitter_factor) * base_delay
        return max(1.0, base_delay + jitter)  # Minimum 1 second
    
    async def wait_with_progress(self, delay_seconds: float, message: str):
        """Wait with progress indication"""
        print(f"{message} (waiting {delay_seconds:.1f}s)")
        
        # Show progress every 10 seconds for long waits
        if delay_seconds > 10:
            intervals = int(delay_seconds / 10)
            for i in range(intervals):
                await asyncio.sleep(10)
                remaining = delay_seconds - ((i + 1) * 10)
                if remaining > 0:
                    print(f"  ⏱ {remaining:.0f}s remaining...")
            
            # Sleep remaining time
            final_wait = delay_seconds - (intervals * 10)
            if final_wait > 0:
                await asyncio.sleep(final_wait)
        else:
            await asyncio.sleep(delay_seconds)
    
    def should_continue_processing(self) -> tuple[bool, str]:
        """Check if processing should continue based on failure patterns"""
        stats = self.session_stats
        
        # Check consecutive failures
        if stats['consecutive_failures'] >= self.config['max_consecutive_failures']:
            return False, f"Too many consecutive failures ({stats['consecutive_failures']})"
        
        # Check success rate (only after processing several zips)
        total_processed = stats['successful_zips'] + stats['failed_zips']
        if total_processed >= 5:
            success_rate = stats['successful_zips'] / total_processed
            if success_rate < self.config['success_rate_threshold']:
                return False, f"Success rate too low ({success_rate:.1%})"
        
        # Check session limits
        if stats['requests_in_session'] >= self.config['session_limit']:
            return False, "Session request limit reached"
        
        # Check daily limits (would need persistent storage to track across sessions)
        
        return True, "OK"
    
    async def process_single_zip(self, zip_code: str, scraper: BrowserScraper) -> bool:
        """Process a single zip code with error handling"""
        try:
            print(f"📍 Processing ZIP {zip_code}...")
            
            # Scrape both sources
            beascout_html = await scraper.scrape_beascout(zip_code)
            await asyncio.sleep(self.calculate_delay((3, 7)))  # Delay between sites
            
            joinexploring_html = await scraper.scrape_joinexploring(zip_code) 
            
            # Save results to session directory
            beascout_file = f"{self.session_dir}/beascout_{zip_code}.html"
            joinexploring_file = f"{self.session_dir}/joinexploring_{zip_code}.html"
            
            with open(beascout_file, 'w', encoding='utf-8') as f:
                f.write(beascout_html)
            
            with open(joinexploring_file, 'w', encoding='utf-8') as f:
                f.write(joinexploring_html)
            
            print(f"✅ ZIP {zip_code} completed successfully")
            print(f"   📁 Saved: {beascout_file}")
            print(f"   📁 Saved: {joinexploring_file}")
            
            self.session_stats['successful_zips'] += 1
            self.session_stats['consecutive_failures'] = 0  # Reset failure counter
            return True
            
        except Exception as e:
            print(f"❌ ZIP {zip_code} failed: {str(e)}")
            self.session_stats['failed_zips'] += 1
            self.session_stats['consecutive_failures'] += 1
            return False
    
    async def process_zip_batch(self, zip_codes: list[str]) -> tuple[int, int]:
        """Process a batch of zip codes with conservative timing"""
        if not self.is_processing_allowed():
            print("❌ Outside business hours - processing stopped")
            return 0, 0
        
        print(f"🚀 Starting batch of {len(zip_codes)} zip codes...")
        
        scraper = BrowserScraper()
        try:
            await scraper.setup_browser()
            
            successful = 0
            failed = 0
            
            for i, zip_code in enumerate(zip_codes):
                # Check if we should continue
                can_continue, reason = self.should_continue_processing()
                if not can_continue:
                    print(f"🛑 Stopping processing: {reason}")
                    break
                
                # Check business hours again
                if not self.is_processing_allowed():
                    print("❌ Outside business hours - stopping batch")
                    break
                
                # Process zip code
                success = await self.process_single_zip(zip_code, scraper)
                self.session_stats['requests_in_session'] += 2  # BeAScout + JoinExploring
                
                if success:
                    successful += 1
                else:
                    failed += 1
                
                # Delay before next zip (except for last one)
                if i < len(zip_codes) - 1:
                    delay = self.calculate_delay(self.config['zip_delay_range'])
                    await self.wait_with_progress(
                        delay, 
                        f"📊 Progress: {i+1}/{len(zip_codes)} | ✅ {successful} | ❌ {failed}"
                    )
            
            return successful, failed
            
        finally:
            await scraper.close()
    
    async def process_all_hne_zip_codes(self):
        """Process all zip codes from the default zip code file"""
        # Load zip codes
        zip_file = "data/zipcodes/hne_council_zipcodes.json"
        with open(zip_file, 'r') as f:
            zip_data = json.load(f)
        
        all_zips = zip_data['all_zipcodes']
        print(f"📋 Loaded {len(all_zips)} zip codes")
        
        # Create timestamped directory for this scraping session
        start_time = datetime.now()
        self.session_stats['start_time'] = start_time
        self.session_timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        self.session_dir = f"data/scraped/{self.session_timestamp}"
        
        # Create session directory
        Path(self.session_dir).mkdir(parents=True, exist_ok=True)
        print(f"📁 Session directory: {self.session_dir}")
        
        # Process in batches
        batch_size = self.config['batch_size']
        batches = [all_zips[i:i + batch_size] for i in range(0, len(all_zips), batch_size)]
        
        print(f"📦 Processing {len(batches)} batches of {batch_size} zip codes each")
        
        total_successful = 0
        total_failed = 0
        
        for batch_num, batch in enumerate(batches, 1):
            print(f"\n🔄 BATCH {batch_num}/{len(batches)}")
            print(f"   ZIP codes: {', '.join(batch)}")
            
            # Check business hours
            if not self.is_processing_allowed():
                print(f"❌ Outside business hours - stopping at batch {batch_num}")
                break
            
            # Process batch
            successful, failed = await self.process_zip_batch(batch)
            total_successful += successful
            total_failed += failed
            
            print(f"   ✅ Batch results: {successful} successful, {failed} failed")
            
            # Cooling period between batches (except last batch)
            if batch_num < len(batches):
                cooldown = self.calculate_delay(self.config['batch_cooldown'])
                await self.wait_with_progress(
                    cooldown, 
                    f"❄️  Cooling down between batches"
                )
                
                # Reset session after cooldown (new browser instance)
                self.session_stats['requests_in_session'] = 0
        
        # Final summary
        duration = datetime.now() - self.session_stats['start_time']
        print(f"\n📊 FINAL SUMMARY")
        print(f"   ✅ Successful: {total_successful}")
        print(f"   ❌ Failed: {total_failed}")
        print(f"   ⏱  Duration: {duration}")
        print(f"   📈 Success rate: {total_successful/(total_successful+total_failed):.1%}")
        print(f"   📁 Results saved in: {self.session_dir}")
        
        # Create session summary file
        summary_file = f"{self.session_dir}/session_summary.json"
        summary_data = {
            "session_timestamp": self.session_timestamp,
            "start_time": self.session_stats['start_time'].isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_minutes": duration.total_seconds() / 60,
            "total_zip_codes": len(all_zips),
            "successful_zips": total_successful,
            "failed_zips": total_failed,
            "success_rate": total_successful/(total_successful+total_failed) if (total_successful+total_failed) > 0 else 0,
            "session_directory": self.session_dir
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"   📋 Session summary: {summary_file}")


# Test function with a few zip codes
async def test_conservative_approach():
    """Test with a small number of zip codes"""
    print("🧪 Testing Conservative Multi-Zip Scraper")
    print("=" * 50)
    
    # Test with just 3 zip codes
    test_zips = ['01720', '01420', '01453']
    
    scraper = MultiZipScraper()
    
    # Initialize session directory and stats for test
    start_time = datetime.now()
    scraper.session_stats = {
        'requests_in_session': 0,
        'successful_zips': 0,
        'failed_zips': 0,
        'consecutive_failures': 0,
        'start_time': start_time
    }
    scraper.session_timestamp = start_time.strftime("%Y%m%d_%H%M%S")
    scraper.session_dir = f"data/scraped/{scraper.session_timestamp}"
    
    # Create session directory
    Path(scraper.session_dir).mkdir(parents=True, exist_ok=True)
    print(f"📁 Session directory: {scraper.session_dir}")
    
    # Temporarily reduce delays for testing
    scraper.config.update({
        'zip_delay_range': (5, 10),       # Shorter delays for testing
        'batch_cooldown': (30, 60),       # Shorter cooldown for testing
        'batch_size': 2,                  # Smaller batches for testing
    })
    
    # Process test batch
    await scraper.process_zip_batch(test_zips)


if __name__ == '__main__':
    # For testing, use the test function
    # For production, use process_all_hne_zip_codes()

    import sys

    # Parse command line arguments
    mode = None
    session_id = None
    skip_failed = False
    fallback_cache = False

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg in ['test', 'full']:
            mode = arg
        elif arg == '--session-id' and i + 1 < len(sys.argv):
            session_id = sys.argv[i + 1]
        elif arg == '--skip-failed':
            skip_failed = True
        elif arg == '--fallback-cache':
            fallback_cache = True

    if mode == 'test':
        asyncio.run(test_conservative_approach())
    elif mode == 'full':
        scraper = MultiZipScraper()

        # Override session timestamp if provided
        if session_id:
            scraper.session_timestamp = session_id
            scraper.session_dir = f"data/scraped/{session_id}"
            Path(scraper.session_dir).mkdir(parents=True, exist_ok=True)

        asyncio.run(scraper.process_all_hne_zip_codes())
    else:
        print("Multi-Zip Scraper")
        print("Usage:")
        print("  python src/scripts/multi_zip_scraper.py test                    # Test with 3 zip codes")
        print("  python src/scripts/multi_zip_scraper.py full                    # Process all zip codes from file")
        print("  python src/scripts/multi_zip_scraper.py full --session-id ID    # Use specific session ID")
        print("  python src/scripts/multi_zip_scraper.py                         # Show usage")