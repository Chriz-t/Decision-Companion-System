import pandas as pd


class GoalProgramming:

    def __init__(self, goals, weights):
        """
        goals: dictionary of target values
        weights: importance weights
        """

        self.goals = goals
        self.weights = weights

    def compute_deviation(self, row):
        total_deviation = 0

        # Price (lower is better)
        if row["price"] > self.goals["price"]:
            deviation = (row["price"] - self.goals["price"])/self.goals["price"]
            total_deviation += deviation * self.weights["price"]

        # RAM (higher is better)
        if row["ram"] < self.goals["ram"]:
            deviation = (self.goals["ram"] - row["ram"])/self.goals["ram"]
            total_deviation += deviation * self.weights["ram"]

        # Storage
        if row["total_storage"] < self.goals["storage"]:
            deviation = (self.goals["storage"] - row["total_storage"])/self.goals["storage"]
            total_deviation += deviation * self.weights["storage"]

        # CPU
        if row["cpu_score"] < self.goals["cpu"]:
            deviation =(self.goals["cpu"] - row["cpu_score"])/self.goals["cpu"]
            total_deviation += deviation * self.weights["cpu"]

        # GPU
        if row["gpu"] < self.goals["gpu"]:
            deviation = (self.goals["gpu"] - row["gpu"])/self.goals["gpu"]
            total_deviation += deviation * self.weights["gpu"]

        return total_deviation

    def rank_laptops(self, df):

        df["deviation_score"] = df.apply(self.compute_deviation, axis=1)

        ranked = df.sort_values("deviation_score")

        return ranked