"""
Sample test to verify pytest setup.

Valid inputs: None
Expected outputs: Test passes successfully
"""
import pytest


class TestSampleSetup:
    """Sample test class to verify pytest configuration."""
    
    def test_pytest_working(self):
        """
        Test that pytest is properly configured.
        
        Valid inputs: None
        Expected outputs: Assertion passes
        """
        assert True, "Pytest is working correctly"
    
    @pytest.mark.unit
    def test_with_marker(self):
        """
        Test that pytest markers are working.
        
        Valid inputs: None
        Expected outputs: Assertion passes with unit marker
        """
        assert 1 + 1 == 2, "Basic arithmetic works"