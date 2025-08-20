# diagnostic_ocr_base.py
#!/usr/bin/env python3
"""Diagnostic du module OCR de base"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_base_ocr():
    """Test du module OCR de base seul"""
    
    from modules.ocr.base_ocr import FiscalOCRModule
    
    config = {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.6,
        "preprocessing": ["contrast", "denoise", "deskew"],
        "fiscal_mode": False
    }
    
    ocr = FiscalOCRModule(config)
    invoice_path = Path("/Users/abdel/Documents/Facture Batterie Bosch.pdf")
    
    print("🔍 DIAGNOSTIC OCR DE BASE")
    print("=" * 50)
    
    # Test direct du module de base
    result = ocr.process_document(invoice_path, "invoice")
    
    print(f"Succès: {result.success}")
    print(f"Confiance: {result.confidence}")
    print(f"Longueur texte: {len(result.text)}")
    print(f"Temps: {result.processing_time:.2f}s")
    
    if result.text:
        print(f"\nPremiers 500 caractères:")
        print(f"'{result.text[:500]}'")
        
        # Recherche manuelle dans le vrai texte
        print(f"\n🔍 RECHERCHE MANUELLE DANS LE TEXTE COMPLET:")
        
        # Recherche montants 
        import re
        montants = re.findall(r'(\d+[,\.]\d{2})', result.text)
        print(f"Montants trouvés: {montants}")
        
        # Recherche TVA
        tva = re.findall(r'(FR[A-Z0-9]{11})', result.text)
        print(f"TVA trouvées: {tva}")
        
        # Recherche dates
        dates = re.findall(r'(\d{1,2})\s+(février|mars|avril)\s+(\d{4})', result.text, re.IGNORECASE)
        print(f"Dates trouvées: {dates}")
        
    else:
        print("❌ Aucun texte extrait par l'OCR de base!")

if __name__ == "__main__":
    test_base_ocr()

