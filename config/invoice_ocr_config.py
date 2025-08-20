# config/invoice_ocr_config.py
"""
Configuration exemple pour l'OCR configurable
Aucune donnée personnelle - uniquement des patterns génériques
"""

ADVANCED_INVOICE_CONFIG = {
    "languages": ["fra", "eng"],
    "confidence_threshold": 0.7,
    "preprocessing": ["contrast", "denoise", "deskew"],
    "extraction_mode": "standard",
    
    # Patterns personnalisés configurables
    "custom_patterns": {
        # Patterns spécifiques aux marketplaces
        "marketplace_patterns": {
            "patterns": [
                r"(marketplace|market\s+place)",
                r"(vendeur|seller)[:\s]*([A-Z][A-Za-z\s]+)"
            ],
            "flags": 2,  # re.IGNORECASE
            "description": "Patterns pour marketplaces"
        },
        
        # Patterns pour références spéciales
        "extended_references": {
            "patterns": [
                r"(?:ref|reference)[:\s]*([A-Z0-9\-]{5,20})",
                r"(?:tracking|suivi)[:\s]*([A-Z0-9]+)"
            ],
            "flags": 2,
            "description": "Références étendues"
        },
        
        # Patterns pour conditions de paiement
        "payment_terms": {
            "patterns": [
                r"(?:paiement|payment)[:\s]*([\w\s]{5,30})",
                r"(?:échéance|due)[:\s]*(\d+\s*jours?)"
            ],
            "flags": 2,
            "description": "Conditions de paiement"
        }
    },
    
    # Règles de filtrage configurables
    "filtering_rules": {
        "min_amount": 0.01,
        "max_amount": 999999.99,
        "min_invoice_number_length": 3,
        "exclude_invoice_numbers": ["total", "description", "date"]
    },
    
    # Options de post-traitement
    "post_processing": {
        "calculate_vat_from_amounts": True,
        "deduplicate_results": True,
        "confidence_weighting": {
            "amounts": 0.3,
            "references": 0.2,
            "dates": 0.2,
            "legal_ids": 0.3
        }
    }
}

