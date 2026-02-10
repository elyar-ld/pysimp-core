
from pydantic import BaseModel, Field
from typing import Optional, Dict

class Surgit(BaseModel):
    """
    Represents the smallest unit of surgical work or action (Surgit).
    Analogous to a 'transition' in the Petri Net layer.
    """
    id: str = Field(..., description="Unique identifier for the surgit (e.g., P7S2)")
    name: str = Field(..., description="Human-readable name of the surgit")
    description: Optional[str] = Field(None, description="Detailed description of the action")
    is_mandatory: bool = Field(True, description="Whether this surgit is mandatory for structural validity")
    is_safety: bool = Field(False, description="Whether this surgit is a designated safety step")
    
    # Layer A/E attributes
    base_probability: float = Field(1.0, ge=0.0, le=1.0, description="Base success probability")
    complexity_weight: float = Field(1.0, ge=0.0, description="Complexity weight for entropy calc")

    class Config:
        frozen = True # Domain entities should be immutable where possible
