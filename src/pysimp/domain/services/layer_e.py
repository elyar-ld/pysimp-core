
import math
from itertools import combinations
from typing import List, Dict, Callable

class LayerE:
    """
    Layer E: Probabilistic Bridge and Shapley Attribution.
    """
    
    @staticmethod
    def sigmoid(eta: float) -> float:
        """
        E2. Logistic Inverse Link (D-Bridge 2)
        sigma(eta) = 1 / (1 + e^-eta)
        """
        # Clipped for numerical stability (avoid overflow in exp)
        if eta > 60: return 1.0
        if eta < -60: return 0.0
        return 1.0 / (1.0 + math.exp(-eta))

    @staticmethod
    def logit(p: float) -> float:
        """
        E1. Logit Operator (D-Bridge 1)
        logit(p) = ln(p / (1-p)) for p in (0, 1)
        """
        if p <= 0.0: return -1e9 # approx -inf
        if p >= 1.0: return 1e9  # approx +inf
        return math.log(p / (1.0 - p))

    @staticmethod
    def calculate_linear_predictor(
        alpha_k: float,
        beta_delta: float, 
        delta_sim: float,
        beta_s: float, 
        s_q_sim: float
    ) -> float:
        """
        E4. Linear Predictor (D-Bridge 4)
        eta_k = alpha_k + beta_k^(Delta) * Delta_SIM + beta_k^(S) * S_q(SIM) 
        (+ sum(gamma * delta_t) in full model, here simplified to global metrics first)
        """
        return alpha_k + (beta_delta * delta_sim) + (beta_s * s_q_sim)

    @staticmethod
    def predict_pcp_probability(eta_k: float) -> float:
        """
        E3. PCP Probability Model (D-Bridge 3)
        P_k(PCP | SIM) = sigma(eta_k)
        """
        return LayerE.sigmoid(eta_k)

    @staticmethod
    def calculate_shapley_values(
        elements: List[str], 
        value_function: Callable[[List[str]], float]
    ) -> Dict[str, float]:
        """
        Calculates Shapley values for a set of elements given a value function v(S).
        Eq (36).
        Currently implements an exponential-time algorithm (exact). 
        For many elements, Monte Carlo approximation would be needed.
        """
        shapley_values = {e: 0.0 for e in elements}
        n = len(elements)
        factorial = math.factorial
        
        for element in elements:
            # Elements excluding current one
            others = [e for e in elements if e != element]
            
            # Iterate over all subsets of others
            for k in range(len(others) + 1):
                for subset in combinations(others, k):
                    subset = list(subset)
                    
                    # Weight = |S|! * (n - |S| - 1)! / n!
                    weight = (factorial(len(subset)) * factorial(n - len(subset) - 1)) / factorial(n)
                    
                    # Marginal contribution = v(S U {i}) - v(S)
                    val_with = value_function(subset + [element])
                    val_without = value_function(subset)
                    
                    marginal = val_with - val_without
                    shapley_values[element] += weight * marginal
                    
        return shapley_values
