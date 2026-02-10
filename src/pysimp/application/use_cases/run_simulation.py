
from pysimp.application.interfaces.repository import TraceRepository
from pysimp.domain.entities.trace import SurgicalTrace
from pysimp.domain.services.layer_a import LayerA
from pysimp.domain.services.layer_d import LayerD
from pysimp.domain.services.layer_e import LayerE
from pysimp.domain.services.layer_b import LayerB
from typing import List, Any, Optional

class RunSimulation:
    def __init__(self, trace_repo: TraceRepository, layer_b_adapter: Optional[LayerB] = None):
        self.trace_repo = trace_repo
        self.layer_b = layer_b_adapter
        
    def execute(self, trace_id: str, template: Any = None, q: float = 1.0) -> dict:
        """
        Orchestrates the simulation for a given trace.
        """
        trace = self.trace_repo.get_trace(trace_id)
        if not trace:
            raise ValueError(f"Trace {trace_id} not found")

        validation_result = {"valid": True, "message": "No template provided for validation"}

        if template and self.layer_b:
            # 0. Validate Structure (Layer B)
            is_valid = self.layer_b.validate_structure(trace.events, template)
            if not is_valid:
                validation_result = {"valid": False, "message": "Structural validation failed (Layer B)"}
                # We can choose to halt or continue with penalty. 
                # SIM-P usually flags it but calculates score anyway (as 'invalid' score).

        # 1. Calculate Saturation (Layer A)
        # Assuming events have 'complexity' attribute or we map it from template
        if template:
             # Enrich events with template data if needed
             for event in trace.events:
                 surgit_def = template.get_surgit(event.surgit_id)
                 if surgit_def:
                     # Since Pydantic models validate assignments, we need to ensure the attribute exists
                     # or use object.__setattr__ if frozen, but here we added the field optional.
                     event.complexity_weight = surgit_def.complexity_weight

        saturation = LayerA.calculate_saturation(trace.events)
        
        # 2. Calculate Entropy (Layer D)
        # Map events to probabilities (using template base_probability)
        probabilities = []
        if template:
            for event in trace.events:
                 surgit_def = template.get_surgit(event.surgit_id)
                 prob = surgit_def.base_probability if surgit_def else 0.1
                 probabilities.append(prob)
        else:
            probabilities = [0.1 for _ in trace.events]

        entropy = LayerD.tsallis_entropy(probabilities, q)
        
        # 3. Calculate Global Score
        global_score = LayerD.calculate_global_score(saturation, entropy)
        
        return {
            "trace_id": trace_id,
            "validation": validation_result,
            "saturation": saturation,
            "tsallis_entropy": entropy,
            "global_score": global_score
        }
