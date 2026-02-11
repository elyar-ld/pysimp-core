
import math

class LayerA:
    """
    Layer A: Axiomatics and Probability Saturation.
    Implements Equation (26) for saturation (Delta_tot) or simplified accumulation.
    """
    @staticmethod
    def calculate_patient_amplification(intrinsic_deviation: float, n_t: float) -> float:
        """
        Calculates deviation amplification due to patient-related noise.
        Equation (3): delta_pat = 1 - (1 - delta_intr)^n_t
        """
        if n_t < 1.0:
            raise ValueError("Patient noise factor n_t must be >= 1.0")
        return 1.0 - math.pow(1.0 - intrinsic_deviation, n_t)

    @staticmethod
    def calculate_total_deviation(intrinsic_deviation: float, n_t: float, e_t: float) -> float:
        """
        Calculates total deviation aggregating all noise sources before mitigation.
        Equation (5): delta_tot = 1 - (1 - delta_intr)^(n_t * e_t)
        """
        if n_t < 1.0 or e_t < 1.0:
            raise ValueError("Noise factors n_t and e_t must be >= 1.0")
        
        exponent = n_t * e_t
        return 1.0 - math.pow(1.0 - intrinsic_deviation, exponent)

    @staticmethod
    def apply_mitigation(total_deviation: float, mitigation_factor: float) -> float:
        """
        Applies security mitigation to the total deviation.
        Layer A' - Equation (6): delta_final = sigma * delta_tot
        """
        return mitigation_factor * total_deviation
