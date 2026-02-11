
import numpy as np
from typing import List

class LayerD:
    """
    Layer D: Global Scoring and Tsallis Entropy.
    Implements Equation (27) for Tsallis Entropy S_q(SIM).
    """
    
    @staticmethod
    def calculate_step_linearity(surgit_final_deviations: List[float]) -> float:
        """
        D1. Step Linearity (pi_t)
        Probability that step t is executed linearly (all surgits correct).
        pi_t = Product(pi_{t,s}) = Product(1 - delta_{t,s}^(final))
        """
        pi_t = 1.0
        for delta in surgit_final_deviations:
            pi_t *= (1.0 - delta)
        return pi_t

    @staticmethod
    def calculate_step_deviation(pi_t: float) -> float:
        """
        D2. Step Deviation (delta_t)
        delta_t = 1 - pi_t
        """
        return 1.0 - pi_t

    @staticmethod
    def calculate_step_entropy(pi_t: float, q: float) -> float:
        """
        D3. Tsallis Entropy (Fragility) per Step S_q(t)
        S_q(t) = 1/(q-1) * [1 - (pi_t^q + delta_t^q)]
        """
        if q == 1.0:
            # Limit q->1 is Shannon: -[pi * ln(pi) + (1-pi)*ln(1-pi)]
            delta_t = 1.0 - pi_t
            if pi_t <= 0 or delta_t <= 0: return 0.0
            return -(pi_t * np.log(pi_t) + delta_t * np.log(delta_t))
            
        delta_t = 1.0 - pi_t
        term = (pi_t ** q) + (delta_t ** q)
        return (1.0 - term) / (q - 1.0)

    @staticmethod
    def q_add(x: float, y: float, q: float) -> float:
        """
        Non-extensive addition operator (x (+)q y).
        x (+)q y = x + y + (1-q)xy
        """
        return x + y + (1.0 - q) * x * y

    @staticmethod
    def calculate_global_entropy(step_entropies: List[float], q: float) -> float:
        """
        D5. Global Entropy (S_q(SIM)) using q-sum aggregation.
        S_q(SIM) = S_q(1) (+)q S_q(2) (+)q ...
        """
        if not step_entropies:
            return 0.0
            
        s_sim = step_entropies[0]
        for s_t in step_entropies[1:]:
            s_sim = LayerD.q_add(s_sim, s_t, q)
            
        return s_sim

    @staticmethod
    def calculate_global_score(
        rho_sim: float, 
        s_q_sim: float, 
        alpha: float = 1.0, 
        beta: float = 1.0
    ) -> float:
        """
        D7. Global SIM Score
        Score = alpha * rho_sim + beta * S_q(SIM)
        """
        return (alpha * rho_sim) + (beta * s_q_sim)
