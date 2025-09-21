#!/usr/bin/env python3
"""
Data source configuration for BeAScout pipeline.
Easily switch between anonymized test data and real production data.
"""

import os
from pathlib import Path

# Environment variable to control data source mode
DEVELOPMENT_MODE = os.getenv('BEASCOUT_DEV_MODE', 'true').lower() == 'true'

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class DataSources:
    """Configuration for all data source paths"""
    
    def __init__(self, development_mode: bool = None):
        """Initialize data sources configuration.
        
        Args:
            development_mode: If True, use anonymized test data. If None, use environment variable.
        """
        if development_mode is None:
            development_mode = DEVELOPMENT_MODE
        
        self.development_mode = development_mode
        
        # Key Three data source
        if development_mode:
            self.key_three_json = PROJECT_ROOT / "tests/reference/key_three/anonymized_key_three.json"
            self.key_three_excel = PROJECT_ROOT / "tests/reference/key_three/anonymized_key_three.xlsx"
        else:
            self.key_three_json = PROJECT_ROOT / "data/input/HNE_key_three.json" 
            self.key_three_excel = PROJECT_ROOT / "data/input/HNE_key_three.xlsx"
    
    def get_key_three_path(self, format: str = 'json') -> Path:
        """Get Key Three data path in specified format.
        
        Args:
            format: 'json' or 'excel'
            
        Returns:
            Path to Key Three data file
        """
        if format.lower() == 'json':
            return self.key_three_json
        elif format.lower() in ['excel', 'xlsx']:
            return self.key_three_excel
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode (using anonymized data)."""
        return self.development_mode
    
    def get_mode_description(self) -> str:
        """Get human-readable description of current mode."""
        if self.development_mode:
            return "Development mode (anonymized test data - safe for commits/sharing)"
        else:
            return "Production mode (real personal data - DO NOT COMMIT)"


# Global instance for easy importing
data_sources = DataSources()


def switch_to_development_mode():
    """Switch to development mode (anonymized data)."""
    global data_sources
    data_sources = DataSources(development_mode=True)


def switch_to_production_mode():
    """Switch to production mode (real data) - USE WITH CAUTION."""
    global data_sources
    data_sources = DataSources(development_mode=False)


if __name__ == "__main__":
    # Print current configuration
    print("BeAScout Data Sources Configuration")
    print("=" * 40)
    print(f"Mode: {data_sources.get_mode_description()}")
    print(f"Key Three JSON: {data_sources.get_key_three_path('json')}")
    print(f"Key Three Excel: {data_sources.get_key_three_path('excel')}")
    print(f"Files exist: JSON={data_sources.get_key_three_path('json').exists()}, Excel={data_sources.get_key_three_path('excel').exists()}")
    
    print(f"\nTo switch modes:")
    print(f"Development: export BEASCOUT_DEV_MODE=true")
    print(f"Production:  export BEASCOUT_DEV_MODE=false")