
import sys
import unittest
from datetime import datetime
# sys.path.append("src")

from pysimp.domain.entities.surgit import Surgit
from pysimp.domain.entities.trace import SurgicalTrace, SurgitEvent
from pysimp.domain.entities.template import NormativeTemplate
from pysimp.application.use_cases.run_simulation import RunSimulation
from pysimp.infrastructure.persistence.in_memory_repository import InMemoryTraceRepository
from pysimp.infrastructure.adapters.snakes_adapter import SnakesLayerBAdapter

class TestLayerB(unittest.TestCase):
    def setUp(self):
        # Define a simple linear template: T1 -> T2
        self.surgits = {
            "T1": Surgit(id="T1", name="Incision", base_probability=0.9, complexity_weight=0.2),
            "T2": Surgit(id="T2", name="Suture", base_probability=0.8, complexity_weight=0.3)
        }
        self.structure = {
            'places': ['p_start', 'p_mid', 'p_end'],
            'transitions': [
                {'id': 'T1', 'input': 'p_start', 'output': 'p_mid'},
                {'id': 'T2', 'input': 'p_mid', 'output': 'p_end'}
            ],
            'initial_marking': 'p_start'
        }
        self.template = NormativeTemplate(
            procedure_type="TestProc", 
            version="1.0",
            surgits=self.surgits,
            structure_definition=self.structure
        )
        
        self.repo = InMemoryTraceRepository()
        self.layer_b = SnakesLayerBAdapter()
        self.simulation = RunSimulation(self.repo, self.layer_b)

    def test_valid_sequence(self):
        """Test T1 -> T2 (Valid)"""
        events = [
            SurgitEvent(surgit_id="T1", timestamp_start=datetime.now(), timestamp_end=datetime.now()),
            SurgitEvent(surgit_id="T2", timestamp_start=datetime.now(), timestamp_end=datetime.now())
        ]
        trace = SurgicalTrace(procedure_id="VALID-01", patient_id="P1", events=events)
        self.repo.save_trace(trace)
        
        result = self.simulation.execute("VALID-01", self.template)
        
        self.assertTrue(result['validation']['valid'])
        # Saturation should be 0.2 + 0.3 = 0.5 (using weights)
        self.assertAlmostEqual(result['saturation'], 0.5)

    def test_invalid_sequence(self):
        """Test T2 -> T1 (Invalid order)"""
        events = [
            SurgitEvent(surgit_id="T2", timestamp_start=datetime.now(), timestamp_end=datetime.now()), # Cannot fire T2 first (needs token in p_mid)
            SurgitEvent(surgit_id="T1", timestamp_start=datetime.now(), timestamp_end=datetime.now())
        ]
        trace = SurgicalTrace(procedure_id="INVALID-01", patient_id="P2", events=events)
        self.repo.save_trace(trace)
        
        result = self.simulation.execute("INVALID-01", self.template)
        
        self.assertFalse(result['validation']['valid'])
        print(f"\nInvalid Trace Msg: {result['validation']['message']}")

if __name__ == '__main__':
    unittest.main()
