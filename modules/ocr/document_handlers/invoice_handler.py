"""
Handler factures – pointe vers InvoiceProcessorWithFallback.
"""

from pathlib import Path
from typing import Dict, Any

from .base_handler import BaseDocumentHandler, DocumentTypeConfig
from ..fallback_wrapper import InvoiceProcessorWithFallback


class InvoiceHandler(BaseDocumentHandler):
    def _get_document_config(self) -> DocumentTypeConfig:
        return DocumentTypeConfig(
            name="invoice",
            priority=1,
            file_patterns=["facture", "invoice", "rechnung", "fattura"],
            content_indicators=[r"\bfacture\b", r"\binvoice\b"],
            required_confidence=0.6,
        )

    def _load_patterns(self) -> Dict[str, Any]:
        return {}

    def _initialize_processor(self):
        return InvoiceProcessorWithFallback(self.config)

    # ------------------------------------------------------------ #
    def process(self, file_path: Path, _raw_text: str) -> Dict[str, Any]:
        res = self.processor.process_invoice(file_path)
        res.extracted_entities["document_type"] = "invoice"
        return res
