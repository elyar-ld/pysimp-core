
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
from pysimp.domain.services.layer_d import LayerD

# Mock Repository
class MockTraceRepo(TraceRepository):
    def __init__(self, trace):
        self.trace = trace
    def get_trace(self, trace_id):
        return self.trace
    def save_trace(self, trace):
        pass

def test_layer_d_aggregation():
    # 1. Setup Data - 2 Steps
    # Step 1: Perfect Execution (pi = 1, delta = 0, S_q = 0)
    s1 = Surgit(id="S1", name="Perfect Step", intrinsic_deviation=0.0)
    step1 = Step(id="Step1", name="Step 1", surgits={"S1": s1})
    
    # Step 2: Risky Execution
    # delta_intr = 0.2. No noise. delta_final = 0.2.
    # pi_t = 1 - 0.2 = 0.8
    # delta_t = 0.2
    # S_q(t) (q=2) = 1 - (0.8^2 + 0.2^2) = 1 - (0.64 + 0.04) = 1 - 0.68 = 0.32
    s2 = Surgit(id="S2", name="Risky Step", intrinsic_deviation=0.2)
    step2 = Step(id="Step2", name="Step 2", surgits={"S2": s2})
    
    template = NormativeTemplate(
        procedure_type="Layer D Test", version="1.0",
        steps={"Step1": step1, "Step2": step2},
        structure_definition={},
        tsallis_q=2.0
    )
    
    # Trace
    e1 = SurgitEvent(surgit_id="S1", timestamp_start=datetime.now(), timestamp_end=datetime.now())
    e2 = SurgitEvent(surgit_id="S2", timestamp_start=datetime.now(), timestamp_end=datetime.now())
    trace = SurgicalTrace(procedure_id="Proc1", patient_id="Pat1", events=[e1, e2])
    
    # 2. Expected Calculations (q=2)
    # Step 1: S_q(1) = 0.0
    # Step 2: S_q(2) = 0.32
    # Global Entropy (q-sum): 0 (+)q 0.32 = 0 + 0.32 + (1-2)*0*0.32 = 0.32
    
    expected_entropy = 0.32
    
    # 3. Run Simulation
    repo = MockTraceRepo(trace)
    use_case = RunSimulation(repo)
    result = use_case.execute("Proc1", template=template, q=2.0)
    
    print(f"Calculated Entropy: {result['tsallis_entropy_global']}")
    print(f"Expected Entropy: {expected_entropy}")
    
    assert abs(result['tsallis_entropy_global'] - expected_entropy) < 1e-6
    print("Layer D Verification Passed!")

if __name__ == "__main__":
    test_layer_d_aggregation()
