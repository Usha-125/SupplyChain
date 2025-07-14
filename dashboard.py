import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(page_title="Smart Returns Optimizer", layout="wide")
st.title("🎯 Smart Returns Optimizer")

# Session management
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# ---------------------- LOGIN ----------------------
with st.expander("🔐 Login", expanded=st.session_state.access_token is None):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        res = requests.post(
            "http://127.0.0.1:8000/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if res.status_code == 200:
            st.session_state.access_token = res.json()["access_token"]
            st.success("✅ Logged in!")
        else:
            st.error("❌ Invalid username or password")

if not st.session_state.access_token:
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

# ---------------------- PREDICTION ----------------------
st.markdown("## 🧾 Predict Return Risk")

with st.form("predict_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        product_category = st.selectbox("Product Category", ["Shirts", "Shoes", "Laptops"])
        product_rating = st.slider("Product Rating", 1.0, 5.0, 4.0)
    with col2:
        product_size = st.selectbox("Product Size", ["S", "M", "L"])
        delivery_time = st.slider("Delivery Time (days)", 1, 30, 5)
    with col3:
        past_return = st.slider("Past Return Count", 0, 20, 1)
        region = st.selectbox("Customer Region", ["North", "South", "East", "West"])
    
    age_group = st.selectbox("Customer Age Group", ["18-25", "26-35", "36-45", "46-60"])
    submitted = st.form_submit_button("🔮 Predict Return Risk")

if submitted:
    input_data = {
        "Product_Category": product_category,
        "Product_Size": product_size,
        "Customer_Region": region,
        "Customer_Age_Group": age_group,
        "Past_Return_Count": past_return,
        "Product_Rating": product_rating,
        "Delivery_Time_Days": delivery_time
    }

    with st.spinner("Processing prediction..."):
        try:
            pred_res = requests.post("http://127.0.0.1:8000/predict-return", json=input_data).json()
            explain_res = requests.post("http://127.0.0.1:8000/explain-return", json=input_data).json()

            prob = round(pred_res["return_probability"] * 100, 1)
            risk_level = "High" if prob > 70 else "Medium" if prob > 40 else "Low"
            risk_color = {"High": "red", "Medium": "orange", "Low": "green"}[risk_level]

            st.markdown(f"### 📊 Prediction Result: **{pred_res['prediction']}**")
            st.markdown(f"**Return Probability:** {prob}%")
            st.markdown(f"**Risk Level:** :{risk_color}[{risk_level}]")
            st.markdown("#### 🧠 Key Factors")
            st.write(explain_res["top_reasons"])

        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")

# ---------------------- DISCOUNTS & RECOMMENDATIONS ----------------------
if submitted:
    with st.expander("🎁 Offers & Recommendations", expanded=True):
        try:
            return_probability = pred_res["return_probability"] * 100

            discount = requests.post(
                "http://127.0.0.1:8000/get-discount", 
                json={"return_probability": return_probability}
            ).json()

            recommend = requests.post(
                "http://127.0.0.1:8000/recommend", 
                json={"Product_Category": product_category}
            ).json()

            st.markdown(f"**💸 Discount Suggestion:** {discount['discount_percent']}% — _{discount['reason']}_")
            st.markdown("**🔄 Recommended Alternatives:**")
            st.write(recommend["recommended_product"])

        except Exception as e:
            st.error("❌ Failed to fetch recommendations or discount.")


# ---------------------- FILTERED DASHBOARD ----------------------
st.markdown("---")
st.header("📊 Real-Time Dashboard Summary")

# 🔽 Region Filter Dropdown
selected_region = st.selectbox("🌍 Select Region to Filter", ["All", "North", "South", "East", "West"])

try:
    # Pass region to backend if not "All"
    if selected_region == "All":
        dashboard = requests.get("http://127.0.0.1:8000/dashboard-data").json()
    else:
        dashboard = requests.get(f"http://127.0.0.1:8000/dashboard-data?region={selected_region}").json()

    col1, col2 = st.columns(2)
    col1.metric("📦 Total Returns", dashboard["total_returns"])
    col2.metric("🚨 High Risk Returns", dashboard["high_risk_returns"])

    # 📊 Returns by Category
    st.subheader("🛍️ Returns by Category")
    df_returns = pd.DataFrame.from_dict(dashboard["return_by_category"], orient="index", columns=["Returns"]).reset_index()
    df_returns.columns = ["Category", "Returns"]
    st.altair_chart(
        alt.Chart(df_returns).mark_bar().encode(
            x="Category", y="Returns", color="Category"
        ).properties(height=300),
        use_container_width=True
    )

    # ⭐ Average Rating by Category
    st.subheader("⭐ Average Ratings by Category")
    df_ratings = pd.DataFrame.from_dict(dashboard["average_rating_by_category"], orient="index", columns=["Avg Rating"]).reset_index()
    df_ratings.columns = ["Category", "Avg Rating"]
    st.altair_chart(
        alt.Chart(df_ratings).mark_line(point=True).encode(
            x="Category", y="Avg Rating"
        ).properties(height=300),
        use_container_width=True
    )

    # 📦 Stock Summary Pie Chart
    st.subheader("📦 Stock Summary")
    stock_dict = dashboard["stock_summary"]
    labels = list(stock_dict.keys())
    values = list(stock_dict.values())

    fig, ax = plt.subplots(figsize=(2.5, 2.5))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # 📋 Raw Table
    st.subheader("📋 Raw Dashboard Data (Returns by Category)")
    st.dataframe(df_returns)

except Exception as e:
    st.error(f"❌ Failed to load dashboard summary: {e}")


# ---------------------- LOG VIEWER ----------------------
st.markdown("---")
st.header("📘 Logs")

try:
    response = requests.get("http://localhost:8000/view-logs")
    if response.status_code == 200:
        logs = response.json().get("logs", "")
        if logs:
            st.text_area("📄 Log Output", logs, height=300)
        else:
            st.warning("Log file is empty.")
    else:
        st.warning("Failed to fetch logs from the backend.")
except Exception as e:
    st.error(f"Error: {str(e)}")
