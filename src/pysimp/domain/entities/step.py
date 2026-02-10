
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from .surgit import Surgit

class Step(BaseModel):
    """
    Represents a major 'Phase' or 'Step' in the procedure (e.g., 'Dissection').
    Defined in Annex I.1: "The complete set of steps and surgits".
    """
    id: str = Field(..., description="Unique Step ID (e.g., P7)")
    name: str = Field(..., description="Human-readable name of the step")
    description: Optional[str] = Field(None, description="Clinical description")
    
    # Stratification: A step contains ordered surgits
    surgits: Dict[str, Surgit] = Field({}, description="Dictionary of surgits belonging to this step")
    
    # Step-Specific Weights (Annex I.1)
    weight_wt: float = Field(1.0, description="Step criticality weight w_t")
    
    class Config:
        frozen = True
