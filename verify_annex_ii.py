
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pysimp.domain.entities.trace import (
    SurgicalTrace, SurgitEvent, SurgitType, DeviationCause, PostoperativeOutcome
)

def test_annex_ii_data_acquisition():
    print("Testing Annex II Data Acquisition Template...")
    
    # 1. Test Outcome Recording (A.II.1b)
    outcome = PostoperativeOutcome(
        complication_type="SS1 (Surgical Site Infection)", 
        time_window="30-day", 
        severity_grade="Clavien-Dindo I"
    )
    
    # 2. Test Enhanced Surgit Event (A.II.1, A.II.4, A.II.5)
    event_ce = SurgitEvent(
        surgit_id="CE_001",
        timestamp_start=datetime.now(),
        timestamp_end=datetime.now(),
        surgit_type=SurgitType.CE_SUBSTITUTION, # A.II.4
        deviation_cause=DeviationCause.EXTERNAL,  # A.II.5 (strict enum)
        risk_tags=["high_tension", "ischemia_risk"], # A.II.1.6
        n_t=1.2, # A.II.3
        e_t=1.5
    )
    
    # 3. Test Trace Assembly
    trace = SurgicalTrace(
        procedure_id="AnnexII_Test", 
        patient_id="Pat_002",
        events=[event_ce],
        outcomes=[outcome]
    )
    
    print("\nVerified Data Structure:")
    print(f"Outcome Recorded: {trace.outcomes[0].complication_type}")
    print(f"Event Type: {trace.events[0].surgit_type}")
    print(f"Deviation Cause: {trace.events[0].deviation_cause}")
    print(f"Risk Tags: {trace.events[0].risk_tags}")
    
    assert trace.outcomes[0].time_window == "30-day"
    assert trace.events[0].surgit_type == SurgitType.CE_SUBSTITUTION
    
    print("\nAnnex II Verification Passed!")

if __name__ == "__main__":
    test_annex_ii_data_acquisition()
