from typing import Optional, List, Dict, Any
import re
import unicodedata
import warnings
from modules.ocr.invoice_extraction_result import InvoiceExtractionResult

warnings.filterwarnings("ignore", message=r"Cannot set gray.*color.*")


class InvoiceProcessor:
    def __init__(self, config: dict):
        self.config = config

    # ───────────────────────── OUTILS ─────────────────────────
    @staticmethod
    def _safe_to_float(raw: str) -> Optional[float]:
        """Convertit « 1 234,56 € » → 1234.56 (gère tous les espaces Unicode)."""
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

    @staticmethod
    def _normalize_vat(vat: str) -> str:
        """Retourne le numéro TVA en majuscules, sans espaces ni tabulations."""
        return re.sub(r'\s+', '', vat.upper()) if vat else vat

    # ─────────────  CHOIX DU TOTAL TTC  ─────────────
    def _choose_total_amount(self, amounts_raw: List[str], full_text: str) -> Optional[float]:
        total_lbl = re.compile(
            r'(total[^0-9\na-z]{0,20}(?:t\s*\.?\s*t\s*\.?\s*c\s*\.?|ttc\.?))'
            r'|total\s+[aà]\s+payer|montant\s+[aà]\s+payer|net\s+[aà]\s+payer',
            re.IGNORECASE
        )

        lines = full_text.splitlines()
        for idx, line in enumerate(lines):
            if total_lbl.search(line):
                window = ' '.join(lines[idx:idx + 4])  # ligne + 3 suivantes
                amounts = re.findall(
                    r'([0-9]{1,3}(?:[\u202F\u00A0 ]?[0-9]{3})*[.,][0-9]{2})',
                    window
                )
                floats = [self._safe_to_float(a) for a in amounts if a]
                floats = [f for f in floats if f and f > 1]
                if floats:
                    return max(floats)  # plus grand = TTC
        # Fallback
        vals = [self._safe_to_float(a) for a in amounts_raw]
        vals = [v for v in vals if v and v > 1]
        return min(vals) if vals else None

    # ───────────  FALLBACK NUMÉRO FACTURE ───────────
    def _fallback_invoice_number(self, full_text: str) -> Optional[str]:
        txt = unicodedata.normalize("NFKC", full_text).replace("\u00A0", " ").replace("\u202F", " ")

        patterns = [
            r'\bfacture\s*[:#-]?\s*([0-9]{5,})\b',
            r'\bfacture[^\n]{0,60}?N[°ºo]\s*[:\-]?\s*([0-9]{5,})\b',
            r'\bN[°ºo]\s*[:\-]?\s*([0-9]{5,})\b',
            r'Invoice\s+No\.?\s*:\s*([A-Z0-9_\-]+)',
            r'Invoice\s+#\s*:\s*([A-Z0-9_\-]+)',
            r'Num[eé]ro\s+de\s+la\s+facture\s*:?\s*([A-Z0-9_\-]{6,})',
            r'Vos\s+références\s*:?\s*([A-Z0-9_\- ]{8,})',
            r'^[^\n]*[№N°]\s*([0-9]{6,})$',
        ]
        for line in txt.splitlines():
            s = line.strip()
            for pat in patterns:
                m = re.search(pat, s, re.IGNORECASE)
                if m:
                    return m.group(1).strip()

        # Ligne composée uniquement de 5–10 chiffres
        for line in txt.splitlines():
            if re.fullmatch(r'\s*[0-9]{5,10}\s*', line):
                return line.strip()
        return None

    # ─────────────  STRUCTURATION  ─────────────
    def structure_results(self, extracted: Dict[str, Any], full_text: str) -> InvoiceExtractionResult:
        res = InvoiceExtractionResult()

        # Montants
        res.amounts_found = extracted.get("currency_amounts", [])
        res.total_amount  = self._choose_total_amount(res.amounts_found, full_text)

        # Dates
        dates = extracted.get("dates", [])
        res.invoice_date = dates[0] if dates else None

        # Numéro de facture
        raw_nums = [n.strip() for n in extracted.get("invoice_numbers", []) if n and n.strip()]
        res.invoice_number = raw_nums[0] if raw_nums else self._fallback_invoice_number(full_text)

        # TVA – normalisation sans espaces
        vats_raw = extracted.get("vat_numbers", [])
        vats_norm = [self._normalize_vat(v) for v in vats_raw if v]
        res.legal_identifiers = {"numero_tva": vats_norm[0] if vats_norm else None}

        # Confiance
        conf = 0.4 if res.total_amount else 0
        conf += 0.2 if res.invoice_date else 0
        conf += 0.2 if res.invoice_number else 0
        conf += 0.2 if res.legal_identifiers["numero_tva"] else 0
        res.extraction_confidence = round(min(conf, 1.0), 2)

        # Entités extraites
        res.extracted_entities = {
            "total_amount": res.total_amount,
            "invoice_date": res.invoice_date,
            "invoice_number": res.invoice_number,
            "numero_tva": res.legal_identifiers["numero_tva"],
            "currency_amounts": res.amounts_found,
            "dates": dates,
            "vat_numbers": vats_norm,
        }
        return res
