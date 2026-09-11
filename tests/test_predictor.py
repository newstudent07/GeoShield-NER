import pytest
import time
from engine.isro_formula import compute_isro_probability
from engine.predictor import predict_cell_risk

def test_isro_formula_cloudburst():
    """Test the empirical ISRO formula under cloudburst conditions."""
    dr = 140.0
    dcr3 = 210.0
    dar30 = 400.0
    
    z, p = compute_isro_probability(dr, dcr3, dar30)
    
    # Check that z score is calculated without crashing
    assert isinstance(z, float)
    assert isinstance(p, float)
    # Extreme condition should yield high probability
    assert p > 0.75

def test_predictor_schema_validation():
    """Test that predictor properly validates features schema."""
    
    # Missing key
    bad_features_1 = {
        "z_score": 1.0,
        "DR": 50,
        "3DCR": 100,
        # missing 30DAR
        "base_slope": 30,
        "soil_porosity": 45
    }
    
    with pytest.raises(ValueError):
        predict_cell_risk(bad_features_1)
        
    # Extra key
    bad_features_2 = {
        "z_score": 1.0,
        "DR": 50,
        "3DCR": 100,
        "30DAR": 200,
        "base_slope": 30,
        "soil_porosity": 45,
        "extra_key": 10
    }
    
    with pytest.raises(ValueError):
        predict_cell_risk(bad_features_2)
        
    # Wrong type
    bad_features_3 = {
        "z_score": "1.0", # String instead of float
        "DR": 50,
        "3DCR": 100,
        "30DAR": 200,
        "base_slope": 30,
        "soil_porosity": 45
    }
    
    with pytest.raises(TypeError):
        predict_cell_risk(bad_features_3)

def test_predictor_cloudburst_risk():
    """Test inference outputs high probability for extreme conditions and completes under 5ms."""
    
    # Simulate a cloudburst condition
    dr = 140.0
    dcr3 = 210.0
    dar30 = 400.0
    slope = 35.0
    porosity = 45.0
    
    z, p_isro = compute_isro_probability(dr, dcr3, dar30)
    
    features = {
        "z_score": z,
        "DR": dr,
        "3DCR": dcr3,
        "30DAR": dar30,
        "base_slope": slope,
        "soil_porosity": porosity
    }
    
    # Warm up model to ensure we aren't measuring cold start time
    predict_cell_risk(features)
    
    start_time = time.perf_counter()
    prob = predict_cell_risk(features)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    # Check 1: Should be high risk (P > 0.75) per Definition of Done
    assert prob > 0.75, f"Expected high risk probability > 0.75, but got {prob}"
    
    # Check 2: Inference < 5ms
    assert elapsed_ms < 5.0, f"Inference took {elapsed_ms} ms, exceeding the 5 ms budget."
