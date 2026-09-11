import os
import httpx
import pandas as pd
import numpy as np
import sys

# Adjust sys.path so we can import the engine module from scripts folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from engine.isro_formula import compute_isro_probability

API_URL = "https://archive-api.open-meteo.com/v1/archive"
PARAMS = {
    "latitude": 23.73,
    "longitude": 92.71,
    "start_date": "2014-01-01",
    "end_date": "2023-12-31",
    "daily": "precipitation_sum",
    "timezone": "auto"
}

OUTPUT_CSV = "data/historical_training_data.csv"

def fetch_weather_data() -> pd.DataFrame:
    print("Fetching historical weather data from Open-Meteo...")
    response = httpx.get(API_URL, params=PARAMS, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    
    daily_data = data["daily"]
    df = pd.DataFrame({
        "date": pd.to_datetime(daily_data["time"]),
        "DR": daily_data["precipitation_sum"]
    })
    
    # Forward fill any missing precipitation values with 0
    df["DR"] = df["DR"].fillna(0)
    return df

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    print("Building rolling window features...")
    
    # 3DCR: 3-Day Cumulative Rainfall (including current day)
    df["3DCR"] = df["DR"].rolling(window=3, min_periods=1).sum()
    
    # 30DAR: 30-Day Antecedent Rainfall
    # Antecedent usually means prior to the current day, but for the sake of simplicity 
    # we can use a rolling sum of 30 days including the current day, or shifted.
    # Let's use a 30-day rolling sum excluding the current day:
    df["30DAR"] = df["DR"].shift(1).rolling(window=30, min_periods=1).sum().fillna(0)

    print("Calculating ISRO probabilities and labels...")
    z_scores = []
    p_isro_list = []
    labels = []
    
    for _, row in df.iterrows():
        dr = row["DR"]
        dcr3 = row["3DCR"]
        dar30 = row["30DAR"]
        
        z, p = compute_isro_probability(dr, dcr3, dar30)
        z_scores.append(z)
        p_isro_list.append(p)
        
        # Labeling logic:
        # If P >= 0.75 and DR > 50 -> Label 1 (Hazard)
        if p >= 0.75 and dr > 50:
            labels.append(1)
        else:
            labels.append(0)
            
    df["z_score"] = z_scores
    df["P_ISRO"] = p_isro_list
    df["label"] = labels
    
    return df

def expand_dataset(df: pd.DataFrame) -> pd.DataFrame:
    print("Expanding dataset with terrain features (slope, porosity)...")
    # We will simulate multiple grid cells with different static features
    # to provide a varied feature space for XGBoost.
    
    expanded_rows = []
    # Let's generate 5 simulated cells with varying parameters
    terrain_configs = [
        {"base_slope": 25.0, "soil_porosity": 45.0},
        {"base_slope": 30.0, "soil_porosity": 50.0},
        {"base_slope": 35.0, "soil_porosity": 55.0},
        {"base_slope": 40.0, "soil_porosity": 40.0},
        {"base_slope": 45.0, "soil_porosity": 60.0},
    ]
    
    for config in terrain_configs:
        cell_df = df.copy()
        cell_df["base_slope"] = config["base_slope"]
        cell_df["soil_porosity"] = config["soil_porosity"]
        
        # We need to adjust labels to make XGBoost learn that higher slope = higher risk.
        # Since our initial label only considered rainfall, we can augment the rule:
        # If rainfall label is 1, it's a hazard. But if slope is too low (< 30), it might not fail.
        # Or if slope is very high (>40), even slightly lower rainfall could cause a failure.
        # Let's apply a slight deterministic modification for a better synthetic-historical mix:
        
        new_labels = []
        for _, row in cell_df.iterrows():
            lbl = row["label"]
            p = row["P_ISRO"]
            dr = row["DR"]
            slope = row["base_slope"]
            
            # Custom heuristic to tie slope into the label:
            if lbl == 1 and slope < 30:
                # High rain, but low slope -> Safe
                lbl = 0
            elif p >= 0.65 and dr > 40 and slope >= 40:
                # Moderate rain, very high slope -> Hazard
                lbl = 1
                
            new_labels.append(lbl)
            
        cell_df["label"] = new_labels
        expanded_rows.append(cell_df)
        
    final_df = pd.concat(expanded_rows, ignore_index=True)
    
    # Shuffle the dataset
    final_df = final_df.sample(frac=1).reset_index(drop=True)
    return final_df

def main():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    df_weather = fetch_weather_data()
    df_features = build_features(df_weather)
    df_expanded = expand_dataset(df_features)
    
    # Select final columns for training
    final_cols = ["z_score", "DR", "3DCR", "30DAR", "base_slope", "soil_porosity", "label"]
    df_final = df_expanded[final_cols]
    
    print(f"Dataset summary:\n{df_final['label'].value_counts()}")
    
    df_final.to_csv(OUTPUT_CSV, index=False)
    print(f"Historical dataset successfully saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
