
import sys
import os
from datetime import datetime
import pytest

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pysimp.domain.entities.surgit import Surgit
from pysimp.domain.entities.step import Step
from pysimp.domain.entities.template import NormativeTemplate
from pysimp.domain.entities.trace import SurgicalTrace, SurgitEvent
from pysimp.infrastructure.adapters.snakes_adapter import SnakesLayerBAdapter


def test_layer_b_structure():
    # 1. Define a Simple Sequential Petri Net
    # p_start -> [S1] -> p_mid -> [S2] -> p_end
    structure_def = {
        'places': ['p_start', 'p_mid', 'p_end'],
        'transitions': [
            {'id': 'S1', 'input': 'p_start', 'output': 'p_mid'},
            {'id': 'S2', 'input': 'p_mid', 'output': 'p_end'}
        ],
        'initial_marking': ['p_start']
    }
    
    # 2. Define Template with Mandatory S1 and S2
    s1 = Surgit(id="S1", name="Step 1", is_mandatory=True)
    s2 = Surgit(id="S2", name="Step 2", is_mandatory=True)
    step = Step(id="Step1", name="Step 1", surgits={"S1": s1, "S2": s2})
    
    template = NormativeTemplate(
        procedure_type="PN Test", version="1.0",
        steps={"Step1": step},
        structure_definition=structure_def,
        forbidden_states=[]
    )
    
    adapter = SnakesLayerBAdapter()
    
    # CASE 1: Valid Sequence (S1 -> S2)
    trace_valid = [
        SurgitEvent(surgit_id="S1", timestamp_start=datetime.now(), timestamp_end=datetime.now()),
        SurgitEvent(surgit_id="S2", timestamp_start=datetime.now(), timestamp_end=datetime.now())
    ]
    print("Testing Valid Trace...")
    assert adapter.validate_structure(trace_valid, template) == True
    print("Passed Valid Trace.")
    
    # CASE 2: Invalid Sequence (S2 -> S1) - S2 not enabled at start
    trace_invalid_seq = [
        SurgitEvent(surgit_id="S2", timestamp_start=datetime.now(), timestamp_end=datetime.now()),
        SurgitEvent(surgit_id="S1", timestamp_start=datetime.now(), timestamp_end=datetime.now())
    ]
    print("Testing Invalid Sequence...")
    assert adapter.validate_structure(trace_invalid_seq, template) == False
    print("Passed Invalid Sequence Check.")
    
    # CASE 3: Missed Mandatory Step (Only S1)
    trace_incomplete = [
        SurgitEvent(surgit_id="S1", timestamp_start=datetime.now(), timestamp_end=datetime.now())
    ]
    print("Testing Incomplete/Mandatory Check...")
    # Should fail because S2 is mandatory but not in trace
    assert adapter.validate_structure(trace_incomplete, template) == False
    print("Passed Mandatory Check.")

    print("Layer B Verification Completel!")

if __name__ == "__main__":
    test_layer_b_structure()
