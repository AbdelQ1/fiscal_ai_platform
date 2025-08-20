# modules/ocr/fast_pdf_invoice_engine.py
"""
FastPdfInvoiceEngine v14 - FINAL avec prix HT
---------------------------------------------
Extraction 100% texte PDF avec normalisation des dates + taux TVA + montant HT.
• Montant TTC   : plus grand montant détecté
• Montant HT    : extraction directe ou calcul depuis TTC/taux
• Date facture  : normalisée JJ/MM/AAAA (français/anglais)
• Numéro facture: labels explicites + "Vos références" + nettoyage préfixes
• TVA européenne: FR, NL, DE, IT, ES, BE (validation stricte)
• Taux de TVA   : extraction explicite ou déduction automatique par pays
"""

from __future__ import annotations

from pathlib import Path
import re
import unicodedata
from typing import Dict, Any, Optional, List

import fitz  # PyMuPDF

from .invoice_extraction_result import InvoiceExtractionResult


class FastPdfInvoiceEngine:
    """Extraction rapide et robuste pour factures PDF avec montant HT."""

    # ---------- MONTANTS ---------- #
    _RE_AMOUNT = re.compile(
        r"([0-9]{1,3}(?:[\u202F\u00A0 ,.]?[0-9]{3})*[.,][0-9]{2})"
    )

    # -------- MONTANTS HT ------------ #
    _RE_AMOUNT_HT = re.compile(
        r"(?:total\s+ht|montant\s+ht|sous[- ]total|subtotal|net\s+amount)\s*:?\s*([0-9]{1,3}(?:[\u202F\u00A0 ,.]?[0-9]{3})*[.,][0-9]{2})",
        re.IGNORECASE,
    )

    _RE_AMOUNT_HT_TABLE = re.compile(
        r"(?:ht|excl\.?\s+(?:tax|vat|tva))\s*:?\s*([0-9]{1,3}(?:[\u202F\u00A0 ,.]?[0-9]{3})*[.,][0-9]{2})",
        re.IGNORECASE,
    )

    # ----------- DATES ------------ #
    _RE_DATE = re.compile(
        r"(\d{4}[./-]\d{1,2}[./-]\d{1,2}"                  # 2024/12/24
        r"|\d{1,2}[./-]\d{1,2}[./-]\d{4}"                   # 24/12/2024
        r"|\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|"
        r"septembre|octobre|novembre|décembre|january|february|march|april|"
        r"may|june|july|august|september|october|november|december)\s+\d{4})",
        re.IGNORECASE,
    )

    # -------- NUMÉRO FACTURE ------ #
    _RE_INVOICE_LBL = re.compile(
        r"(?:invoice(?:\s*(?:no\.?|number))?|receipt|facture)"
        r"[^\w]{0,10}([A-Z0-9_\-/]{5,40})",
        re.IGNORECASE,
    )
    _RE_GENERIC_NUM = re.compile(
        r"\b(?:EU\d{7}|FR\d{2}[A-Z0-9]{8}|MCA\d{9}_[A-Z0-9_]{3,}|[A-Z]{2,}\d{4,}|"
        r"\d{7,})\b"
    )

    # ---------- TVA UE ------------ #
    _RE_VAT_ANY = re.compile(
        r"\b([A-Z]{2}(?:\s*[0-9A-Z]){8,13})\b"
    )
    _RE_VAT_VALID = re.compile(
        r"^(?:"
        r"FR(?=[A-Z0-9]{11}$)(?=[A-Z0-9]*\d)[A-Z0-9]{11}"
        r"|NL[A-Z0-9]{9}B[0-9]{2}"
        r"|DE[0-9]{9}"
        r"|IT[0-9]{11}"
        r"|ES[A-Z0-9]{9}"
        r"|BE[0-9]{10}"
        r")$"
    )

    # -------- TAUX TVA ------------ #
    _RE_VAT_RATE = re.compile(
        r"(?:tva|vat|tax)\s*(?:à|at|@|:)?\s*([0-9]{1,2}(?:[,.][0-9]{1,2})?)\s*%",
        re.IGNORECASE,
    )

    # Patterns spécifiques pour les taux français
    _RE_VAT_RATE_FR = re.compile(
        r"(?:TVA\s+)?([0-9]{1,2}(?:[,.][0-9]{1,2})?)\s*%",
        re.IGNORECASE,
    )

    # Patterns dans les tableaux de facture
    _RE_VAT_RATE_TABLE = re.compile(
        r"(?:taux|rate)\s*:?\s*([0-9]{1,2}(?:[,.][0-9]{1,2})?)\s*%",
        re.IGNORECASE,
    )

    # ================================================================= #
    #                     POINT D'ENTRÉE PRINCIPAL                      #
    # ================================================================= #
    def __init__(self, _config: Dict[str, Any]) -> None:
        """Aucune configuration requise pour l'extraction PDF."""
        pass

    def process_invoice(self, pdf_path: Path) -> InvoiceExtractionResult:
        """Traite une facture PDF et retourne les données structurées."""
        text = self._extract_text(pdf_path)
        lines = text.splitlines()

        result = InvoiceExtractionResult()
        result.processing_method = "fast_pdf"

        # -------- Total TTC -------- #
        amounts = [self._to_float(m) for m in self._RE_AMOUNT.findall(text)]
        amounts = [a for a in amounts if a and a > 0]
        result.total_amount = max(amounts) if amounts else None
        result.amounts_found = [f"{a:.2f}" for a in amounts]

        # -------- Date facture -------- #
        result.invoice_date = self._extract_best_date(text)

        # -------- Numéro facture -------- #
        result.invoice_number = self._extract_invoice_number(text, lines)

        # -------- TVA européenne -------- #
        vat = self._extract_vat_number(text)
        result.legal_identifiers = {"numero_tva": vat} if vat else {}

        # -------- Taux de TVA -------- #
        vat_rate = self._extract_vat_rate(text)
        if vat_rate is not None:
            result.vat_rate = vat_rate

        # -------- NOUVEAU : Montant HT -------- #
        # Stockage temporaire pour calculs croisés
        self._current_total_amount = result.total_amount
        self._current_vat_rate = vat_rate
        
        amount_ht = self._extract_amount_ht(text)
        if amount_ht is not None:
            result.amount_ht = amount_ht

        # -------- Confiance -------- #
        result.extraction_confidence = self._calculate_confidence(result)
        
        return result

    # ================================================================= #
    #                     MÉTHODES D'EXTRACTION                         #
    # ================================================================= #
    
    def _extract_best_date(self, text: str) -> Optional[str]:
        """Extrait la meilleure date et la normalise au format JJ/MM/AAAA."""
        dates = self._RE_DATE.findall(text)
        if not dates:
            return None
        
        # Privilégier les dates avec année 4 chiffres au début (AAAA/MM/JJ)
        dates.sort(key=lambda d: 0 if re.match(r"\d{4}", d) else 1)
        
        # Normalise la meilleure date au format JJ/MM/AAAA
        best_date = dates[0]
        return self._normalize_date_format(best_date)

    @staticmethod
    def _normalize_date_format(date_str: str) -> str:
        """Normalise une date vers le format JJ/MM/AAAA"""
        if not date_str:
            return date_str
        
        date_str = date_str.strip()
        
        # Format AAAA/MM/JJ → JJ/MM/AAAA
        if re.match(r'^\d{4}[./-]\d{1,2}[./-]\d{1,2}$', date_str):
            parts = re.split(r'[./-]', date_str)
            year, month, day = parts[0], parts[1], parts[2]
            return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        # Format JJ/MM/AAAA (normalise les zéros)
        if re.match(r'^\d{1,2}[./-]\d{1,2}[./-]\d{4}$', date_str):
            parts = re.split(r'[./-]', date_str)
            day, month, year = parts[0], parts[1], parts[2]
            return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        # Format "JJ mois AAAA" → JJ/MM/AAAA
        month_names = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12',
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        
        for month_name, month_num in month_names.items():
            pattern = rf'(\d{{1,2}})\s+{re.escape(month_name)}\s+(\d{{4}})'
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                day, year = match.groups()
                return f"{day.zfill(2)}/{month_num}/{year}"
        
        return date_str

    def _extract_invoice_number(self, text: str, lines: List[str]) -> Optional[str]:
        """Extraction priorisée du numéro de facture avec nettoyage"""
        
        # 1. Cas spécial "Vos références" pour MCA
        for i, line in enumerate(lines):
            if "Vos références" in line and i + 1 < len(lines):
                candidate = lines[i + 1].strip()
                if self._is_valid_invoice_number(candidate):
                    return self._clean_invoice_number(candidate)

        # 2. Labels explicites (Invoice No:, Facture:, etc.)
        for match in self._RE_INVOICE_LBL.finditer(text):
            candidate = match.group(1).strip()
            if self._is_valid_invoice_number(candidate):
                return self._clean_invoice_number(candidate)

        # 3. Patterns génériques (fallback)
        candidates = []
        for token in self._RE_GENERIC_NUM.findall(text):
            if self._is_valid_invoice_number(token):
                candidates.append(self._clean_invoice_number(token))
        
        return max(candidates, key=len) if candidates else None

    def _extract_vat_number(self, text: str) -> Optional[str]:
        """Extraction TVA européenne avec validation stricte"""
        
        # 1. Recherche prioritaire "VAT ID" explicite (pour Ubiquiti)
        vat_id_match = re.search(r"VAT\s+ID\s*:\s*([A-Z]{2}[A-Z0-9]{8,13})", text, re.IGNORECASE)
        if vat_id_match:
            candidate = vat_id_match.group(1)
            if self._RE_VAT_VALID.match(candidate):
                return candidate
        
        # 2. Recherche TVA française avec espaces (pour MCA/Synology)
        fr_match = re.search(r"TVA\s+(?:FR\s*)?([0-9\s]{11,})", text, re.IGNORECASE)
        if fr_match:
            numbers_only = re.sub(r"\s+", "", fr_match.group(1))
            if len(numbers_only) == 11 and numbers_only.isdigit():
                fr_vat = f"FR{numbers_only}"
                if self._RE_VAT_VALID.match(fr_vat):
                    return fr_vat
        
        # 3. Recherche standard avec validation par chiffres
        for raw in self._RE_VAT_ANY.findall(text):
            if not any(ch.isdigit() for ch in raw):
                continue
            
            normalized = re.sub(r"\s+", "", raw.upper())
            if self._RE_VAT_VALID.match(normalized):
                if normalized.startswith("FR") and "VAT ID" in text:
                    continue
                return normalized
        
        return None

    def _extract_vat_rate(self, text: str) -> Optional[float]:
        """Extrait le taux de TVA avec déduction automatique par pays."""
        
        vat_rates = []
        
        # 1. Recherche patterns explicites
        for match in self._RE_VAT_RATE.finditer(text):
            rate_str = match.group(1).replace(',', '.')
            try:
                rate = float(rate_str)
                if 0 <= rate <= 30:
                    vat_rates.append(rate)
            except ValueError:
                continue
        
        # 2. Recherche patterns français
        for match in self._RE_VAT_RATE_FR.finditer(text):
            rate_str = match.group(1).replace(',', '.')
            try:
                rate = float(rate_str)
                if 0 <= rate <= 30:
                    vat_rates.append(rate)
            except ValueError:
                continue
        
        # 3. Recherche dans tableaux
        for match in self._RE_VAT_RATE_TABLE.finditer(text):
            rate_str = match.group(1).replace(',', '.')
            try:
                rate = float(rate_str)
                if 0 <= rate <= 30:
                    vat_rates.append(rate)
            except ValueError:
                continue
        
        # 4. Calcul depuis montants
        if not vat_rates:
            calculated_rate = self._calculate_vat_rate_from_amounts(text)
            if calculated_rate:
                vat_rates.append(calculated_rate)
        
        # 5. Déduction automatique par pays TVA
        if not vat_rates:
            country_rate = self._deduce_vat_rate_by_country(text)
            if country_rate:
                vat_rates.append(country_rate)
        
        return max(vat_rates) if vat_rates else None

    def _extract_amount_ht(self, text: str) -> Optional[float]:
        """
        Extrait le montant Hors Taxes de la facture.
        Priorité : patterns explicites > calcul depuis TTC et taux TVA
        """
        
        ht_amounts = []
        
        # 1. Recherche patterns explicites "Total HT", "Montant HT"
        for match in self._RE_AMOUNT_HT.finditer(text):
            amount_str = match.group(1)
            amount_value = self._to_float(amount_str)
            if amount_value and amount_value > 0:
                ht_amounts.append(amount_value)
        
        # 2. Recherche dans tableaux "HT", "Excl. VAT"
        for match in self._RE_AMOUNT_HT_TABLE.finditer(text):
            amount_str = match.group(1)
            amount_value = self._to_float(amount_str)
            if amount_value and amount_value > 0:
                ht_amounts.append(amount_value)
        
        # 3. Si montants HT trouvés, retourner le plus élevé
        if ht_amounts:
            return max(ht_amounts)
        
        # 4. Calcul depuis TTC et taux de TVA si disponibles
        if hasattr(self, '_current_total_amount') and hasattr(self, '_current_vat_rate'):
            if self._current_total_amount and self._current_vat_rate:
                calculated_ht = self._calculate_ht_from_ttc_and_rate(
                    self._current_total_amount, 
                    self._current_vat_rate
                )
                if calculated_ht:
                    return calculated_ht
        
        return None

    @staticmethod
    def _calculate_ht_from_ttc_and_rate(ttc_amount: float, vat_rate: float) -> Optional[float]:
        """Calcule le montant HT à partir du TTC et du taux de TVA."""
        try:
            if ttc_amount > 0 and vat_rate >= 0:
                ht_amount = ttc_amount / (1 + (vat_rate / 100))
                return round(ht_amount, 2)
        except (ValueError, ZeroDivisionError):
            pass
        return None

    def _calculate_vat_rate_from_amounts(self, text: str) -> Optional[float]:
        """Calcule le taux de TVA à partir des montants HT, TVA et TTC."""
        
        # Patterns pour montants structurés
        ht_match = re.search(r"(?:total\s+ht|montant\s+ht|sous[- ]total)\s*:?\s*([0-9,. ]+)", text, re.IGNORECASE)
        vat_amount_match = re.search(r"(?:montant\s+tva|tva)\s*:?\s*([0-9,. ]+)", text, re.IGNORECASE)
        
        if ht_match and vat_amount_match:
            try:
                ht_amount = self._to_float(ht_match.group(1))
                vat_amount = self._to_float(vat_amount_match.group(1))
                
                if ht_amount and vat_amount and ht_amount > 0:
                    calculated_rate = (vat_amount / ht_amount) * 100
                    
                    # Arrondit aux taux standards français
                    if 19 <= calculated_rate <= 21:
                        return 20.0
                    elif 9 <= calculated_rate <= 11:
                        return 10.0
                    elif 5 <= calculated_rate <= 6:
                        return 5.5
                    elif calculated_rate <= 3:
                        return 2.1
                    
                    return round(calculated_rate, 1)
            except (ValueError, TypeError):
                pass
        
        return None

    def _deduce_vat_rate_by_country(self, text: str) -> Optional[float]:
        """Déduit le taux de TVA standard selon le pays détecté dans les identifiants."""
        
        # Taux de TVA standards par pays européen
        vat_country_rates = {
            'NL': 21.0,  # Pays-Bas (Ubiquiti)
            'FR': 20.0,  # France
            'DE': 19.0,  # Allemagne  
            'IT': 22.0,  # Italie
            'ES': 21.0,  # Espagne
            'BE': 21.0   # Belgique
        }
        
        # Cherche les patterns de TVA européenne déjà extraits
        for match in self._RE_VAT_ANY.findall(text):
            normalized = re.sub(r"\s+", "", match.upper())
            if self._RE_VAT_VALID.match(normalized):
                country_code = normalized[:2]
                if country_code in vat_country_rates:
                    return vat_country_rates[country_code]
        
        # Fallback : recherche explicite "VAT ID: NL..." pour Ubiquiti
        if re.search(r"VAT\s+ID\s*:\s*NL", text, re.IGNORECASE):
            return 21.0  # Taux standard néerlandais
        
        # Fallback : recherche "TVA FR" pour factures françaises
        if re.search(r"TVA\s+FR", text, re.IGNORECASE):
            return 20.0  # Taux standard français
        
        return None

    # ================================================================= #
    #                     VALIDATION & NETTOYAGE                        #
    # ================================================================= #
    
    @staticmethod
    def _is_valid_invoice_number(token: str) -> bool:
        """Valide un numéro de facture candidat"""
        if not token or len(token) < 5 or len(token) > 40:
            return False
        
        if not any(c.isdigit() for c in token):
            return False
        
        excluded_terms = ["TOTAL", "Total", "DELIVRAISON", "Taille", "logy", "Synology"]
        if any(term in token for term in excluded_terms):
            return False
        
        return True

    @staticmethod
    def _clean_invoice_number(token: str) -> str:
        """Nettoie un numéro de facture des préfixes indésirables."""
        prefixes_to_remove = ['s/view/', 'view/', 'invoice/', 'bill/', 'receipt/']
        
        for prefix in prefixes_to_remove:
            if token.startswith(prefix):
                token = token[len(prefix):]
        
        suffixes_to_remove = ['/', '#']
        for suffix in suffixes_to_remove:
            if token.endswith(suffix):
                token = token[:-len(suffix)]
        
        return token.strip()

    # ================================================================= #
    #                      UTILITAIRES GÉNÉRAUX                         #
    # ================================================================= #
    
    @staticmethod
    def _extract_text(pdf_path: Path) -> str:
        """Extrait le texte brut de toutes les pages du PDF."""
        with fitz.open(pdf_path) as doc:
            return "\n".join(page.get_text("text") for page in doc)

    @staticmethod
    def _to_float(raw: str) -> Optional[float]:
        """Convertit une chaîne de montant en float."""
        if not raw:
            return None
        
        normalized = "".join(
            c for c in unicodedata.normalize("NFKD", raw)
            if c.isdigit() or c in {",", "."}
        ).replace(",", ".")
        
        try:
            return float(normalized)
        except ValueError:
            return None

    @staticmethod
    def _calculate_confidence(result: InvoiceExtractionResult) -> float:
        """Calcule un score de confiance basé sur les champs extraits."""
        score = 0.80  # Base
        
        if result.total_amount:
            score += 0.05
        if result.invoice_date:
            score += 0.05
        if result.invoice_number:
            score += 0.05
        if result.legal_identifiers.get("numero_tva"):
            score += 0.03
        if result.vat_rate is not None:
            score += 0.01
        if result.amount_ht is not None:  # NOUVEAU
            score += 0.01
            
        return min(score, 1.0)
