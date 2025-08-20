#!/usr/bin/env python3
"""
Script pour forcer l'utilisation de l'OCR réel et voir le contenu du PDF
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Désactiver le mode test pour forcer l'OCR réel
os.environ.pop('FISCAL_OCR_TEST_MODE', None)

from modules.ocr.configurable_invoice_ocr import ConfigurableInvoiceOCR

def debug_real_ocr():
    config = {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.65,
        "preprocessing": ["contrast", "denoise", "deskew"],
    }
    
    # Créer une version modifiée qui force l'OCR réel
    class DebugOCR(ConfigurableInvoiceOCR):
        def _extract_text_with_base_ocr(self, file_path):
            try:
                from .base_ocr import FiscalOCRModule
                ocr = FiscalOCRModule(self.base_ocr_config)
                result = ocr.process_document(file_path, "invoice")
                print(f"🔍 OCR RÉEL - Texte extrait ({len(result.text)} car.) avec confiance de {result.confidence:.2f}")
                print("📄 CONTENU COMPLET DU PDF:")
                print("=" * 60)
                print(result.text)
                print("=" * 60)
                return result.text if result.success else ""
            except Exception as e:
                print(f"❌ Erreur OCR réel: {e}")
                return super()._extract_text_with_base_ocr(file_path)
    
    ocr_system = DebugOCR(config)
    test_file = Path("invoices_to_test/Facture MCA Syno RAM 8G 2024.pdf")
    
    if not test_file.exists():
        print(f"❌ Fichier non trouvé: {test_file}")
        return
    
    result = ocr_system.process_invoice(test_file)
    
    print("\n📊 RÉSULTATS FINAUX:")
    print(f"Date: {result.invoice_date}")
    print(f"Numéro: {result.invoice_number}")
    print(f"Total: {result.total_amount}€")
    print(f"HT: {result.subtotal_ht}€")
    print(f"TVA: {result.vat_amount}€")
    print(f"N° TVA: {result.legal_identifiers.get('vat_number')}")

if __name__ == "__main__":
    debug_real_ocr()