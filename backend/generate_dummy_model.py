import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import shap

# Define model save directory
model_dir = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(model_dir, exist_ok=True)

# Create sample data for training
data = pd.DataFrame([
    {"Product_Category": "Shirts", "Product_Size": "M", "Customer_Region": "South", "Customer_Age_Group": "26-35", "Past_Return_Count": 2, "Product_Rating": 4.2, "Delivery_Time_Days": 3, "Return": "No"},
    {"Product_Category": "Shoes", "Product_Size": "L", "Customer_Region": "East", "Customer_Age_Group": "18-25", "Past_Return_Count": 0, "Product_Rating": 2.5, "Delivery_Time_Days": 7, "Return": "Yes"},
    {"Product_Category": "Laptops", "Product_Size": "S", "Customer_Region": "West", "Customer_Age_Group": "46-60", "Past_Return_Count": 5, "Product_Rating": 3.5, "Delivery_Time_Days": 5, "Return": "Yes"},
    {"Product_Category": "Shirts", "Product_Size": "S", "Customer_Region": "North", "Customer_Age_Group": "36-45", "Past_Return_Count": 1, "Product_Rating": 5.0, "Delivery_Time_Days": 2, "Return": "No"},
])

# Encode target
data["Return"] = data["Return"].map({"No": 0, "Yes": 1})

# One-hot encode input
X = pd.get_dummies(data.drop("Return", axis=1))
y = data["Return"]

# Save expected column list
expected_columns = list(X.columns)
with open(os.path.join(model_dir, "input_columns.json"), "w") as f:
    json.dump(expected_columns, f)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model and SHAP explainer
joblib.dump(model, os.path.join(model_dir, "trained_model.pkl"))
explainer = shap.TreeExplainer(model)
joblib.dump(explainer, os.path.join(model_dir, "shap_explainer.pkl"))

print("✅ New model and SHAP explainer saved with correct input columns!")
