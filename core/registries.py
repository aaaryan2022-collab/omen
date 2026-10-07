# OMEN UPGRADE — Real registry interfaces (spec §21); mock only where external dep missing.
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ModelRegistry(ABC):
    @abstractmethod
    def list_models(self) -> List[str]: ...
    @abstractmethod
    def select(self, task: str) -> str: ...

class AgentRegistry(ABC):
    @abstractmethod
    def list_agents(self) -> List[str]: ...

class ToolRegistry(ABC):
    @abstractmethod
    def list_tools(self) -> List[str]: ...

class MemoryRegistry(ABC):
    @abstractmethod
    def search(self, q: str) -> List[Dict]: ...

class EventBus(ABC):
    @abstractmethod
    def emit(self, event: str, payload: Dict) -> None: ...

class TaskManager(ABC):
    @abstractmethod
    def list_active(self) -> List[Dict]: ...

class TraceManager(ABC):
    @abstractmethod
    def record(self, step: str, data: Dict) -> None: ...
