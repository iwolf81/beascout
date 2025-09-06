#!/usr/bin/env python3
"""
Dual-Source URL Generation for BeAScout and JoinExploring

Generates URLs for scraping unit data from both beascout.scouting.org and joinexploring.org
with proper parameter encoding and unit type filtering.
"""

from typing import List, Dict, Tuple
import urllib.parse


class DualSourceURLGenerator:
    """Generates URLs for both BeAScout and JoinExploring data sources"""
    
    # BeAScout program mappings
    BEASCOUT_PROGRAMS = {
        'pack': 'pack',
        'troop': 'scoutsBSA', 
        'crew': 'crew',
        'ship': 'ship'
    }
    
    # JoinExploring program mappings  
    JOINEXPLORING_PROGRAMS = {
        'post': 'post',
        'club': 'club'
    }
    
    # Default search radius for each source
    BEASCOUT_RADIUS = 10  # miles
    JOINEXPLORING_RADIUS = 20  # miles
    
    def __init__(self):
        self.beascout_base = "https://beascout.scouting.org/list/"
        self.joinexploring_base = "https://joinexploring.org/list/"
    
    def generate_beascout_url(self, zip_code: str, programs: List[str] = None, 
                             radius: int = None) -> str:
        """Generate BeAScout URL for traditional Scouting units
        
        Args:
            zip_code: ZIP code to search around
            programs: List of unit types to include ['pack', 'troop', 'crew', 'ship']
            radius: Search radius in miles (default: 10)
            
        Returns:
            Formatted BeAScout URL
        """
        if programs is None:
            programs = ['pack', 'troop', 'crew', 'ship']
        
        if radius is None:
            radius = self.BEASCOUT_RADIUS
            
        params = {
            'zip': zip_code,
            'miles': str(radius),
            'cubFilter': 'all',
            'scoutsBSAFilter': 'all'
        }
        
        # Add program parameters with array notation
        for i, program in enumerate(programs):
            if program in self.BEASCOUT_PROGRAMS:
                params[f'program[{i}]'] = self.BEASCOUT_PROGRAMS[program]
        
        query_string = urllib.parse.urlencode(params, safe='[]')
        return f"{self.beascout_base}?{query_string}"
    
    def generate_joinexploring_url(self, zip_code: str, programs: List[str] = None,
                                  radius: int = None) -> str:
        """Generate JoinExploring URL for Explorer units
        
        Args:
            zip_code: ZIP code to search around  
            programs: List of unit types to include ['post', 'club']
            radius: Search radius in miles (default: 20)
            
        Returns:
            Formatted JoinExploring URL
        """
        if programs is None:
            programs = ['post', 'club']
            
        if radius is None:
            radius = self.JOINEXPLORING_RADIUS
            
        params = {
            'zip': zip_code,
            'miles': str(radius)
        }
        
        # Add program parameters with array notation
        for i, program in enumerate(programs):
            if program in self.JOINEXPLORING_PROGRAMS:
                params[f'program[{i}]'] = self.JOINEXPLORING_PROGRAMS[program]
        
        query_string = urllib.parse.urlencode(params, safe='[]')
        return f"{self.joinexploring_base}?{query_string}"
    
    def generate_all_urls(self, zip_code: str, 
                         beascout_programs: List[str] = None,
                         joinexploring_programs: List[str] = None,
                         beascout_radius: int = None,
                         joinexploring_radius: int = None) -> Dict[str, str]:
        """Generate URLs for both data sources
        
        Args:
            zip_code: ZIP code to search around
            beascout_programs: BeAScout unit types (default: all traditional units)
            joinexploring_programs: JoinExploring unit types (default: all explorer units)
            beascout_radius: BeAScout search radius (default: 10 miles)
            joinexploring_radius: JoinExploring search radius (default: 20 miles)
            
        Returns:
            Dictionary with 'beascout' and 'joinexploring' URLs
        """
        urls = {}
        
        # Generate BeAScout URL for traditional units
        urls['beascout'] = self.generate_beascout_url(
            zip_code, beascout_programs, beascout_radius
        )
        
        # Generate JoinExploring URL for Explorer units  
        urls['joinexploring'] = self.generate_joinexploring_url(
            zip_code, joinexploring_programs, joinexploring_radius
        )
        
        return urls
    
    def get_curl_commands(self, zip_code: str) -> Dict[str, str]:
        """Generate curl commands for testing both URLs
        
        Args:
            zip_code: ZIP code to search around
            
        Returns:
            Dictionary with curl commands for both sources
        """
        urls = self.generate_all_urls(zip_code)
        
        return {
            'beascout': f'curl -s "{urls["beascout"]}" > beascout_{zip_code}.html',
            'joinexploring': f'curl -s "{urls["joinexploring"]}" > joinexploring_{zip_code}.html'
        }


def main():
    """Command-line interface for URL generation"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python src/scraping/url_generator.py <zip_code>")
        print("\nExample: python src/scraping/url_generator.py 01720")
        sys.exit(1)
    
    zip_code = sys.argv[1]
    generator = DualSourceURLGenerator()
    
    # Generate URLs
    urls = generator.generate_all_urls(zip_code)
    curl_commands = generator.get_curl_commands(zip_code)
    
    print(f"Dual-Source URLs for ZIP {zip_code}:")
    print(f"\nBeAScout URL (Traditional Units):")
    print(urls['beascout'])
    print(f"\nJoinExploring URL (Explorer Units):")
    print(urls['joinexploring'])
    
    print(f"\nCurl Commands for Testing:")
    print(f"\nBeAScout:")
    print(curl_commands['beascout'])
    print(f"\nJoinExploring:")
    print(curl_commands['joinexploring'])


if __name__ == '__main__':
    main()