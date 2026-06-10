import shap
import joblib
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ingestion.logger import get_logger

logger = get_logger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'models')

def get_shap_values(target='points', sample_size=200):
    logger.info(f"Computing SHAP values for {target} model...")

    model_path = os.path.join(MODEL_DIR, f'xgb_{target}.joblib')
    artifact = joblib.load(model_path)
    model = artifact['model']
    feature_cols = artifact['feature_cols']

    explainer = shap.TreeExplainer(model)
    return explainer, feature_cols

def get_feature_importance(target='points'):
    artifact_path = os.path.join(MODEL_DIR, f'xgb_{target}.joblib')
    artifact = joblib.load(artifact_path)
    model = artifact['model']
    feature_cols = artifact['feature_cols']

    importance = model.feature_importances_
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': importance
    }).sort_values('importance', ascending=False)

    return importance_df

def explain_prediction(player_features: dict, target='points'):
    artifact_path = os.path.join(MODEL_DIR, f'xgb_{target}.joblib')
    artifact = joblib.load(artifact_path)
    model = artifact['model']
    feature_cols = artifact['feature_cols']

    row = pd.DataFrame([player_features])
    for col in feature_cols:
        if col not in row.columns:
            row[col] = 0
    row = row[feature_cols].fillna(0)

    prediction = model.predict(row)[0]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(row)

    shap_df = pd.DataFrame({
        'feature': feature_cols,
        'value': row.values[0],
        'shap_value': shap_values[0]
    }).sort_values('shap_value', key=abs, ascending=False)

    return float(prediction), shap_df

if __name__ == "__main__":
    print("\n--- Feature Importance for Points Model ---")
    importance_df = get_feature_importance('points')
    print(importance_df.head(10).to_string(index=False))

    print("\n--- Feature Importance for Rebounds Model ---")
    importance_df = get_feature_matrix = get_feature_importance('rebounds')
    print(importance_df.head(10).to_string(index=False))

    print("\n--- Feature Importance for Assists Model ---")
    importance_df = get_feature_importance('assists')
    print(importance_df.head(10).to_string(index=False))
