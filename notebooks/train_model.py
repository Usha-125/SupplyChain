import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import shap
import json
import os

def load_and_preprocess_data():
    """Load and preprocess the dataset"""
   
    csv_path = os.path.join(os.path.dirname(__file__), 'smart_returns_dataset.csv')
    df = pd.read_csv(csv_path)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nMissing values:\n{df.isnull().sum()}")
    
    # Handle missing values in categorical columns (replace NaN with 'Unknown')
    categorical_cols = ['Product_Category', 'Product_Size', 'Customer_Region', 'Customer_Age_Group']
    for col in categorical_cols:
        df[col] = df[col].fillna('Unknown')
    
    return df

def prepare_features_and_target(df):
    """Prepare features and target variable"""
    # Separate features and target
    X = df.drop(['Product_ID', 'Will_Return'], axis=1)
    y = df['Will_Return']
    
    # Encode target variable
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # One-hot encode categorical features
    categorical_cols = ['Product_Category', 'Product_Size', 'Customer_Region', 'Customer_Age_Group']
    X_encoded = pd.get_dummies(X, columns=categorical_cols)
    
    print(f"Feature columns after encoding: {X_encoded.columns.tolist()}")
    print(f"Encoded dataset shape: {X_encoded.shape}")
    
    return X_encoded, y_encoded, label_encoder, X_encoded.columns.tolist()

def train_model(X, y):
    """Train the Random Forest model"""
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Evaluate
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.3f}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")
    
    return model, X_train, X_test, y_test

def create_shap_explainer(model, X_train):
    """Create SHAP explainer"""
    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)
    
    # Test with a small sample to ensure it works
    shap_sample = X_train.sample(min(100, len(X_train)), random_state=42)
    shap_values = explainer.shap_values(shap_sample)
    
    print(f"SHAP explainer created successfully")
    print(f"SHAP values shape: {np.array(shap_values).shape}")
    
    return explainer

def save_model_artifacts(model, explainer, label_encoder, feature_columns):
    """Save all model artifacts"""
    # Create model directory
    model_dir = 'model'
    os.makedirs(model_dir, exist_ok=True)
    
    # Save model
    joblib.dump(model, os.path.join(model_dir, 'trained_model.pkl'))
    print("✅ Model saved")
    
    # Save SHAP explainer
    joblib.dump(explainer, os.path.join(model_dir, 'shap_explainer.pkl'))
    print("✅ SHAP explainer saved")
    
    # Save label encoder
    joblib.dump(label_encoder, os.path.join(model_dir, 'label_encoder.pkl'))
    print("✅ Label encoder saved")
    
    # Save feature columns
    with open(os.path.join(model_dir, 'input_columns.json'), 'w') as f:
        json.dump(feature_columns, f)
    print("✅ Feature columns saved")

def main():
    """Main training pipeline"""
    print("🚀 Starting Smart Returns Model Training...")
    
    # Load and preprocess data
    df = load_and_preprocess_data()
    
    # Prepare features and target
    X_encoded, y_encoded, label_encoder, feature_columns = prepare_features_and_target(df)
    
    # Train model
    model, X_train, X_test, y_test = train_model(X_encoded, y_encoded)
    
    # Create SHAP explainer
    explainer = create_shap_explainer(model, X_train)
    
    # Save all artifacts
    save_model_artifacts(model, explainer, label_encoder, feature_columns)
    
    print("\n🎉 Training completed successfully!")
    print("📁 Model artifacts saved in 'model/' directory")
    print("\n🔧 Next steps:")
    print("1. Navigate to backend/ directory")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: python main.py")
    print("4. Open frontend/index.html in your browser")

if __name__ == "__main__":
    main()