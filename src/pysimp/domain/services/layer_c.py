
from typing import List, Dict, Callable
from dataclasses import dataclass, field
import numpy as np

@dataclass
class ExpandedGlobalState:
    """
    Represents the Expanded Global State Z_t = (X_t, H_t) at step t.
    SIM v1.2.0 - Section 5 (Layer C)
    """
    # X_t: Clinical Degradation Vector (e.g., [blood_loss, edema, fatigue])
    # For core simplicity, we'll use a single scalar 'burden' or a dict. 
    # Let's use a dict for extensibility as X \in \mathcal{X}
    clinical_state: Dict[str, float] = field(default_factory=dict)
    
    # H_t: Provenance Vector (C3)
    # Stores residual influence of past steps k <= t.
    provenance_vector: List[float] = field(default_factory=list)

class LayerC:
    """
    Layer C: Expanded Global State Dynamics.
    Implements transition kernel and state updates (Eq 20-23).
    """

    @staticmethod
    def initialize_state() -> ExpandedGlobalState:
        """
        C4. Initialization
        Z_0 = (0, Empty)
        """
        return ExpandedGlobalState(clinical_state={}, provenance_vector=[])

    @staticmethod
    def update_provenance(
        current_provenance: List[float], 
        new_deviation: float, 
        decay_function: Callable[[float], float] = None
    ) -> List[float]:
        """
        C7. Provenance Update Rule.
        h_{k, t+1} = g(h_{k,t}) for past events (decay)
        h_{t+1, t+1} = delta_new (new event)
        """
        if decay_function is None:
            # Default g(h) = h (no decay / full memory)
            decay_function = lambda h: h
            
        # 1. Decay past influences
        next_provenance = [decay_function(h) for h in current_provenance]
        
        # 2. Append new event's final deviation
        next_provenance.append(new_deviation)
        
        return next_provenance

    @staticmethod
    def update_clinical_state(
        current_state: Dict[str, float], 
        deviation_final: float,
        n_t: float,
        e_t: float
    ) -> Dict[str, float]:
        """
        C6. Clinical State Update.
        X_{t+1} = f(X_t, delta_final, n_t, e_t)
        
        Simple Model:
        Accumulates 'general_burden' proportional to deviation * noise.
        """
        new_state = current_state.copy()
        current_burden = new_state.get('general_burden', 0.0)
        
        # Heuristic update: Burden increases with deviation amplified by context
        # dX = delta * n_t * e_t
        increment = deviation_final * n_t * e_t
        
        new_state['general_burden'] = current_burden + increment
        
        return new_state

    @staticmethod
    def transition_kernel(
        current_z: ExpandedGlobalState,
        delta_final: float,
        n_t: float,
        e_t: float,
        decay_rate: float = 1.0
    ) -> ExpandedGlobalState:
        """
        Execute full state transition Z_t -> Z_{t+1}.
        Combines C6 and C7.
        decay_rate: Factor for provenance decay (1.0 = no decay, <1.0 = decay).
        """
        # Define simple linear decay: g(h) = h * decay
        decay_func = lambda h: h * decay_rate
        
        # Update H
        next_H = LayerC.update_provenance(
            current_z.provenance_vector, 
            delta_final, 
            decay_func
        )
        
        # Update X
        next_X = LayerC.update_clinical_state(
            current_z.clinical_state,
            delta_final,
            n_t,
            e_t
        )
        
        return ExpandedGlobalState(clinical_state=next_X, provenance_vector=next_H)
