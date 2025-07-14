def calculate_discount(return_probability: float):
    try:
        if return_probability > 90:
            return {"discount_percent": 20, "reason": "Very high return risk"}
        elif return_probability > 70:
            return {"discount_percent": 10, "reason": "High return risk"}
        else:
            return {"discount_percent": 0, "reason": "No risk mitigation needed"}
    except Exception as e:
        return {"discount_percent": 0, "reason": f"❌ Discount logic failed: {str(e)}"}
