
from typing import Dict, Optional
from pysimp.application.interfaces.repository import TraceRepository
from pysimp.domain.entities.trace import SurgicalTrace

class InMemoryTraceRepository(TraceRepository):
    def __init__(self):
        self._traces: Dict[str, SurgicalTrace] = {}

    def get_trace(self, trace_id: str) -> Optional[SurgicalTrace]:
        return self._traces.get(trace_id)

    def save_trace(self, trace: SurgicalTrace) -> None:
        self._traces[trace.procedure_id] = trace
