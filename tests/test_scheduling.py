import pytest
from app.utils.scheduling import calculate_interval

def test_calculate_interval():
    # Test with 8 articles over 8 hours
    assert calculate_interval(8) == 3600.0  # One hour (3600 seconds)
    
    # Test with 16 articles over 8 hours
    assert calculate_interval(16) == 1800.0  # Half hour (1800 seconds)
    
    # Test with 0 articles
    assert calculate_interval(0) == float('inf')
    
    # Test with custom window
    assert calculate_interval(4, window_hours=4) == 3600.0  # One hour with 4-hour window
    
    # Test with 1 article
    assert calculate_interval(1) == 28800.0  # Full 8-hour window