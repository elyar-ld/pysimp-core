
import math
from itertools import combinations
from typing import List, Dict, Callable

class LayerE:
    """
    Layer E: Probabilistic Bridge and Shapley Attribution.
    """
    
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
