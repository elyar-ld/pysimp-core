
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

def test_sim_v1_2_0_layer_a_prime():
    # 1. Setup Data
    # Surgit 1: Security Step (Residual)
    s1_id = "S1"
    s1 = Surgit(
        id=s1_id, name="Antibiotic Prophylaxis", 
        intrinsic_deviation=0.0, # Ideal security step
        mitigation_factor=0.5,   # Reduces risk by 50%
        security_scope="res",    # Residual effect
        complexity_weight=0.1
    )
    
    # Surgit 2: Technical Step (Risk)
    s2_id = "S2"
    s2_intr_dev = 0.2
    s2 = Surgit(
        id=s2_id, name="Incision", 
        intrinsic_deviation=s2_intr_dev, 
        mitigation_factor=1.0,   # No immediate mitigation
        security_scope="imm",
        complexity_weight=1.0
    )
    
    step = Step(id="Step1", name="Step 1", surgits={s1_id: s1, s2_id: s2})
    
    template = NormativeTemplate(
        procedure_type="Test A'", version="1.2",
        steps={"Step1": step}, structure_definition={}
    )
    
    # Trace Events
    # Event 1: Security enacted
    e1 = SurgitEvent(surgit_id=s1_id, timestamp_start=datetime.now(), timestamp_end=datetime.now())
    # Event 2: Action performed (should be mitigated by S1)
    e2 = SurgitEvent(surgit_id=s2_id, timestamp_start=datetime.now(), timestamp_end=datetime.now())
    
    trace = SurgicalTrace(procedure_id="Proc1", patient_id="Pat1", events=[e1, e2])
    
    # 2. Expected Calculations
    # Event 1 (S1): 
    #   delta_intr=0 -> delta_tot=0 
    #   scope=res -> cumulative_res becomes 1.0 * 0.5 = 0.5
    #   delta_final = 0.5 * 0 = 0.0
    
    # Event 2 (S2): 
    #   delta_intr=0.2, n_t=1, e_t=1 -> delta_tot = 1 - (1-0.2)^1 = 0.2
    #   scope=imm -> sigma_imm = 1.0
    #   sigma_effective = cumulative_res (0.5) * sigma_imm (1.0) = 0.5
    #   delta_final = 0.5 * 0.2 = 0.1
    
    expected_saturation = 0.1
    
    # 3. Run Simulation
    repo = MockTraceRepo(trace)
    use_case = RunSimulation(repo)
    result = use_case.execute("Proc1", template=template)
    
    print(f"Calculated Saturation: {result['saturation']}")
    print(f"Expected Saturation: {expected_saturation}")
    
    # Allow small float error
    assert abs(result['saturation'] - expected_saturation) < 1e-6, "Residual mitigation failed!"
    print("Layer A' Verification Passed!")

if __name__ == "__main__":
    test_sim_v1_2_0_layer_a_prime()
