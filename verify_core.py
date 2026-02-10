
import sys
import unittest
from datetime import datetime, timedelta

# Adjust path to include src if not installed, but we assume installed
# sys.path.append("src")

from pysimp.domain.entities.surgit import Surgit
from pysimp.domain.entities.trace import SurgicalTrace, SurgitEvent
from pysimp.domain.services.layer_d import LayerD
from pysimp.domain.services.layer_e import LayerE
from pysimp.application.use_cases.run_simulation import RunSimulation
from pysimp.infrastructure.persistence.in_memory_repository import InMemoryTraceRepository

class TestPysimpCore(unittest.TestCase):

    def test_tsallis_entropy_shannon_limit(self):
        """Test that q=1 converges to Shannon entropy"""
        probs = [0.5, 0.5]
        # Shannon: - (0.5 ln(0.5) + 0.5 ln(0.5)) = - ( -0.3465 + -0.3465 ) = 0.693
        entropy = LayerD.tsallis_entropy(probs, q=1.0)
        self.assertAlmostEqual(entropy, 0.693147, places=5)

    def test_tsallis_entropy_q2(self):
        """Test Tsallis with q=2 (Simpson index related)"""
        probs = [0.5, 0.5]
        # S_2 = (1 - (0.25 + 0.25)) / (2 - 1) = 0.5
        entropy = LayerD.tsallis_entropy(probs, q=2.0)
        self.assertAlmostEqual(entropy, 0.5)

    def test_shapley_value_symmetry(self):
        """Test that symmetric players get equal value"""
        elements = ["A", "B"]
        # Value function: v({}) = 0, v({A}) = 1, v({B}) = 1, v({A,B}) = 2
        # Additive game -> Shapley(A) = 1, Shapley(B) = 1
        val_func = lambda s: len(s) 
        
        shapleys = LayerE.calculate_shapley_values(elements, val_func)
        self.assertAlmostEqual(shapleys["A"], 1.0)
        self.assertAlmostEqual(shapleys["B"], 1.0)

    def test_full_simulation_flow(self):
        """Test the application layer orchestration"""
        repo = InMemoryTraceRepository()
        
        # Create a dummy trace
        events = [
            SurgitEvent(
                surgit_id="S1", 
                timestamp_start=datetime.now(), 
                timestamp_end=datetime.now() + timedelta(minutes=5)
            ),
            SurgitEvent(
                surgit_id="S2", 
                timestamp_start=datetime.now(), 
                timestamp_end=datetime.now() + timedelta(minutes=5)
            )
        ]
        trace = SurgicalTrace(procedure_id="PROC-001", patient_id="PAT-123", events=events)
        repo.save_trace(trace)
        
        use_case = RunSimulation(repo)
        result = use_case.execute("PROC-001", q=2.0)
        
        self.assertEqual(result["trace_id"], "PROC-001")
        self.assertGreater(result["global_score"], 0.0)
        print(f"\nSimulation Result: {result}")

if __name__ == '__main__':
    unittest.main()
