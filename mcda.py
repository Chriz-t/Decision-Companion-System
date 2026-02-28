import numpy as np

class MCDA:
    
    def __init__(self, weights, criteria_columns):
        """
        weights: numpy array from AHP
        criteria_columns: list of scaled column names
        """
        self.weights = weights
        self.criteria_columns = criteria_columns
    
    def compute_scores(self, df):
        """
        Computes weighted score for each alternative
        """
        matrix = df[self.criteria_columns].values
        
        scores = np.dot(matrix, self.weights)
        
        df["final_score"] = scores
        
        return df.sort_values(by="final_score", ascending=False)