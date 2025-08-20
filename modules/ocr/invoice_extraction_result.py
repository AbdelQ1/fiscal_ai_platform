# modules/ocr/invoice_extraction_result.py
"""
Classe de résultat pour l'extraction de factures
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Any


@dataclass
class InvoiceExtractionResult:
    """Résultat structuré de l'extraction d'une facture PDF."""
    
    # Champs principaux
    total_amount: Optional[float] = None
    invoice_date: Optional[str] = None
    invoice_number: Optional[str] = None
    legal_identifiers: Dict[str, str] = None
    
    # Champs TVA
    vat_rate: Optional[float] = None
    amount_ht: Optional[float] = None  # NOUVEAU : Montant HT
    
    # Métadonnées d'extraction
    processing_method: str = "unknown"
    extraction_confidence: float = 0.0
    amounts_found: List[str] = None
    
    def __post_init__(self):
        if self.legal_identifiers is None:
            self.legal_identifiers = {}
        if self.amounts_found is None:
            self.amounts_found = []
