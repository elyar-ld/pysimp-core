from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SurgitType(str, Enum):
    """A.II.1/4: Surgit Labeling (Normal, Safety, CE)"""
    NORMAL = "normal"
    SAFETY = "safety"
    CE_SUBSTITUTION = "ce_substitution"
    CE_ADDITION = "ce_addition"

class DeviationCause(str, Enum):
    """A.II.5: Deviation Cause Attribution"""
    INTRINSIC = "intr"
    PATIENT = "pat"
    EXTERNAL = "ext"
    DECISION = "dec"

class PostoperativeOutcome(BaseModel):
    """
    A.II.1b: Postoperative Outcomes (Required for Calibration)
    """
    complication_type: str = Field(..., description="Complication k from Set K")
    time_window: str = Field(..., description="e.g. 'intraop', '30-day'")
    severity_grade: Optional[str] = Field(None, description="e.g. 'Clavien-Dindo IIIb'")

class SurgitEvent(BaseModel):
    """
    A single execution instance of a Surgit in a real surgery trace.
    Annex II: Minimum Required Record.
    """
    surgit_id: str
    timestamp_start: datetime
    timestamp_end: datetime
    
    # A.II.1/4: Surgit Type Label
    surgit_type: SurgitType = Field(SurgitType.NORMAL, description="Normal, Safety, or CE-labeled")
    
    # A.II.3 Noise Capture
    noise_patient: float = Field(1.0, ge=0.0, alias="n_t") 
    noise_external: float = Field(1.0, ge=0.0, alias="e_t")
    
    is_deviation: bool = Field(False, description="Marked as a deviation from norm")
    
    # A.II.5: Strict Deviation Cause
    deviation_cause: Optional[DeviationCause] = Field(None, description="Cause: intr, pat, ext, dec")
    
    # A.II.1.6: Postoperative-risk tags
    risk_tags: List[str] = Field(default_factory=list, description="Tags relevant to PCP (e.g., 'bleeding_risk')")
    
    # Enriched attribute from template checks
    complexity_weight: Optional[float] = Field(None, description="Complexity weight from template")
    
    # Annex I.3: External Pauses
    is_pause: bool = Field(False, description="Marked as an external pause (A.I.3)")

class SurgicalTrace(BaseModel):
    """
    Represents the full event log of a performed surgery (A.II.1).
    """
    procedure_id: str
    patient_id: str
    events: List[SurgitEvent] = Field(default_factory=list)
    
    # A.II.1b Outcome Records
    outcomes: List[PostoperativeOutcome] = Field(default_factory=list, description="Observed postoperative complications")
