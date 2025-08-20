from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path

class BaseDocumentHandler(ABC):
    def __init__(self, config: Dict):
        self.config = config

    @abstractmethod
    def detect_document_type(self, file_path: Path, text_sample: str) -> str:
        pass

    @abstractmethod
    def process_document(self, file_path: Path, text: str) -> Dict[str, Any]:
        pass
