#!/usr/bin/env python3
"""
Script de débogage pour analyser le contenu réel du PDF
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from modules.ocr.configurable_invoice_ocr import ConfigurableInvoiceOCR

def debug_pdf_content():
    config = {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.65,
        "preprocessing": ["contrast", "denoise", "deskew"],
    }
    
    ocr_system = ConfigurableInvoiceOCR(config)
    test_file = Path("invoices_to_test/Facture MCA Syno RAM 8G 2024.pdf")
    
    if not test_file.exists():
        print(f"❌ Fichier non trouvé: {test_file}")
        return
    
    print(f"🔍 Analyse du contenu de: {test_file.name}")
    print("=" * 60)
    
    # Extraction du texte brut
    raw_text = ocr_system._extract_text_with_base_ocr(test_file)
    
    print("📄 TEXTE BRUT EXTRAIT:")
    print("-" * 40)
    print(raw_text)
    print("-" * 40)
    print(f"Longueur: {len(raw_text)} caractères")
    
    # Analyse avec extraction structurée
    result = ocr_system.process_invoice(test_file)
    
    print("\n📊 DONNÉES EXTRAITES:")
    print(f"✅ Succès: {result.success}")
    print(f"📅 Date: {result.invoice_date}")
    print(f"🔢 Numéro: {result.invoice_number}")
    print(f"💰 Total: {result.total_amount}€")
    print(f"💰 HT: {result.subtotal_ht}€")
    print(f"💰 TVA: {result.vat_amount}€")
    print(f"🏢 N° TVA: {result.legal_identifiers.get('vat_number')}")
    print(f"🎯 Confiance: {result.extraction_confidence:.2f}")
    print(f"⏱️  Temps: {result.processing_time:.2f}s")
    
    print(f"\n🔍 Montants trouvés: {result.amounts_found}")
    print(f"🏷️  Patterns détectés: {result.patterns_matched}")

if __name__ == "__main__":
    debug_pdf_content()