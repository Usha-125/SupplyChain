from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import ReturnPrediction, Stock
import matplotlib.pyplot as plt
import io
import base64

def stock_bar_chart():
    try:
        db: Session = SessionLocal()

        # 1. Return count by product category
        return_counts = db.query(
            ReturnPrediction.product_category,
            func.count(ReturnPrediction.id)
        ).group_by(ReturnPrediction.product_category).all()

        # 2. Average return probability by category
        avg_probs = db.query(
            ReturnPrediction.product_category,
            func.avg(ReturnPrediction.return_probability)
        ).group_by(ReturnPrediction.product_category).all()

        db.close()

        if not return_counts:
            return_counts = [("No data", 0)]
        if not avg_probs:
            avg_probs = [("No data", 0)]

        categories1 = [r[0] for r in return_counts]
        counts = [r[1] for r in return_counts]

        categories2 = [r[0] for r in avg_probs]
        avg_returns = [round(r[1] * 100, 2) for r in avg_probs]  # Convert to %

        # Plotting
        fig, axs = plt.subplots(2, 1, figsize=(7, 6))
        fig.tight_layout(pad=4)

        # Chart 1 - Return count
        bars1 = axs[0].bar(categories1, counts, color='mediumpurple')
        axs[0].set_title("📦 Return Count by Product Category", fontsize=11)
        axs[0].set_ylabel("Count")
        for bar in bars1:
            height = bar.get_height()
            axs[0].annotate(f'{height}', xy=(bar.get_x() + bar.get_width()/2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=8)

        # Chart 2 - Avg return probability
        bars2 = axs[1].bar(categories2, avg_returns, color='tomato')
        axs[1].set_title("📈 Avg Return Probability by Category", fontsize=11)
        axs[1].set_ylabel("Probability (%)")
        axs[1].set_ylim(0, 100)
        for bar in bars2:
            height = bar.get_height()
            axs[1].annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=8)

        # Save as base64
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()
        plt.close(fig)

        # Return as embeddable HTML
        return f'<h3>📊 Dashboard Charts</h3><img src="data:image/png;base64,{image_base64}" alt="Chart" style="width:100%; max-width:600px;">'

    except Exception as e:
        return f"<p>Plotting Error: {str(e)}</p>"
