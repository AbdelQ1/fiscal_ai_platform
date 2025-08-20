# tests/test_configurable_invoice_ocr.py
#!/usr/bin/env python3
"""Test du module OCR configurable sans données personnelles statiques"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.ocr.configurable_invoice_ocr import ConfigurableInvoiceOCR

def test_configurable_extraction():
    """Test d'extraction configurable sur votre facture"""
    
    # Configuration sans aucune donnée personnelle codée
    config = {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.65,
        "preprocessing": ["contrast", "denoise", "deskew"],
        "extraction_mode": "standard",
        "custom_patterns": {
            # Exemple de pattern personnalisé (si besoin)
            "special_references": {
                "patterns": [r"REF[:\s]*([A-Z0-9]+)"],
                "flags": 0,
                "description": "Références spéciales"
            }
        }
    }
    
    ocr = ConfigurableInvoiceOCR(config)
    
    # Votre facture
    invoice_path = Path("/Users/abdel/Documents/Facture Batterie Bosch.pdf")
    
    print("🔧 TEST MODULE OCR CONFIGURABLE")
    print("=" * 60)
    print("✅ Aucune donnée personnelle codée en dur")
    print("✅ Patterns entièrement configurables")
    
    if not invoice_path.exists():
        print("❌ Fichier non trouvé!")
        return
    
    # Traitement
    result = ocr.process_invoice(invoice_path)
    
    if result.success:
        print(f"\n✅ Extraction réussie")
        print(f"   ⏱️ Temps: {result.processing_time:.2f}s")
        print(f"   📊 Confiance: {result.extraction_confidence:.2f}")
        print(f"   🎯 Patterns utilisés: {len(result.patterns_matched)}")
        
        # === DONNÉES TECHNIQUES (NON PERSONNELLES) ===
        print(f"\n📋 DONNÉES TECHNIQUES EXTRAITES:")
        
        if result.invoice_number:
            print(f"   📄 Numéro facture: {result.invoice_number}")
        
        if result.invoice_date:
            print(f"   📅 Date facture: {result.invoice_date}")
        
        # === MONTANTS ===
        print(f"\n💰 DONNÉES FINANCIÈRES:")
        
        if result.total_amount:
            print(f"   💵 Montant total: {result.total_amount:.2f}€")
        
        if result.subtotal_ht:
            print(f"   📊 Sous-total HT: {result.subtotal_ht:.2f}€")
        
        if result.vat_amount:
            print(f"   🏛️ TVA: {result.vat_amount:.2f}€")
        
        if result.amounts_found:
            print(f"   📈 Tous montants trouvés: {[f'{a:.2f}€' for a in result.amounts_found[:5]]}")
        
        # === IDENTIFIANTS LÉGAUX (PUBLICS) ===
        if result.legal_identifiers:
            print(f"\n🏢 IDENTIFIANTS LÉGAUX (PUBLICS):")
            for id_type, id_value in result.legal_identifiers.items():
                print(f"   {id_type.upper()}: {id_value}")
        
        # === INFORMATIONS D'ENTITÉ (GÉNÉRIQUES) ===
        if result.supplier_info:
            print(f"\n📞 INFORMATIONS DE CONTACT (GÉNÉRIQUES):")
            for info_type, info_values in result.supplier_info.items():
                if isinstance(info_values, list):
                    print(f"   {info_type}: {', '.join(info_values[:2])}")
                else:
                    print(f"   {info_type}: {info_values}")
        
        # === PATTERNS UTILISÉS ===
        print(f"\n🎯 PATTERNS ACTIVÉS:")
        for pattern in result.patterns_matched:
            print(f"   ✅ {pattern}")
        
        # === VALIDATION DES ATTENTES ===
        print(f"\n📊 VALIDATION DES EXTRACTIONS:")
        
        validations = [
            ("Montant total détecté", result.total_amount is not None and 160 <= result.total_amount <= 180),
            ("Date présente", result.invoice_date is not None),
            ("Identifiants légaux", result.legal_identifiers is not None),
            ("Numéro facture", result.invoice_number is not None),
            ("Confiance acceptable", result.extraction_confidence >= 0.6)
        ]
        
        success_count = sum(1 for _, valid in validations if valid)
        
        for desc, valid in validations:
            status = "✅" if valid else "❌"
            print(f"   {status} {desc}")
        
        print(f"\n📈 Score validation: {success_count}/{len(validations)} ({success_count/len(validations)*100:.0f}%)")
        
    else:
        print(f"❌ Échec: {result.error_message}")
    
    # Informations sur la configuration
    config_info = ocr.get_configuration_info()
    print(f"\n🔧 CONFIGURATION:")
    for key, value in config_info.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    test_configurable_extraction()

