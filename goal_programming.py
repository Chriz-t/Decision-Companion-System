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

    def explain(self, row, goals, weights):
        """Generate a human-readable explanation for why this laptop was recommended."""
        lines = []
        total = sum(weights.values()) or 1

        # Price
        price_pct = (weights.get("price", 0) / total) * 100
        if row["price"] <= goals["price"]:
            savings = goals["price"] - row["price"]
            lines.append(f"✅ Price of ₹{int(row['price']):,} is within your ₹{int(goals['price']):,} budget — saving you ₹{int(savings):,} (priority: {price_pct:.0f}%).")
        else:
            over = row["price"] - goals["price"]
            lines.append(f"⚠️ Price of ₹{int(row['price']):,} exceeds your ₹{int(goals['price']):,} budget by ₹{int(over):,} (priority: {price_pct:.0f}%).")

        # RAM
        ram_pct = (weights.get("ram", 0) / total) * 100
        if row["ram"] >= goals["ram"]:
            lines.append(f"✅ RAM of {int(row['ram'])} GB meets your {int(goals['ram'])} GB target (priority: {ram_pct:.0f}%).")
        else:
            lines.append(f"⚠️ RAM of {int(row['ram'])} GB falls short of your {int(goals['ram'])} GB target (priority: {ram_pct:.0f}%).")

        # CPU
        cpu_pct = (weights.get("cpu", 0) / total) * 100
        if row["cpu_score"] >= goals["cpu"]:
            lines.append(f"✅ CPU score of {row['cpu_score']:.1f} meets your target of {goals['cpu']:.1f} (priority: {cpu_pct:.0f}%).")
        else:
            lines.append(f"⚠️ CPU score of {row['cpu_score']:.1f} is below your target of {goals['cpu']:.1f} (priority: {cpu_pct:.0f}%).")

        # GPU
        gpu_pct = (weights.get("gpu", 0) / total) * 100
        if row["gpu"] >= goals["gpu"]:
            lines.append(f"✅ GPU of {row['gpu']:.1f} GB meets your {goals['gpu']:.1f} GB target (priority: {gpu_pct:.0f}%).")
        else:
            lines.append(f"⚠️ GPU of {row['gpu']:.1f} GB is below your {goals['gpu']:.1f} GB target (priority: {gpu_pct:.0f}%).")

        # Storage
        storage_pct = (weights.get("storage", 0) / total) * 100
        if row["total_storage"] >= goals["storage"]:
            lines.append(f"✅ Storage of {int(row['total_storage'])} GB meets your {int(goals['storage'])} GB target (priority: {storage_pct:.0f}%).")
        else:
            lines.append(f"⚠️ Storage of {int(row['total_storage'])} GB falls short of your {int(goals['storage'])} GB target (priority: {storage_pct:.0f}%).")

        return lines