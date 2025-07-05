const form = document.getElementById("predictForm");
const resultDiv = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Show loading state
  resultDiv.innerHTML = `<p>🔄 Processing prediction...</p>`;

  const formData = new FormData(form);

  // Create the data object matching the expected API format
  const data = {
    Product_Category: formData.get("Product_Category"),
    Product_Size: formData.get("Product_Size"),
    Customer_Region: formData.get("Customer_Region"),
    Customer_Age_Group: formData.get("Customer_Age_Group"),
    Past_Return_Count: parseInt(formData.get("Past_Return_Count")),
    Product_Rating: parseFloat(formData.get("Product_Rating")),
    Delivery_Time_Days: parseInt(formData.get("Delivery_Time_Days"))
  };

  try {
    // Make both API calls
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
      })
    ]);

    if (!predictRes.ok || !explainRes.ok) {
      throw new Error(`API Error: ${predictRes.status} | ${explainRes.status}`);
    }

    const predictJson = await predictRes.json();
    const explainJson = await explainRes.json();

    // Display results
    const probabilityPercent = (predictJson.return_probability * 100).toFixed(1);
    const riskLevel = predictJson.return_probability > 0.7 ? "High" : 
                     predictJson.return_probability > 0.4 ? "Medium" : "Low";
    
    const riskColor = riskLevel === "High" ? "#e53e3e" : 
                     riskLevel === "Medium" ? "#dd6b20" : "#38a169";

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
          ${explainJson.top_reasons.map(reason => `<li>${reason}</li>`).join("")}
        </ul>
        
        <div class="recommendation">
          <h4>💡 Recommendation:</h4>
          <p>${getRecommendation(predictJson.return_probability, riskLevel)}</p>
        </div>
      </div>
    `;
  } catch (err) {
    console.error("Error:", err);
    resultDiv.innerHTML = `
      <div class="error-container">
        <p style="color: red;">❌ <strong>Error:</strong> ${err.message}</p>
        <p>Please make sure the backend server is running on port 8000.</p>
        <p><small>Run: <code>uvicorn main:app --reload</code> in the backend directory</small></p>
      </div>
    `;
  }
});

function getRecommendation(probability, riskLevel) {
  if (riskLevel === "High") {
    return "⚠️ High return risk detected. Consider improving product quality, reducing delivery time, or offering additional customer support.";
  } else if (riskLevel === "Medium") {
    return "⚡ Moderate return risk. Monitor this customer and consider proactive engagement to ensure satisfaction.";
  } else {
    return "✅ Low return risk. This appears to be a satisfied customer with low likelihood of return.";
  }
}