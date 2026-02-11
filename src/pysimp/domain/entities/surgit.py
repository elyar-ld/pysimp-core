
from pydantic import BaseModel, Field
from typing import Optional, Dict

from enum import Enum

class SecurityScope(str, Enum):
    IMMEDIATE = "imm"
    RESIDUAL = "res"
    PCP = "pcp"

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
    
    # Layer A (Axiomatics) attributes - SIM v1.2.0
    intrinsic_deviation: float = Field(0.0, ge=0.0, le=1.0, description="Intrinsic deviation probability (delta_intr, Eq 2)")
    mitigation_factor: float = Field(1.0, ge=0.0, le=1.0, description="Security mitigation factor (sigma, Eq 6). 1.0 = no mitigation.")
    security_scope: SecurityScope = Field(SecurityScope.IMMEDIATE, description="Scope of the security operator (A'4): imm, res, pcp")
    complexity_weight: float = Field(1.0, ge=0.0, description="Complexity weight for entropy calc")

    class Config:
        frozen = True # Domain entities should be immutable where possible
        use_enum_values = True
