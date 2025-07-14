const form = document.getElementById("predictForm");
const resultDiv = document.getElementById("result");
const infoDiv = document.getElementById("additional-info");
const vizDiv = document.getElementById("visualization");
const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");
let accessToken = null;

// 🔐 Login Form Submission
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(loginForm);
  const loginData = new URLSearchParams();
  loginData.append("username", formData.get("username"));
  loginData.append("password", formData.get("password"));

  try {
    const res = await fetch("http://127.0.0.1:8000/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: loginData,
    });

    if (!res.ok) throw new Error("Invalid credentials");

    const json = await res.json();
    accessToken = json.access_token;
    loginMessage.innerHTML = `<p style="color: green;">✅ Logged in!</p>`;
  } catch (err) {
    loginMessage.innerHTML = `<p style="color: red;">❌ ${err.message}</p>`;
  }
});

// 🔮 Prediction Form Submission
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  resultDiv.innerHTML = `<div class="result-container"><p>🔄 Processing prediction...</p></div>`;
  infoDiv.innerHTML = "";
  vizDiv.innerHTML = "";

  const formData = new FormData(form);
  const data = {
    Product_Category: formData.get("Product_Category"),
    Product_Size: formData.get("Product_Size"),
    Customer_Region: formData.get("Customer_Region"),
    Customer_Age_Group: formData.get("Customer_Age_Group"),
    Past_Return_Count: parseInt(formData.get("Past_Return_Count")),
    Product_Rating: parseFloat(formData.get("Product_Rating")),
    Delivery_Time_Days: parseInt(formData.get("Delivery_Time_Days")),
  };

  try {
    const [predictRes, explainRes] = await Promise.all([
      fetch("http://127.0.0.1:8000/predict-return", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }),
      fetch("http://127.0.0.1:8000/explain-return", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }),
    ]);

    if (!predictRes.ok || !explainRes.ok)
      throw new Error(`API Error: ${predictRes.status} | ${explainRes.status}`);

    const predictJson = await predictRes.json();
    const explainJson = await explainRes.json();

    const probabilityPercent = (predictJson.return_probability * 100).toFixed(1);
    const riskLevel =
      predictJson.return_probability > 0.7
        ? "High"
        : predictJson.return_probability > 0.4
        ? "Medium"
        : "Low";

    const riskColor =
      riskLevel === "High"
        ? "#e53e3e"
        : riskLevel === "Medium"
        ? "#dd6b20"
        : "#38a169";

    resultDiv.innerHTML = `
      <div class="result-container">
        <h3>📊 Prediction Result</h3>
        <div class="prediction-summary">
          <p><strong>Return Prediction:</strong> <span style="color: ${riskColor}; font-weight: bold;">${predictJson.prediction}</span></p>
          <p><strong>Return Probability:</strong> ${probabilityPercent}%</p>
          <p><strong>Risk Level:</strong> <span style="color: ${riskColor};">${riskLevel}</span></p>
        </div>
        <h4>🧠 Key Factors Influencing This Prediction:</h4>
        <ul class="reasons-list">
          ${explainJson.top_reasons.map((r) => `<li>${r}</li>`).join("")}
        </ul>
        <div class="recommendation">
          <h4>💡 Recommendation:</h4>
          <p>${getRecommendation(predictJson.return_probability, riskLevel)}</p>
        </div>
      </div>
    `;

    await loadAdditionalInfo(data);
    await loadVisualization();
  } catch (err) {
    resultDiv.innerHTML = `
      <div class="error-container">
        <p style="color: red;">❌ <strong>Error:</strong> ${err.message}</p>
        <p>Please make sure the backend server is running on port 8000.</p>
        <p><small>Run: <code>uvicorn main:app --reload</code></small></p>
      </div>
    `;
  }
});

// 💡 Recommendation Logic
function getRecommendation(prob, level) {
  if (level === "High") return "⚠️ High return risk. Take immediate steps to reduce risk.";
  if (level === "Medium") return "⚡ Moderate return risk. Monitor and follow up.";
  return "✅ Low return risk. Continue engagement.";
}

// 📊 Load Chart Visualization
async function loadVisualization() {
  try {
    const res = await fetch("http://127.0.0.1:8000/visualize");
    const html = await res.text();
    vizDiv.innerHTML = `<div class="visualization-container">${html}</div>`;
  } catch (error) {
    vizDiv.innerHTML = `<div class="error-container"><p>❌ Visualization failed to load.</p></div>`;
  }
}

// 📁 Load Additional Info (Discounts + Recommendations + Dashboard)
// 📁 Load Additional Info (Discounts + Recommendations + Dashboard)
async function loadAdditionalInfo(data) {
  try {
    const [discountRes, recommendRes, dashboardRes] = await Promise.all([
      fetch("http://127.0.0.1:8000/get-discount", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ Product_Category: data.Product_Category }),
      }),
      fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          Product_Category: data.Product_Category,
          Product_Size: data.Product_Size,
        }),
      }),
      fetch("http://127.0.0.1:8000/dashboard-data"),
    ]);

    const discount = await discountRes.json();
    const recommend = await recommendRes.json();
    const dashboard = await dashboardRes.json();

    infoDiv.innerHTML = `
      <div class="result-container extra-section">
        <h3>🎁 Discount Suggestion</h3>
        <p><strong>${discount.discount}</strong> - ${discount.message}</p>

        <h3>🔄 Recommended Alternatives</h3>
        <p>${recommend.recommended_product || "No alternative found."}</p>

        <h3>📊 Dashboard Summary</h3>
        <p><strong>Total Returns:</strong> ${dashboard.total_returns}</p>
        <p><strong>High Risk Returns:</strong> ${dashboard.high_risk_returns}</p>
        <h4>Returns by Category:</h4>
        <ul>${Object.entries(dashboard.return_by_category).map(([k, v]) => `<li>${k}: ${v}</li>`).join("")}</ul>
        <h4>Avg. Ratings by Category:</h4>
        <ul>${Object.entries(dashboard.average_rating_by_category).map(([k, v]) => `<li>${k}: ${v}</li>`).join("")}</ul>
        <h4>📦 Stock Summary:</h4>
        <ul>${Object.entries(dashboard.stock_summary).map(([k, v]) => `<li>${k}: ${v}</li>`).join("")}</ul>
      </div>
    `;
  } catch (err) {
    infoDiv.innerHTML = `<div class="error-container"><p>⚠️ Could not load additional information.</p></div>`;
  }
}
// 📜 Load Logs
async function loadLogs() {
  try {
    const response = await fetch("http://127.0.0.1:8000/view-logs");
    const data = await response.json();
    const logsArea = document.getElementById("logs-output");
    logsArea.textContent = data.logs || "No logs available.";
  } catch (error) {
    const logsArea = document.getElementById("logs-output");
    logsArea.textContent = `❌ Failed to load logs: ${error.message}`;
  }
}
