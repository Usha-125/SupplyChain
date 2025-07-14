# 🔁 Smart Returns Optimizer

## 📌 Problem We Are Solving

E-commerce platforms today suffer massive losses due to **high product return rates**. These returns:

* Disrupt **inventory** and **logistics** flow
* **Damage seller ratings** and platform trust
* Lead to **avoidable environmental impact** via reverse shipping
* Are often caused by **predictable factors** like wrong product size, past customer behavior, or slow delivery

🛑 Currently, there’s **no intelligent system** that predicts and prevents returns **before shipment**.
This results in billions of rupees in losses and dissatisfied customers.

---

## ✅ Our Solution: Smart Returns Optimizer

We have built an **AI-powered system** that:

* 🔍 Predicts the likelihood of a product being returned **before it's shipped**
* 🧠 Provides **SHAP-based explainability** for each prediction
* 📊 Offers feature importance insights to understand key drivers
* 🌟 Helps businesses make decisions like applying discounts, manual verification, or delivery improvements

This system exposes:

* 🧪 A **REST API backend** (via FastAPI) for prediction and explanation
* 🖥️ A **lightweight frontend** for sellers/support to input data and view return insights in real time

---

## 💡 Importance

* 🚛 Reduce reverse logistics costs
* 📉 Minimize return percentage
* 😄 Improve customer satisfaction and trust
* ♻️ Reduce carbon emissions from unnecessary delivery cycles
* 💼 Support business teams with **data-driven decisions**

---

## 🧰 Tech Stack & Justification

| Component           | Technology Used             | Why?                                                   |
| ------------------- | --------------------------- | ------------------------------------------------------ |
| **Backend**         | `FastAPI`, `Pydantic v2`    | Fast, async-capable REST APIs with schema validation   |
| **ML Model**        | `RandomForestClassifier`    | Robust, interpretable, and works well for tabular data |
| **Explainability**  | `SHAP`                      | Model interpretability to explain feature impact       |
| **Serialization**   | `Joblib`                    | Efficient saving/loading of model and encoders         |
| **Frontend**        | `HTML`, `CSS`, `JavaScript` | Lightweight static interface for easy usage            |
| **Version Control** | `Git + GitHub`              | Collaboration and multi-branch team workflows          |

---

## 🚀 How to Run This Project

### ⚙️ 1. Train the Machine Learning Model

Generates:

* `trained_model.pkl`
* `shap_explainer.pkl`
* `label_encoder.pkl`
* `input_columns.json`

```bash
D:\wall\backend\.venv\Scripts\python.exe D:\wall\notebooks\train_model.py
```

📅 Output: Model artifacts saved to `backend/model/`

---

### 🧠 2. Start the FastAPI Backend Server

```bash
cd backend
python main.py
```

Or using `uvicorn` for production:

```bash
uvicorn main:app --reload
```

📅 Server running at: `http://127.0.0.1:8000`

---

### 🧪 3. Test APIs Using Swagger UI

Open in browser:

```
http://127.0.0.1:8000/docs
```

Available API routes:

| Endpoint              | Purpose                        |
| --------------------- | ------------------------------ |
| `/predict-return`     | Predict return probability     |
| `/explain-return`     | Explain key reasons for return |
| `/feature-importance` | Show global top features       |

---

### 🌐 4. Open Frontend

```bash
start frontend\index.html
```

Or just double-click `index.html` from the `frontend/` folder.

Use the interface to:

* Enter order details
* Get prediction + explanation
* Make business decisions

---


## 📂 Folder Structure

```
project-root/
├── backend/
│   ├── main.py
│   ├── predict_logic.py
│   ├── model/
│   │   ├── trained_model.pkl
│   │   ├── shap_explainer.pkl
│   │   ├── label_encoder.pkl
│   │   └── input_columns.json
│   └── __init__.py
├── frontend/
│   └── index.html
└── notebooks/
    └── train_model.py
```

---

## 📣 Final Note

Smart Returns Optimizer is a ready-to-use, ML-integrated platform for **reducing return rates**, **improving satisfaction**, and **saving costs**.
Built with a modular, explainable, and scalable architecture — perfect for real-world deployment.
