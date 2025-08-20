# modules/ocr/configurable_invoice_ocr.py
import re
import unicodedata
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from .base_ocr import BaseOCR
from .invoice_extraction_result import InvoiceExtractionResult

logger = logging.getLogger(__name__)

class ConfigurableInvoiceOCR(BaseOCR):
    """Module OCR configurable pour factures avec sélection intelligente du montant TTC."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.patterns = self._load_patterns()
        logger.info("🔧 Module OCR Configurable Finalisé Initialisé.")
        logger.info("   - Patterns chargés: %d catégories", len(self.patterns))

    def _load_patterns(self) -> Dict[str, Any]:
        """Charge les patterns d'extraction."""
        return {
            "currency_amounts": r'([0-9]{1,3}(?:[\u202F\u00A0 ,]?[0-9]{3})*[.,][0-9]{2})',
            "french_dates": r'(\d{1,2}(?:\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}|\s*/\s*\d{1,2}\s*/\s*\d{4}))',
            "invoice_numbers": r'(?:facture|invoice|référence|ref\.?|n°)\s*[:\-]?\s*([A-Z0-9_\-\s]+)',
            "vat_numbers": r'\b((?:FR|DE|IT|ES|BE|NL)[0-9A-Z\s]{8,15})\b'
        }

    def process_invoice(self, file_path: Path) -> InvoiceExtractionResult:
        """Point d'entrée principal pour traiter une facture."""
        logger.info("--- Début du traitement pour : %s ---", file_path.name)
        
        # 1. Extraction OCR
        raw_text, confidence = self.extract_text(file_path)
        
        # 2. Extraction par regex
        extracted_data = self._extract_data_with_patterns(raw_text)
        logger.info("Données brutes extraites par regex: %s", extracted_data)
        
        # 3. Sélection intelligente du montant TTC
        total_amount = self._select_total_amount(raw_text, extracted_data["currency_amounts"])
        
        # 4. Construction du résultat
        result = InvoiceExtractionResult()
        result.total_amount = total_amount
        result.invoice_date = extracted_data["french_dates"][0] if extracted_data["french_dates"] else None
        result.invoice_number = extracted_data["invoice_numbers"][-1] if extracted_data["invoice_numbers"] else None
        result.legal_identifiers = {
            "numero_tva": self._normalize_vat(extracted_data["vat_numbers"][0]) if extracted_data["vat_numbers"] else None
        }
        result.amounts_found = extracted_data["currency_amounts"]
        result.extraction_confidence = min(confidence + 0.15, 1.0)
        
        # Entités extraites pour debug
        result.extracted_entities = {
            "total_amount": result.total_amount,
            "invoice_date": result.invoice_date,
            "invoice_number": result.invoice_number,
            "numero_tva": result.legal_identifiers["numero_tva"],
            "currency_amounts": result.amounts_found
        }
        
        logger.info("Résultat final de l'extraction: %s", {
            "total_amount": result.total_amount,
            "subtotal_ht": None,
            "vat_amount": None,
            "invoice_date": result.invoice_date,
            "invoice_number": result.invoice_number,
            "vat_number": result.legal_identifiers["numero_tva"]
        })
        logger.info("--- Extraction terminée avec une confiance de %.2f ---", result.extraction_confidence)
        
        return result

    def _extract_data_with_patterns(self, text: str) -> Dict[str, list]:
        """Applique tous les patterns regex sur le texte."""
        results = {}
        for key, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            results[key] = matches
        return results

    def _select_total_amount(self, raw_text: str, amounts_raw: list[str]) -> Optional[float]:
        """
        Sélection intelligente du montant TTC :
        1. Cherche les labels 'Total TTC', 'Montant à payer', etc.
        2. Prend le PLUS GRAND montant dans la zone (TTC > HT)
        3. Fallback : plus grand montant global (car TTC habituellement max)
        """
        # Patterns de labels TTC améliorés
        ttc_labels = re.compile(
            r'(?:total|montant|net).*?(?:ttc|t\.t\.c\.|à\s+payer|due?|payable)' +
            r'|(?:ttc|t\.t\.c\.).*?(?:total|montant)' +
            r'|grand\s+total' +
            r'|total\s+général',
            re.IGNORECASE | re.DOTALL
        )
        
        amount_pattern = re.compile(r'([0-9]{1,3}(?:[\u202F\u00A0 ,]?[0-9]{3})*[.,][0-9]{2})')
        
        lines = raw_text.splitlines()
        
        # Recherche dans chaque ligne + fenêtre de 4 lignes suivantes
        for i, line in enumerate(lines):
            if ttc_labels.search(line):
                # Fenêtre : ligne courante + 4 suivantes
                window = ' '.join(lines[i:i + 5])
                candidates = amount_pattern.findall(window)
                
                if candidates:
                    floats = [self._to_float(a) for a in candidates if self._to_float(a) and self._to_float(a) > 1]
                    if floats:
                        selected = max(floats)  # Le plus grand = TTC
                        logger.info("💰 Label TTC trouvé, montant sélectionné: %.2f€", selected)
                        return selected

        # Fallback : plus grand montant global (TTC généralement max)
        all_floats = [self._to_float(a) for a in amounts_raw if self._to_float(a) and self._to_float(a) > 1]
        if all_floats:
            fallback = max(all_floats)  # Changé de min() à max()
            logger.info("🔄 Fallback activé, plus grand montant: %.2f€", fallback)
            return fallback
        
        return None

    @staticmethod
    def _to_float(raw: str) -> Optional[float]:
        """Convertit string montant en float (gère virgules, espaces insécables)."""
        if not raw:
            return None
        normalized = ''.join(
            c for c in unicodedata.normalize('NFKD', raw)
            if c.isdigit() or c in {',', '.'}
        ).replace(',', '.')
        try:
            return float(normalized)
        except ValueError:
            return None

    @staticmethod
    def _normalize_vat(vat: str) -> str:
        """Normalise numéro TVA : majuscules, pas d'espaces."""
        return re.sub(r'\s+', '', vat.upper()) if vat else vat
