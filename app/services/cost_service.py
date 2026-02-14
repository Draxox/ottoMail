"""Business logic services"""
import json
from typing import Dict

def calculate_cost(hours: int, complexity: str) -> Dict:
    """Calculate project cost based on hours and complexity"""
    multipliers = {
        "simple": 1.0,
        "medium": 1.5,
        "complex": 2.0
    }
    
    multiplier = multipliers.get(complexity, 1.5)
    base_rate = 50
    base_cost = int(hours * base_rate * multiplier)
    
    return {
        "min": int(base_cost * 0.9),
        "max": int(base_cost * 1.1),
        "hours": hours,
        "complexity": complexity
    }
