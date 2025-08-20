"""
InvoiceProcessorWithFallback
----------------------------
1. Essaie FastPdfInvoiceEngine.
2. Vérifie la présence des 4 champs clés.
3. Si l’un manque ➜ fallback ConfigurableInvoiceOCR.
4. Complète les champs manquants, ne touche pas aux déjà corrects.
"""

from pathlib import Path
from typing import Dict, Any

from .fast_pdf_invoice_engine import FastPdfInvoiceEngine
from .configurable_invoice_ocr import ConfigurableInvoiceOCR
from .invoice_extraction_result import InvoiceExtractionResult


class InvoiceProcessorWithFallback:
    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.fast = FastPdfInvoiceEngine(cfg)
        self.ocr = ConfigurableInvoiceOCR(cfg)

    # ------------------------------------------------------------------ #
    def process_invoice(self, pdf_path: Path) -> InvoiceExtractionResult:
        fast_res = self.fast.process_invoice(pdf_path)

        if self._all_fields_present(fast_res):
            return fast_res  # 100 % OK

        ocr_res = self.ocr.process_invoice(pdf_path)

        # complétion
        for fld in ("total_amount", "invoice_date", "invoice_number"):
            if not getattr(fast_res, fld) and getattr(ocr_res, fld):
                setattr(fast_res, fld, getattr(ocr_res, fld))

        if (
            not fast_res.legal_identifiers.get("numero_tva")
            and ocr_res.legal_identifiers.get("numero_tva")
        ):
            fast_res.legal_identifiers["numero_tva"] = ocr_res.legal_identifiers["numero_tva"]

        fast_res.processing_method = (
            "hybrid" if self._all_fields_present(fast_res) else "hybrid_partial"
        )
        return fast_res

    # ------------------------------------------------------------------ #
    @staticmethod
    def _all_fields_present(res: InvoiceExtractionResult) -> bool:
        return all(
            [
                res.total_amount,
                res.invoice_date,
                res.invoice_number,
                res.legal_identifiers.get("numero_tva"),
            ]
        )

