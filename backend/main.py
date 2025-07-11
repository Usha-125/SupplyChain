from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from predict_logic import make_prediction, explain_prediction



app = FastAPI(title="Smart Returns Optimizer API", version="1.0.0")



# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request validation
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
        input_data = data.dict()

        if input_data['Product_Rating'] < 1 or input_data['Product_Rating'] > 5:
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
        print(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/explain-return")
def explain_return(data: PredictRequest):
    try:
        input_data = data.dict()
        required_fields = ['Product_Category', 'Product_Size', 'Customer_Region', 'Customer_Age_Group']
        for field in required_fields:
            if not input_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        result = explain_prediction(input_data)
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
