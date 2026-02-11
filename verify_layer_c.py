
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pysimp.domain.entities.surgit import Surgit, SecurityScope
from pysimp.domain.entities.step import Step
from pysimp.domain.entities.template import NormativeTemplate
from pysimp.domain.entities.trace import SurgicalTrace, SurgitEvent
from pysimp.application.use_cases.run_simulation import RunSimulation
from pysimp.application.interfaces.repository import TraceRepository

# Mock Repository
class MockTraceRepo(TraceRepository):
    def __init__(self, trace):
        self.trace = trace
    def get_trace(self, trace_id):
        return self.trace
    def save_trace(self, trace):
        pass

def test_layer_c_dynamics():
    # 1. Setup Data
    # Surgit 1: High Deviation
    s1 = Surgit(
        id="S1", name="Step 1", 
        intrinsic_deviation=0.5, 
        security_scope="imm"
    )
    # Surgit 2: Low Deviation
    s2 = Surgit(
        id="S2", name="Step 2", 
        intrinsic_deviation=0.1, 
        security_scope="imm"
    )
    
    step = Step(id="Step1", name="Step 1", surgits={"S1": s1, "S2": s2})
    
    template = NormativeTemplate(
        procedure_type="Layer C Test", version="1.0",
        steps={"Step1": step},
        structure_definition={},
        dynamics_definition={'provenance_decay': 0.5} # 50% decay per step
    )
    
    # Trace Events
    e1 = SurgitEvent(surgit_id="S1", timestamp_start=datetime.now(), timestamp_end=datetime.now())
    e2 = SurgitEvent(surgit_id="S2", timestamp_start=datetime.now(), timestamp_end=datetime.now())
    
    trace = SurgicalTrace(procedure_id="Proc1", patient_id="Pat1", events=[e1, e2])
    
    # 2. Expected Calculation
    # Event 1 (S1): 
    # delta_final = 0.5. 
    # H_1 = [0.5]. 
    # X_1 burden += 0.5 * 1 * 1 = 0.5.
    
    # Event 2 (S2):
    # delta_final = 0.1.
    # H_2 update:
    #   old H_1 decays: 0.5 * 0.5 = 0.25
    #   new H_2 = [0.25, 0.1]
    # X_2 burden += 0.1 * 1 * 1 = 0.1 -> Total 0.6.
    
    expected_burden = 0.6
    expected_prov_len = 2
    
    # 3. Run Simulation
    repo = MockTraceRepo(trace)
    use_case = RunSimulation(repo)
    result = use_case.execute("Proc1", template=template)
    
    print(f"Calculated Burden: {result['final_clinical_burden']}")
    print(f"Expected Burden: {expected_burden}")
    print(f"Provenance Length: {result['provenance_vector_length']}")
    
    assert abs(result['final_clinical_burden'] - expected_burden) < 1e-6
    assert result['provenance_vector_length'] == expected_prov_len
    
    print("Layer C Verification Passed!")

if __name__ == "__main__":
    test_layer_c_dynamics()
