
import numpy as np
from typing import List

class LayerD:
    """
    Layer D: Global Scoring and Tsallis Entropy.
    Implements Equation (27) for Tsallis Entropy S_q(SIM).
    """
    
    @staticmethod
    def tsallis_entropy(probabilities: List[float], q: float) -> float:
        """
        Calculates the Tsallis entropy for a set of probabilities.
        Formula: S_q = (1 - sum(p^q)) / (q - 1)
        """
        if q == 1.0:
            # Converges to Shannon entropy
            return -np.sum([p * np.log(p) for p in probabilities if p > 0])
        
        sum_pq = np.sum([p ** q for p in probabilities])
        return (1.0 - sum_pq) / (q - 1.0)

    @staticmethod
    def calculate_global_score(
        saturation: float, 
        entropy: float, 
        alpha: float = 1.0, 
        beta: float = 1.0
    ) -> float:
        """
        Combines Saturation (Layer A) and Entropy (Layer D) into a global score.
        Eq (32-ish) simplified: eta = alpha * Delta + beta * S_q
        """
        return (alpha * saturation) + (beta * entropy)
