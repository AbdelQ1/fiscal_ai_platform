# config/hybrid_config.py
HYBRID_CONFIG = {
    # Configuration du moteur rapide
    "fast_extraction": {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.65,
        "enable_fallback": True
    },
    
    # Configuration du moteur OCR
    "ocr_extraction": {
        "languages": ["fra", "eng"],
        "preprocessing": ["contrast", "denoise", "deskew"],
        "confidence_threshold": 0.75,
        "gpu_acceleration": True
    },
    
    # Seuils de décision
    "thresholds": {
        "confidence_threshold": 0.75,      # Seuil pour accepter un résultat
        "ocr_fallback_threshold": 0.6,     # Seuil pour déclencher OCR
        "merge_threshold": 0.8             # Seuil pour fusion des résultats
    },
    
    # Stratégies de fallback
    "fallback_strategy": "auto",  # auto, manual, disabled
    "max_processing_time": 10,    # secondes max par document
}

