
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any
from .trace import PostoperativeOutcome

class StepMetric(BaseModel):
    """
    A.III.1: Step Table Row
    """
    step_id: str
    m_t: float = Field(..., description="Marking / Token status")
    pi_t: float = Field(..., description="Step Linearity")
    delta_t: float = Field(..., description="Step Deviation")
    s_q_t: float = Field(..., description="Step Tsallis Entropy")
    rho_t: float = Field(..., description="Step Risk Aggregation")
    w_t: float = Field(..., description="Step Criticality Weight")

class NoiseMetric(BaseModel):
    """
    A.III.1: Noise Table Row
    """
    step_id: str
    n_t: float
    e_t: float
    pause_duration: Optional[float] = None

class CEMetric(BaseModel):
    """
    A.III.1: CE Table Row
    """
    step_id: str
    ce_type: str # substitution/addition
    timestamp: str

class PCPMetric(BaseModel):
    """
    A.III.1: PCP Table Row
    """
    complication_type: str
    p_k_sim: float = Field(..., description="P(PCP | SIM)")
    eta_k: float = Field(..., description="Log-odds")
    
class TraceabilityEntry(BaseModel):
    """
    A.III.2: Expanded-State Traceability Summary
    """
    step_index: int
    step_id: str
    clinical_state_burden: float
    provenance_vector: List[float]

class ShapleyDecomposition(BaseModel):
    """
    A.III.4: Shapley Decomposition by Deviation Cause
    Score_SIM = Score_Ideal + Sum(Phi_i)
    """
    score_ideal: float
    phi_intrinsic: float
    phi_patient: float
    phi_external: float
    phi_decision: float
    
class SimulationReport(BaseModel):
    """
    Annex III: SIM Final Report (Standard Output)
    """
    model_config = ConfigDict(frozen=True)
    
    trace_id: str
    GlobalMetrics: Dict[str, float] = Field(..., description="S_q(SIM), rho_SIM, Score_SIM")
    
    # A.III.1 Tables
    StepTable: List[StepMetric]
    NoiseTable: List[NoiseMetric]
    CETable: List[CEMetric]
    PCPTable: List[PCPMetric]
    
    # A.III.2 Traceability
    Traceability: List[TraceabilityEntry]
    
    # A.III.4 Decomposition
    ShapleyDecomposition: ShapleyDecomposition
    
    # Validation Status
    validation_status: str = "VALID"
    validation_message: str = "Structure Valid"
