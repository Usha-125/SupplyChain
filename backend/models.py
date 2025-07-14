from sqlalchemy import Column, Integer, String, Float
from database import Base

# Stock Table
class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)

# ReturnPrediction Table
class ReturnPrediction(Base):
    __tablename__ = "return_predictions"

    id = Column(Integer, primary_key=True, index=True)
    product_category = Column(String)
    product_size = Column(String)
    customer_region = Column(String)
    customer_age_group = Column(String)
    past_return_count = Column(Integer)
    product_rating = Column(Float)
    delivery_time_days = Column(Integer)
    prediction = Column(String)
    return_probability = Column(Float)
