
from abc import ABC, abstractmethod
from pysimp.domain.entities.trace import SurgicalTrace
from typing import Optional

class TraceRepository(ABC):
    @abstractmethod
    def get_trace(self, trace_id: str) -> Optional[SurgicalTrace]:
        pass

    @abstractmethod
    def save_trace(self, trace: SurgicalTrace) -> None:
        pass
