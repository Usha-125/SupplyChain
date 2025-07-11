from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from predict_logic import make_prediction, explain_prediction, get_feature_importance_summary

app = FastAPI(title="Smart Returns Optimizer API", version="1.0.0")

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input schema
class PredictRequest(BaseModel):
    Product_Category: str
    Product_Size: str
    Customer_Region: str
    Customer_Age_Group: str
    Past_Return_Count: int
    Product_Rating: float
    Delivery_Time_Days: int

@app.get("/")
def read_root():
    return {"message": "Smart Returns Optimizer API is running!"}

@app.post("/predict-return")
def predict_return(data: PredictRequest):
    try:
        input_data = data.model_dump()

        # Basic validations
        if not (1 <= input_data['Product_Rating'] <= 5):
            raise HTTPException(status_code=400, detail="Product_Rating must be between 1 and 5")
        if input_data['Past_Return_Count'] < 0:
            raise HTTPException(status_code=400, detail="Past_Return_Count cannot be negative")
        if input_data['Delivery_Time_Days'] < 1:
            raise HTTPException(status_code=400, detail="Delivery_Time_Days must be at least 1")

        result = make_prediction(input_data)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/explain-return")
def explain_return(data: PredictRequest):
    try:
        input_data = data.model_dump()
        result = explain_prediction(input_data)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@app.get("/feature-importance")
def feature_importance():
    try:
        return {"top_features": get_feature_importance_summary()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch feature importance: {str(e)}")

# For local dev (optional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
