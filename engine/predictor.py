import os
import time
import xgboost as xgb
import pandas as pd
from pydantic import BaseModel, StrictFloat, StrictInt
from typing import Union

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "landslide_xgb.json")



# Load model globally to avoid loading it per request
_model = None

def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        _model = xgb.XGBClassifier()
        _model.load_model(MODEL_PATH)
    return _model

def predict_cell_risk(features_dict: dict) -> float:
    """
    Predicts landslide trigger probability for a given cell.
    
    Args:
        features_dict (dict): Dictionary containing all required features.
        
    Returns:
        float: Landslide trigger probability (0.0 to 1.0).
    """
    start_time = time.perf_counter()
    
    # Check 1: Strict Validation
    # We use Pydantic to ensure all required fields are present and are numbers.
    # Due to variable names starting with numbers (3DCR), Pydantic aliases might be needed if mapped to object fields,
    # but we can simply validate the dict keys and types directly.
    
    required_keys = ["z_score", "DR", "3DCR", "30DAR", "base_slope", "soil_porosity"]
    
    # Strict validation of keys
    if set(features_dict.keys()) != set(required_keys):
        raise ValueError(f"Feature dictionary must contain exactly these keys: {required_keys}")
        
    for k, v in features_dict.items():
        if not isinstance(v, (int, float)):
            raise TypeError(f"Feature '{k}' must be a number, got {type(v)}")

    # Convert to DataFrame ensuring column order exactly matches training data
    df = pd.DataFrame([features_dict], columns=required_keys)
    
    model = get_model()
    
    # Predict probability (class 1)
    # predict_proba returns array of [prob_class_0, prob_class_1]
    prob = model.predict_proba(df)[0][1]
    
    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000
    
    # Check 2: Benchmark Constraint (< 5ms)
    if elapsed_ms > 5.0:
        print(f"WARNING: Inference took {elapsed_ms:.2f} ms, which exceeds the 5 ms budget.")
        
    return float(prob)
