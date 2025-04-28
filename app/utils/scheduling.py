"""Utilities for calculating dynamic publishing intervals."""

def calculate_interval(pending_count: int, window_hours: int = 0.5) -> float:
    """
    Calculate the interval in seconds between posts to evenly spread them over a time window.
    
    Args:
        pending_count: Number of pending articles to publish
        window_hours: Time window in hours to spread the posts over (default 30 minutes for testing)
        
    Returns:
        float: Interval in seconds between posts. Returns infinity if pending_count is 0
    """
    total_seconds = window_hours * 3600
    return total_seconds / pending_count if pending_count > 0 else float('inf')