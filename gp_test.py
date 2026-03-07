from data_preprocessing import DataPreprocessor
from goal_programming import GoalProgramming
import numpy as np


preprocessor=DataPreprocessor("data/laptops.csv")
data=preprocessor.preprocess()

# goals = {
#     "price": 80000,
#     "ram": 16,
#     "storage": 512,
#     "cpu": 7,
#     "gpu": 6
# }

# weights = {
#     "price": 0.3,
#     "ram": 0.2,
#     "storage": 0.1,
#     "cpu": 0.2,
#     "gpu": 0.2
# }

# -----------------------------
# GET USER GOALS
# -----------------------------

print("\nEnter your desired laptop goals:\n")

goals = {}

goals["price"] = float(input("Maximum price you are willing to pay: "))
goals["ram"] = float(input("Minimum RAM required (GB): "))
goals["cpu"] = float(input("Minimum CPU score required: "))
goals["gpu"] = float(input("Minimum GPU score required: "))
goals["storage"] = float(input("Minimum storage required (GB): "))


# -----------------------------
# POINT ALLOCATION METHOD
# -----------------------------

print("\nDistribute 100 points across the criteria based on importance.\n")

points = {}

points["price"] = float(input("Points for PRICE: "))
points["ram"] = float(input("Points for RAM: "))
points["cpu"] = float(input("Points for CPU: "))
points["gpu"] = float(input("Points for GPU: "))
points["storage"] = float(input("Points for STORAGE: "))


# -----------------------------
# NORMALIZE WEIGHTS
# -----------------------------

total_points = sum(points.values())

weights = {}

for key in points:
    weights[key] = points[key] / total_points

gp = GoalProgramming(goals, weights)

ranked_df = gp.rank_laptops(data)

print(ranked_df[["brand","model","processor_brand","processor_name","processor_gnrtn","ram","total_storage","price","deviation_score"]].head(10))