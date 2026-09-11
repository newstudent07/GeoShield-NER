import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import json

INPUT_CSV = "data/historical_training_data.csv"
MODEL_OUTPUT = "models/landslide_xgb.json"

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found. Run build_historical_dataset.py first.")
        return
        
    print("Loading historical dataset...")
    df = pd.read_csv(INPUT_CSV)
    
    # Define features and label
    features = ["z_score", "DR", "3DCR", "30DAR", "base_slope", "soil_porosity"]
    X = df[features]
    y = df["label"]
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))
    
    # Save model artifact
    if not os.path.exists("models"):
        os.makedirs("models")
        
    model.save_model(MODEL_OUTPUT)
    print(f"Model saved to {MODEL_OUTPUT}")

if __name__ == "__main__":
    main()
