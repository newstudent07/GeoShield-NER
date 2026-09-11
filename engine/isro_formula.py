import math
from typing import Tuple

def compute_isro_probability(dr: float, dcr3: float, dar30: float) -> Tuple[float, float]:
    """
    Computes the ISRO empirical probability for landslide occurrence.
    
    Args:
        dr (float): Daily Rainfall in mm.
        dcr3 (float): 3-Day Cumulative Rainfall in mm.
        dar30 (float): 30-Day Antecedent Rainfall in mm.
        
    Returns:
        tuple[float, float]: A tuple of (z_score, probability)
    """
    z = -3.817 + (0.077 * dr) + (0.058 * dcr3) + (0.008 * dar30)
    
    # Sigmoid function for probability
    # Using math.exp with a try-except to avoid overflow for very large negative z
    try:
        p_isro = 1.0 / (1.0 + math.exp(-z))
    except OverflowError:
        p_isro = 0.0 if z < 0 else 1.0
        
    return z, p_isro
