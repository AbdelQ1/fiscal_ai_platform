"""
Bibliothèque de patterns (regex & règles) réservée au handler FACTURE.

!  À exposer via `INVOICE_PATTERNS` et `__all__` pour que les importeurs
   puissent l'importer en toute sécurité.
"""

from typing import Dict, Any

INVOICE_PATTERNS: Dict[str, Any] = {
    # --------------------  Numéro de facture  --------------------- #
    "invoice_number": [
        r"\bfacture\s*[:#-]?\s*([0-9]{5,})\b",
        r"\bN[°ºo]\s*[:\-]?\s*([0-9]{5,})\b",
        r"Invoice\s+No\.?\s*:\s*([A-Z0-9_\-]+)",
        r"^[^\n]*[№N°]\s*([0-9]{6,})$",
        r"\s*[0-9]{5,10}\s*",  # dernier filet
    ],

    # --------------------  Numéro de TVA  ------------------------- #
    "vat_number": r"\b(?:FR|DE|IT|ES|BE|NL)[0-9A-Z\s]{8,15}\b",

    # --------------------  Montants  ------------------------------ #
    "total_amount": {
        "labels": [
            r"total[^0-9\na-z]{0,20}(?:t\s*\.?\s*t\s*\.?\s*c\s*\.?|ttc\.?)",
            r"total\s+[aà]\s+payer",
            r"montant\s+[aà]\s+payer",
            r"net\s+[aà]\s+payer",
        ],
        "amount_pattern": r"([0-9]{1,3}(?:[\u202F\u00A0 ]?[0-9]{3})*[.,][0-9]{2})",
        "search_window": 4,
        "selection_method": "max",  # « max » = TTC (vs HT)
    },

    # --------------------  Devise  -------------------------------- #
    "currency": {
        "symbols": {"€": "EUR", "$": "USD", "£": "GBP", "Fr": "CHF"},
        "iso_codes": ["EUR", "USD", "GBP", "CHF"],
        "default": "EUR",
    },
}

__all__ = ["INVOICE_PATTERNS"]