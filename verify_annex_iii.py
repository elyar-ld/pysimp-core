
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
from pysimp.infrastructure.adapters.snakes_adapter import SnakesLayerBAdapter
from pysimp.domain.services.layer_c import LayerC

# Mock Repository
class MockTraceRepo(TraceRepository):
    def __init__(self, trace):
        self.trace = trace
    def get_trace(self, trace_id):
        return self.trace
    def save_trace(self, trace):
        pass

def test_annex_iii_reporting():
    print("Testing Annex III Reporting and Shapley Decomposition...")
    
    # 1. Setup - Template with Intrinsic Deviation
    # S1: Intrinsic 0.1.
    s1 = Surgit(id="S1", name="Step 1", intrinsic_deviation=0.1)
    step1 = Step(id="Step1", name="Step 1", surgits={"S1": s1}, weight_wt=1.0)
    
    # Structure valid
    structure_def = {
        'places': ['start', 'end'], 
        'transitions': [{'id': 'S1', 'input': 'start', 'output': 'end'}],
        'initial_marking': ['start']
    }
    
    template = NormativeTemplate(
        procedure_type="DecompTest", version="1.0",
        steps={"Step1": step1},
        structure_definition=structure_def,
        tsallis_q=1.0, # Boltzmann-Gibbs for simplicity
        weight_alpha=1.0, 
        weight_beta=1.0,
        dynamics_definition={'provenance_decay': 1.0}
    )
    
    # 2. Trace with Patient Noise (n_t = 1.2)
    # Event 1: S1. Noise Patient = 1.2. External = 1.0.
    # Logic:
    # Ideal (n=1, e=1): Delta = Intr(0.1) * 1 * 1 = 0.1.
    # Actual (n=1.2, e=1): Delta = 0.1 * 1.2 * 1 = 0.12.
    # Deviation Effect: 0.12 - 0.1 = 0.02 increase in deviation.
    # Entropy/Score will increase accordingly.
    # Phi_Patient should be positive.
    
    e1 = SurgitEvent(surgit_id="S1", timestamp_start=datetime.now(), timestamp_end=datetime.now(), n_t=1.2)
    trace = SurgicalTrace(procedure_id="Dec1", patient_id="Pat1", events=[e1])
    
    # Mock Repo & Adapter
    repo = MockTraceRepo(trace)
    # Dummy valid adapter
    class DummyValidB:
        def validate_structure(self, e, t): return True
        
    use_case = RunSimulation(repo, layer_b_adapter=DummyValidB())
    
    # 3. Execute
    report = use_case.execute("Dec1", template=template)
    
    # 4. Verify Output Structure
    print(f"Global Score: {report.GlobalMetrics['Score_SIM']}")
    print(f"Ideal Score: {report.ShapleyDecomposition.score_ideal}")
    print(f"Phi Patient: {report.ShapleyDecomposition.phi_patient}")
    print(f"Phi External: {report.ShapleyDecomposition.phi_external}")
    
    # Assertions
    # Ideal Score > 0 (intrinsic entropy)
    assert report.ShapleyDecomposition.score_ideal > 0
    # Actual > Ideal
    assert report.GlobalMetrics['Score_SIM'] > report.ShapleyDecomposition.score_ideal
    # Phi Patient > 0 (since n_t = 1.2)
    assert report.ShapleyDecomposition.phi_patient > 0
    # Phi External ~ 0 (since e_t = 1.0)
    assert abs(report.ShapleyDecomposition.phi_external) < 1e-6
    
    # Verify Table Presence
    assert len(report.StepTable) == 1
    assert len(report.NoiseTable) == 1
    assert len(report.Traceability) == 1
    
    print("Annex III Reporting Verified!")

if __name__ == "__main__":
    test_annex_iii_reporting()
