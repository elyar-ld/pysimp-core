
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from .surgit import Surgit
from .step import Step

class NormativeTemplate(BaseModel):
    """
    Represents the 'ideal' or 'standard' procedure definition (The Frozen Template).
    Contains:
    - The set of valid Surgits (transitions).
    - The structural rules (Petri Net definition).
    - Global parameters (q, alpha, beta).
    
    A.I.2 Model Freezing Rule: Immutability enforced via frozen=True.
    """
    model_config = ConfigDict(frozen=True)
    procedure_type: str = Field(..., description="Name of the procedure (e.g., 'Laparoscopic Appendectomy')")
    version: str = Field(..., description="Version of the template (e.g., '1.0.0')")
    
    # Stratification (Annex I.1)
    steps: Dict[str, Step] = Field(..., description="Steps composing the procedure")
    
    # Layer B: Topology
    # Forbidden states (markings that are clinically invalid)
    forbidden_states: List[List[str]] = Field([], description="List of forbidden markings (e.g. [['p_open', 'p_closed']])")

    # Layer C: Dynamics (State components and decay)
    dynamics_definition: Dict[str, Any] = Field({}, description="Configuration for state decay/update functions")

    # Layer D: Global Scoring & Shapley
    shapley_convention: str = Field("default", description="Name of the characteristic function v(S) to use")
    
    # Layer E: Complication Set K and calibration (Annex I.1)
    complication_set_k: List[str] = Field([], description="List of complication types k (PCP)")
    calibration_coefficients: Dict[str, Any] = Field({}, description="Coefficients for SIM-PCP bridge (alpha_k, beta_k, etc.)")
    
    # Structural definition for Layer B (Petri Net)
    structure_definition: Any = Field(..., description="Petri Net structure (places, transitions, arcs, initial_marking)")
    
    # Global Parameters (Layer D)
    tsallis_q: float = Field(1.0, description="Tsallis q parameter for entropy")
    weight_alpha: float = Field(1.0, description="Weight for Saturation")
    weight_beta: float = Field(1.0, description="Weight for Entropy")
    
    def get_surgit(self, surgit_id: str) -> Optional[Surgit]:
        """
        Helper to find a surgit by ID across all steps.
        """
        for step in self.steps.values():
            if surgit_id in step.surgits:
                return step.surgits[surgit_id]
        return None
