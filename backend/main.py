from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
import os, json, logging

# Services
from services.discount_logic import calculate_discount
from services.recommendation_logic import recommend_alternative

from logger_config import logger
from auth import authenticate_user, create_access_token
from database import SessionLocal, engine
from models import Base, Stock, ReturnPrediction
from visualize import stock_bar_chart
from predict_logic import make_prediction, explain_prediction

app = FastAPI(title="Smart Returns Optimizer API", version="1.0.0")

# Setup base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "app.log")
PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "products.json")

# Serve frontend if exists
frontend_path = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_path):
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB
Base.metadata.create_all(bind=engine)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schema
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

@app.on_event("startup")
def seed_initial_data():
    db = SessionLocal()
    if db.query(Stock).count() == 0:
        db.add_all([
            Stock(name="Shirts", quantity=100),
            Stock(name="Shoes", quantity=50),
            Stock(name="Laptops", quantity=30)
        ])
    if db.query(ReturnPrediction).count() == 0:
        db.add_all([
            ReturnPrediction(
                product_category="Shirts",
                product_size="M",
                customer_region="North",
                customer_age_group="18-25",
                past_return_count=2,
                product_rating=4.0,
                delivery_time_days=3,
                prediction="Yes",
                return_probability=0.76
            ),
            ReturnPrediction(
                product_category="Shoes",
                product_size="8",
                customer_region="South",
                customer_age_group="26-35",
                past_return_count=1,
                product_rating=3.5,
                delivery_time_days=2,
                prediction="No",
                return_probability=0.38
            ),
            ReturnPrediction(
                product_category="Laptops",
                product_size="15-inch",
                customer_region="East",
                customer_age_group="36-45",
                past_return_count=0,
                product_rating=4.8,
                delivery_time_days=1,
                prediction="No",
                return_probability=0.15
            )
        ])
    db.commit()
    db.close()

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        logger.warning(f"❌ Failed login for: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token({"sub": form_data.username})
    logger.info(f"🔐 Login successful: {form_data.username}")
    return {"access_token": token, "token_type": "bearer"}

@app.post("/predict-return")
def predict_return(data: PredictRequest, db: Session = Depends(get_db)):
    try:
        input_data = data.dict()
        result = make_prediction(input_data)
        db_record = ReturnPrediction(
            product_category=input_data["Product_Category"],
            product_size=input_data["Product_Size"],
            customer_region=input_data["Customer_Region"],
            customer_age_group=input_data["Customer_Age_Group"],
            product_rating=input_data["Product_Rating"],
            delivery_time_days=input_data["Delivery_Time_Days"],
            past_return_count=input_data["Past_Return_Count"],
            prediction=result["prediction"],
            return_probability=result["return_probability"]
        )
        db.add(db_record)
        db.commit()
        logger.info("✅ Prediction made successfully.")
        return result
    except Exception as e:
        logger.error(f"❌ Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/explain-return")
def explain_return(data: PredictRequest):
    try:
        input_data = data.dict()
        result = explain_prediction(input_data)
        logger.info("ℹ️ Explanation generated.")
        return result
    except Exception as e:
        logger.error(f"❌ Explanation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@app.post("/get-discount")
async def get_discount(data: dict):
    try:
        probability = float(data.get("return_probability", 0))
        result = calculate_discount(probability)
        logger.info(f"🎁 Discount logic executed for return_probability={probability}")
        return result
    except Exception as e:
        logger.error(f"❌ Discount logic error: {str(e)}")
        return {"discount_percent": 0, "reason": "Failed to calculate discount"}

@app.post("/recommend")
async def recommend_product(data: dict):
    try:
        category = data.get("Product_Category")
        result = recommend_alternative(category)
        logger.info(f"🧠 Recommendation made for category={category}")
        return result
    except Exception as e:
        logger.error(f"❌ Recommendation logic error: {str(e)}")
        return {"recommended_product": None, "reason": "Failed to recommend"}

@app.get("/view-logs")
def view_logs():
    try:
        if not os.path.exists(LOG_PATH):
            raise FileNotFoundError("Log file not found.")
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        return JSONResponse(content={"logs": content})
    except Exception as e:
        logger.error(f"❌ Log file read error: {str(e)}")
        return JSONResponse(content={"logs": "Unable to read logs."})

@app.get("/stocks")
def get_stocks(db: Session = Depends(get_db)):
    return db.query(Stock).all()

@app.get("/visualize", response_class=HTMLResponse)
async def visualize_chart():
    try:
        chart_html = stock_bar_chart()
        logger.info("📊 Stock chart rendered.")
        return HTMLResponse(content=chart_html)
    except Exception as e:
        logger.error(f"❌ Visualization error: {str(e)}")
        return HTMLResponse(content=f"<p>Error rendering chart: {str(e)}</p>")

@app.get("/dashboard-data")
def dashboard_data(region: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(ReturnPrediction)
        if region and region != "All":
            query = query.filter(ReturnPrediction.customer_region == region)

        total_returns = query.count()
        high_risk_returns = query.filter(ReturnPrediction.return_probability > 0.7).count()

        category_counts = query.with_entities(ReturnPrediction.product_category, func.count()).group_by(ReturnPrediction.product_category).all()
        category_ratings = query.with_entities(ReturnPrediction.product_category, func.avg(ReturnPrediction.product_rating)).group_by(ReturnPrediction.product_category).all()
        avg_return_probs = query.with_entities(ReturnPrediction.product_category, func.avg(ReturnPrediction.return_probability)).group_by(ReturnPrediction.product_category).all()

        stock_data = db.query(Stock).all()
        stock_summary = {s.name: s.quantity for s in stock_data}

        discount_summary = {}
        try:
            with open(PRODUCTS_FILE, "r") as f:
                products = json.load(f)
                for p in products:
                    discount_summary[p["name"]] = {
                        "discount_percent": p.get("discount_percent", 0),
                        "reason": p.get("discount_reason", "N/A")
                    }
        except Exception as e:
            logger.warning(f"⚠️ Couldn't read product file: {e}")
            discount_summary = {}

        logger.info(f"📊 Dashboard loaded: Total={total_returns}, High Risk={high_risk_returns}")

        return {
            "total_returns": total_returns,
            "high_risk_returns": high_risk_returns,
            "return_by_category": {cat: count for cat, count in category_counts},
            "average_rating_by_category": {cat: round(avg, 2) for cat, avg in category_ratings},
            "average_return_probability_by_category": {cat: round(prob, 2) for cat, prob in avg_return_probs},
            "stock_summary": stock_summary,
            "discount_summary_by_category": discount_summary
        }
    except Exception as e:
        logger.error(f"❌ Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard data")

# Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
