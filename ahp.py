# ahp.py

import numpy as np


class AHP:
    """
    Analytic Hierarchy Process implementation
    Computes criteria weights using pairwise comparison matrix
    and checks consistency ratio.
    """

    # Random Index values for matrix sizes 1–10
    RI_DICT = {
        1: 0.00,
        2: 0.00,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49,
    }

    def __init__(self, comparison_matrix):
        """
        comparison_matrix: 2D list or numpy array
        """
        self.matrix = np.array(comparison_matrix, dtype=float)
        self.n = self.matrix.shape[0]

        if self.matrix.shape[0] != self.matrix.shape[1]:
            raise ValueError("Pairwise comparison matrix must be square")

    # ---------------------------------------------------
    # Step 1: Normalize matrix
    # ---------------------------------------------------
    def normalize_matrix(self):
        column_sums = self.matrix.sum(axis=0)
        normalized = self.matrix / column_sums
        return normalized

    # ---------------------------------------------------
    # Step 2: Compute weights
    # ---------------------------------------------------
    def compute_weights(self):
        normalized = self.normalize_matrix()
        weights = normalized.mean(axis=1)
        return weights

    # ---------------------------------------------------
    # Step 3: Consistency Check
    # ---------------------------------------------------
    def consistency_ratio(self):
        weights = self.compute_weights()

        # λ_max calculation
        weighted_sum = np.dot(self.matrix, weights)
        lambda_max = np.mean(weighted_sum / weights)

        CI = (lambda_max - self.n) / (self.n - 1)

        RI = self.RI_DICT.get(self.n, 1.49)

        if RI == 0:
            return 0

        CR = CI / RI
        return CR

    # ---------------------------------------------------
    # Main Method
    # ---------------------------------------------------
    def get_weights(self):
        weights = self.compute_weights()
        CR = self.consistency_ratio()

        return {
            "weights": weights,
            "consistency_ratio": CR,
            "is_consistent": CR < 0.1
        }