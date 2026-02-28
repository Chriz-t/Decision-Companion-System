from data_preprocessing import DataPreprocessor
from ahp import AHP
from mcda import MCDA
import numpy as np

preprocessor=DataPreprocessor("data/laptops.csv")
data=preprocessor.preprocess()
print(data)



def build_ahp_matrix(criteria):
    """
    Creates pairwise comparison matrix from user input
    """

    n = len(criteria)
    matrix = np.ones((n, n))  # diagonal initialized to 1

    print("\nUse Saaty scale (1-9)")
    print("If first criterion is less important, enter reciprocal (e.g., 1/3)\n")

    for i in range(n):
        for j in range(i + 1, n):

            while True:
                try:
                    print(f"\nCompare: {criteria[i]} vs {criteria[j]}")
                    value = input(
                        f"How much more important is {criteria[i]} over {criteria[j]}? : "
                    )

                    # Handle fraction input like 1/3
                    if "/" in value:
                        num, den = value.split("/")
                        value = float(num) / float(den)
                    else:
                        value = float(value)

                    if value <= 0:
                        raise ValueError

                    matrix[i][j] = value
                    matrix[j][i] = 1 / value
                    break

                except:
                    print("Invalid input. Please enter a number like 3 or 1/5.")

    return matrix

criteria = ["RAM", "GPU", "Price", "Storage", "Weight", "CPU"]

comp_matrix = build_ahp_matrix(criteria)

print("\nGenerated AHP Matrix:\n")
print(comp_matrix)

ahp = AHP(comp_matrix)
result = ahp.get_weights()

weights = result["weights"]
print(criteria)
print("Weights:", weights)
print("CR:", result["consistency_ratio"])

criteria_cols = [
    "ram_scaled",
    "gpu_scaled",
    "price_scaled",
    "total_storage_scaled",
    "weight_type_scaled",
    "cpu_score_scaled"
]

mcda = MCDA(weights, criteria_cols)

ranked_df = mcda.compute_scores(data)

print(ranked_df.head(10))