safe_alternatives = {
    "Shoes": "Shoes with adjustable sizes and flexible returns",
    "Laptop": "Laptop with extended warranty and fewer complaints",
    "Shirts": "Stretchable or free-size Shirts with positive reviews"
}

def recommend_alternative(category: str):
    try:
        recommendation = safe_alternatives.get(category, "No better alternative found for this category.")
        return {
            "recommended_product": recommendation,
            "reason": "Recommended based on lower historical return rates in this category."
        }
    except Exception as e:
        return {
            "recommended_product": None,
            "reason": f"❌ Recommendation logic failed: {str(e)}"
        }
