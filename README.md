# SIM-P Core (Surgical Iatromathic Model Procedure)

**SIM-P Core** is the foundational Python library for the **Surgical Iatromathic Model Procedure**, a mathematical framework designed to model, analyze, and validat surgical procedures using advanced probability theory, topology, and entropy metrics.

---

## 🏥 For Medical Professionals & Stakeholders

**What is SIM-P?**
SIM-P translates the complex reality of surgery into a rigorous mathematical language. It allows us to:
-   **Standardize Procedures**: Define "Normative Templates" for surgeries (the "ideal" way).
-   **Measure Complexity**: Use **Entropy** (Tsallis) to quantify how "disordered" or complex a surgery was.
-   **Attribute Risk**: Understand exactly which steps contributed to a complication using **Game Theory** (Shapley Values).
-   **Validate Safety**: Ensure no mandatory safety steps were skipped.

**Key Components:**
1.  **Layer A (Axiomatics)**: The fundamental rules and probability of each step.
2.  **Layer B (Topology)**: The "map" of the surgery – what steps can follow what.
3.  **Layer C (Dynamics)**: How the surgery evolves over time (fatigue, instrument wear).
4.  **Layer D (Scoring)**: Global scores for complexity and risk.
5.  **Layer E (Outcomes)**: Predicting real-world patient outcomes from the model.

---

## 💻 For Developers

**SIM-P Core** is built using **Clean Architecture** principles to ensure robustness, testability, and separation of concerns.

### Architecture Overview

The project is structured into three concentric layers:

1.  **Domain Layer** (`src/pysimp/domain`)
    *   **Entities**: Core business objects like `Surgit` (a surgical unit of action) and `Trace` (a record of a surgery).
    *   **Services**: Pure mathematical logic for Layers A-E (e.g., Tsallis Entropy calculation, probability saturation).
    *   *No external dependencies (except `pydantic` for strict data modeling).*

2.  **Application Layer** (`src/pysimp/application`)
    *   **Use Cases**: Orchestrators that execute specific workflows, like `RunSimulation`.
    *   **Interfaces**: Abstract definitions for repositories and adapters.

3.  **Infrastructure Layer** (`src/pysimp/infrastructure`)
    *   **Persistence**: Implementations of repositories (e.g., `InMemoryTraceRepository`).
    *   **Adapters**: Tools to connect to external libraries (like `snakes` for Petri Nets or `networkx`).

### Installation

Requires Python 3.10+

```bash
# Clone the repository
git clone https://github.com/your-org/pysimp-core.git
cd pysimp-core

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### Running Verification

To verify the core mathematical models are working correctly, run the verification script:

```bash
python verify_core.py
```

### Example Usage

```python
from pysimp.domain.entities.trace import SurgicalTrace, SurgitEvent
from pysimp.application.use_cases.run_simulation import RunSimulation
from pysimp.infrastructure.persistence.in_memory_repository import InMemoryTraceRepository

# 1. Setup Repo and Use Case
# 1. Setup Repo and Use Case (with Petri Net validation)
from pysimp.infrastructure.adapters.snakes_adapter import SnakesLayerBAdapter
repo = InMemoryTraceRepository()
layer_b = SnakesLayerBAdapter()
simulation = RunSimulation(repo, layer_b_adapter=layer_b)

# 2. Define Normative Template (Layer B Structure)
from pysimp.domain.entities.template import NormativeTemplate
from pysimp.domain.entities.surgit import Surgit

template = NormativeTemplate(
    procedure_type="Appendectomy",
    version="1.0",
    surgits={
        "S1": Surgit(id="S1", name="Incision", base_probability=0.9, complexity_weight=0.2),
        "S2": Surgit(id="S2", name="Dissection", base_probability=0.8, complexity_weight=0.3)
    },
    structure_definition={
        'places': ['p_start', 'p_mid', 'p_end'],
        'transitions': [
            {'id': 'S1', 'input': 'p_start', 'output': 'p_mid'},
            {'id': 'S2', 'input': 'p_mid', 'output': 'p_end'}
        ],
        'initial_marking': 'p_start'
    }
)

# 3. Create a Real Trace
trace = SurgicalTrace(procedure_id="PROC-001", patient_id="PAT-ABC")
# (Populate trace.events with SurgitEvent...)
repo.save_trace(trace)

# 4. Run Simulation with Template
result = simulation.execute(trace_id="PROC-001", template=template, q=2.0)
print(f"Valid: {result['validation']['valid']}")
print(f"Global Score: {result['global_score']}")
```

---

**Status**: Alpha Development (v0.1.0)
**License**: Proprietary (Private Source). All rights reserved. No part of this code may be used, distributed, or modified without explicit permission from the creators.
