import joblib
import pandas as pd
import numpy as np
import json
import os
import shap
from logger_config import logger  # ✅ Logging added

# Temporary fix for SHAP compatibility
if not hasattr(np, 'bool'):
    np.bool = bool

# --- Resolve paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(BASE_DIR, "model")

# --- Load model and explainer ---
model = joblib.load(os.path.join(model_dir, "trained_model.pkl"))
explainer = shap.TreeExplainer(model)

# Load label encoder
try:
    label_encoder = joblib.load(os.path.join(model_dir, "label_encoder.pkl"))
except FileNotFoundError:
    from sklearn.preprocessing import LabelEncoder
    label_encoder = LabelEncoder()
    label_encoder.classes_ = np.array(['No', 'Yes'])

# Load expected columns
with open(os.path.join(model_dir, "input_columns.json"), "r") as f:
    expected_columns = json.load(f)

# --- Prediction Function ---
def make_prediction(data: dict):
    logger.info("🧠 Running prediction logic")
    df = pd.DataFrame([data])

    # One-hot encode
    categorical_mappings = {
        'Product_Category': ['Laptops', 'Shirts', 'Shoes'],
        'Product_Size': ['L', 'M', 'S'],
        'Customer_Region': ['East', 'North', 'South', 'West'],
        'Customer_Age_Group': ['18-25', '26-35', '36-45', '46-60']
    }
    df_encoded = pd.get_dummies(df, columns=list(categorical_mappings.keys()))

    # Add missing expected columns
    for col in expected_columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_encoded = df_encoded[expected_columns]

    prob = model.predict_proba(df_encoded)[0][1]
    prediction = "Yes" if prob > 0.5 else "No"

    logger.info(f"✅ Prediction = {prediction} | Probability = {round(prob, 3)}")

    return {
        "return_probability": round(float(prob), 3),
        "prediction": prediction
    }

# --- SHAP Explanation ---
def explain_prediction(data: dict):
    logger.info("🔍 SHAP explanation requested")
    try:
        df = pd.DataFrame([data])
        categorical_mappings = {
            'Product_Category': ['Laptops', 'Shirts', 'Shoes'],
            'Product_Size': ['L', 'M', 'S'],
            'Customer_Region': ['East', 'North', 'South', 'West'],
            'Customer_Age_Group': ['18-25', '26-35', '36-45', '46-60']
        }
        df_encoded = pd.get_dummies(df, columns=list(categorical_mappings.keys()))

        for col in expected_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        df_encoded = df_encoded[expected_columns]

        shap_values = explainer.shap_values(df_encoded)

        if isinstance(shap_values, list) and len(shap_values) == 2:
            shap_contributions = shap_values[1][0]
        elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 2:
            shap_contributions = shap_values[0]
        else:
            raise ValueError("Unsupported SHAP output format")

        abs_vals = np.abs(shap_contributions)
        top_indices = np.argsort(abs_vals)[-3:][::-1]

        top_reasons = []
        for idx in top_indices:
            feature_name = expected_columns[idx]
            impact = shap_contributions[idx]
            clean_name = format_feature_name(feature_name)
            direction = "increases" if impact > 0 else "decreases"
            impact_strength = "strongly" if abs(impact) > 0.1 else "slightly"
            top_reasons.append(f"{clean_name} {impact_strength} {direction} return likelihood")

        logger.info("ℹ️ Explanation generated successfully")
        return {
            "top_reasons": top_reasons
            # Optional: "raw_shap": shap_contributions.tolist()
        }

    except Exception as e:
        logger.warning(f"⚠️ SHAP explanation fallback due to error: {str(e)}")
        return {
            "top_reasons": [
                "Product rating affects return likelihood",
                "Delivery time influences customer satisfaction",
                "Past return history is a key indicator"
            ]
        }

# --- Helper to Clean Feature Names ---
def format_feature_name(feature_name):
    if feature_name.startswith('Product_Category_'):
        return f"Product Category: {feature_name.replace('Product_Category_', '')}"
    elif feature_name.startswith('Product_Size_'):
        return f"Product Size: {feature_name.replace('Product_Size_', '')}"
    elif feature_name.startswith('Customer_Region_'):
        return f"Customer Region: {feature_name.replace('Customer_Region_', '')}"
    elif feature_name.startswith('Customer_Age_Group_'):
        return f"Customer Age: {feature_name.replace('Customer_Age_Group_', '').replace('_', '-')}"
    else:
        return feature_name.replace('_', ' ').title()
