import os
import sys
from datetime import datetime, timedelta

# Ensure src is in python path for local execution
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from pysimp.infrastructure.persistence.in_memory_repository import InMemoryTraceRepository
from pysimp.infrastructure.persistence.yaml_loader import YamlTemplateLoader
from pysimp.infrastructure.adapters.snakes_adapter import SnakesLayerBAdapter
from pysimp.application.use_cases.run_simulation import RunSimulation
from pysimp.domain.entities.trace import SurgicalTrace, SurgitEvent
from pysimp.utils.loggers import setup_logger

def run():
    logger = setup_logger()
    logger.info("Initializing SIM-P Core (Clean Architecture)...")
    
    # 0. Load the Normative Template
    yaml_path = os.path.join(os.path.dirname(__file__), '../templates/apendicectomia.yaml')
    try:
        template = YamlTemplateLoader.load(yaml_path)
        logger.info(f"Loaded Template: {template.procedure_type} v{template.version}")
    except Exception as e:
        logger.error(f"Failed to load template: {e}")
        return

    # 1. Setup Infrastructure
    repo = InMemoryTraceRepository()
    layer_b = SnakesLayerBAdapter()
    simulation = RunSimulation(repo, layer_b_adapter=layer_b)

    # 2. Create Dummy Trace (Simulating a real surgery)
    # Let's say we did S1 -> S2 -> S3 (Valid prefix)
    trace_id = "REAL-CASE-001"
    
    events = []
    current_time = datetime.now()
    
    # Executing steps S1 to S3
    for step_id in ["S1", "S2", "S3", "S4", "S5", "S6"]:
        events.append(SurgitEvent(
            surgit_id=step_id, 
            timestamp_start=current_time, 
            timestamp_end=current_time + timedelta(minutes=5)
        ))
        current_time += timedelta(minutes=10)
        
    trace = SurgicalTrace(
        procedure_id=trace_id, 
        patient_id="PAT-REAL-123",
        events=events
    )
    repo.save_trace(trace)
    logger.info(f"Created trace: {trace_id} with {len(events)} events")

    # 3. Run Simulation
    try:
        result = simulation.execute(trace_id=trace_id, template=template, q=template.tsallis_q)
        
        logger.info("-" * 30)
        logger.info(f"Trace Validation: {result.validation_status}")
        if result.validation_status != "VALID":
            logger.info(f"Validation Msg: {result.validation_message}")
            
        logger.info(f"Saturation Delta: {result.GlobalMetrics['rho_SIM']:.4f}")
        logger.info(f"Tsallis Entropy: {result.GlobalMetrics['S_q(SIM)']:.4f}")
        logger.info(f"Global Score:     {result.GlobalMetrics['Score_SIM']:.4f}")
        logger.info("-" * 30)
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")

if __name__ == "__main__":
    run()
