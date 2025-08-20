from typing import Optional, List, Dict, Any
import re
import unicodedata
import warnings
from modules.ocr.invoice_extraction_result import InvoiceExtractionResult

# Masque les warnings « Cannot set gray … » produits par reportlab/PyPDF
warnings.filterwarnings("ignore", message=r"Cannot set gray.*color.*")


class InvoiceProcessor:
    def __init__(self, config: dict):
        self.config = config

    # ───────────────────────── OUTILS ─────────────────────────
    @staticmethod
    def _safe_to_float(raw: str) -> Optional[float]:
        """« 1 234,56 € » → 1234.56  (tous espaces Unicode gérés)."""
        if not raw:
            return None
        num = ''.join(
            c for c in unicodedata.normalize("NFKD", raw)
            if c.isdigit() or c in {',', '.'}
        ).replace(',', '.')
        try:
            return float(num)
        except ValueError:
            return None

    # ─────────────  CHOIX DU TOTAL TTC  ─────────────
    def _choose_total_amount(self, amounts_raw: List[str], full_text: str) -> Optional[float]:
        total_lbl = re.compile(
            r'(total[^0-9\na-z]{0,20}t\s*\.?\s*t\s*\.?\s*c\s*\.?'   # TOTAL T.T.C / T T C / TTC
            r'|total[^0-9\na-z]{0,20}ttc\.?'                        # TOTALTTC collé
            r'|total\s+[aà]\s+payer'                                # Total à payer
            r'|montant\s+[aà]\s+payer'                              # Montant à payer
            r'|net\s+[aà]\s+payer)',                                # Net à payer
            re.IGNORECASE
        )

        lines = full_text.splitlines()
        for idx, line in enumerate(lines):
            if total_lbl.search(line):
                # Cherche un montant € dans la même ligne
                block = ' '.join(lines[idx:idx + 2])  # ← 2 lignes pour MCA
                m = re.search(
                    r'([0-9]{1,3}(?:[\u202F\u00A0 ]?[0-9]{3})*[.,][0-9]{2})',
                    block
                )
                if m:
                    val = self._safe_to_float(m.group(1))
                    if val and val > 0:
                        return val

        # Fallback : plus petit montant >1 €
        if amounts_raw:
            vals = [self._safe_to_float(a) for a in amounts_raw]
            vals = [v for v in vals if v and v > 1]
            return min(vals) if vals else None
        return None

    # ───────────  FALLBACK NUMÉRO FACTURE ───────────
    def _fallback_invoice_number(self, full_text: str) -> Optional[str]:
        # Normalisation : insécables/fine-space → espace
        txt = unicodedata.normalize("NFKC", full_text).replace("\u00A0", " ").replace("\u202F", " ")

        patterns = [
            r'\bfacture[^\n]{0,60}?N[°ºo]\s*[:\-]?\s*([0-9]{5,})\b',   # FACTURE N° : 1042160
            r'\bN[°ºo]\s*[:\-]?\s*([0-9]{5,})\b',                      # N° 1042160
            r'Invoice\s+No\.?\s*:\s*([A-Z0-9_\-]+)',                   # Ubiquiti
            r'Invoice\s+#\s*:\s*([A-Z0-9_\-]+)',                       # Ubiquiti var
            r'Num[eé]ro\s+de\s+la\s+facture\s*:?\s*([A-Z0-9_\-]{6,})', # Bosch
            r'Vos\s+références\s*:?\s*([A-Z0-9_\- ]{8,})',             # MCA
            r'^[^\n]*[№N°]\s*([0-9]{6,})$',                            # Godaddy
        ]
        for line in txt.splitlines():
            s = line.strip()
            for pat in patterns:
                m = re.search(pat, s, re.IGNORECASE)
                if m:
                    return m.group(1).strip()

        # Dernier filet : ligne ne contenant QUE 5-10 chiffres (éventuel point final)
        for line in txt.splitlines():
            if re.fullmatch(r'\s*[0-9]{5,10}\.?\s*', line):
                return re.sub(r'\D', '', line)
        return None

    # ─────────────  STRUCTURATION  ─────────────
    def structure_results(self, extracted: Dict[str, Any], full_text: str) -> InvoiceExtractionResult:
        res = InvoiceExtractionResult()

        # Montants
        res.amounts_found = extracted.get("currency_amounts", [])
        res.total_amount = self._choose_total_amount(res.amounts_found, full_text)

        # Dates
        dates = extracted.get("dates", [])
        res.invoice_date = dates[0] if dates else None

        # Numéro de facture
        raw_nums = [n.strip() for n in extracted.get("invoice_numbers", []) if n and n.strip()]
        res.invoice_number = raw_nums[0] if raw_nums else self._fallback_invoice_number(full_text)

        # TVA
        vats = extracted.get("vat_numbers", [])
        res.legal_identifiers = {"numero_tva": vats[0] if vats else None}

        # Confiance
        conf = 0.4 if res.total_amount else 0
        conf += 0.2 if res.invoice_date else 0
        conf += 0.2 if res.invoice_number else 0
        conf += 0.2 if res.legal_identifiers["numero_tva"] else 0
        res.extraction_confidence = round(min(conf, 1.0), 2)

        # Entités complètes
        res.extracted_entities = {
            "total_amount": res.total_amount,
            "invoice_date": res.invoice_date,
            "invoice_number": res.invoice_number,
            "numero_tva": res.legal_identifiers["numero_tva"],
            "currency_amounts": res.amounts_found,
            "dates": dates,
            "vat_numbers": vats,
        }
        return res