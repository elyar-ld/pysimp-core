
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SurgitEvent(BaseModel):
    """
    A single execution instance of a Surgit in a real surgery trace.
    """
    surgit_id: str
    timestamp_start: datetime
    timestamp_end: datetime
    
    # Noise factors (Layer C/E) - Defaulting to 1.0 (no noise)
    noise_patient: float = Field(1.0, ge=0.0, alias="n_t") 
    noise_external: float = Field(1.0, ge=0.0, alias="e_t")
    
    is_deviation: bool = Field(False, description="Marked as a deviation from norm")
    deviation_cause: Optional[str] = Field(None, description="Cause: intr, pat, ext, dec")
    
    # Enriched attribute from template during analysis
    complexity_weight: Optional[float] = Field(None, description="Complexity weight from template")

class SurgicalTrace(BaseModel):
    """
    Represents the full event log of a performed surgery.
    """
    procedure_id: str
    patient_id: str
    events: List[SurgitEvent] = Field(default_factory=list)
