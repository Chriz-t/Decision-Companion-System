from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from data_preprocessing import DataPreprocessor
from goal_programming import GoalProgramming

app = Flask(__name__)

# ─── Load & preprocess data once at startup ───────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "laptops.csv")
preprocessor = DataPreprocessor(DATA_PATH)
data = preprocessor.preprocess()

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    # Pass some stats for the landing page
    stats = {
        "total_laptops": len(data),
        "brands": sorted(data["brand"].dropna().unique().tolist()),
        "min_price": int(data["price"].min()),
        "max_price": int(data["price"].max()),
        "min_ram": int(data["ram"].min()),
        "max_ram": int(data["ram"].max()),
    }
    return render_template("index.html", stats=stats)


@app.route("/recommend", methods=["POST"])
def recommend():
    body = request.get_json()

    goals = {
        "price":   float(body["price"]),
        "ram":     float(body["ram"]),
        "cpu":     float(body["cpu"]),
        "gpu":     float(body["gpu"]),
        "storage": float(body["storage"]),
    }

    raw_points = {
        "price":   float(body["w_price"]),
        "ram":     float(body["w_ram"]),
        "cpu":     float(body["w_cpu"]),
        "gpu":     float(body["w_gpu"]),
        "storage": float(body["w_storage"]),
    }

    total = sum(raw_points.values()) or 1
    weights = {k: v / total for k, v in raw_points.items()}

    gp = GoalProgramming(goals, weights)
    ranked = gp.rank_laptops(data.copy())

    top = ranked[[
        "brand", "model",
        "processor_brand", "processor_name", "processor_gnrtn",
        "ram", "total_storage", "ssd_gb", "hdd_gb", "gpu",
        "display_size", "warranty", "star_rating",
        "price", "cpu_score", "deviation_score"
    ]].head(10)

    results = []
    for _, row in top.iterrows():
        explanation = gp.explain(row, goals, weights)
        results.append({
            "brand":         str(row["brand"]),
            "model":         str(row["model"]),
            "processor":     f'{row["processor_brand"]} {row["processor_name"]} ({row["processor_gnrtn"]} Gen)',
            "ram":           int(row["ram"]),
            "storage":       int(row["total_storage"]),
            "ssd_gb":        int(row["ssd_gb"]),
            "hdd_gb":        int(row["hdd_gb"]),
            "gpu":           float(round(row["gpu"], 1)),
            "display":       float(round(row["display_size"], 1)),
            "warranty":      str(row["warranty"]),
            "rating":        float(round(row["star_rating"], 1)),
            "price":         int(row["price"]),
            "cpu_score":     float(round(row["cpu_score"], 2)),
            "deviation":     float(round(row["deviation_score"], 4)),
            "explanation":   explanation,
        })

    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(debug=True)
