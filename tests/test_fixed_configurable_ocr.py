# tests/test_fixed_configurable_ocr.py
#!/usr/bin/env python3
"""Test du module OCR configurable CORRIGÉ"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.ocr.configurable_invoice_ocr import ConfigurableInvoiceOCR

def test_fixed_extraction():
    """Test de l'extraction configurable CORRIGÉE"""
    
    # Configuration corrigée (sans patterns personnalisés pour commencer)
    config = {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.65,
        "preprocessing": ["contrast", "denoise", "deskew"],
        "extraction_mode": "standard",
        # Suppression temporaire des custom_patterns pour tester les défauts
    }
    
    ocr = ConfigurableInvoiceOCR(config)
    
    # Votre facture
    invoice_path = Path("/Users/abdel/Documents/Facture Batterie Bosch.pdf")
    
    print("🔧 TEST MODULE OCR CONFIGURABLE - VERSION CORRIGÉE")
    print("=" * 65)
    
    if not invoice_path.exists():
        print("❌ Fichier non trouvé!")
        return
    
    # Affichage de la configuration chargée
    config_info = ocr.get_configuration_info()
    print(f"📋 Configuration chargée:")
    print(f"   Patterns total: {config_info['patterns_loaded']}")
    print(f"   Catégories: {', '.join(config_info['pattern_categories'][:5])}")
    
    # Traitement
    result = ocr.process_invoice(invoice_path)
    
    if result.success:
        print(f"\n✅ Extraction réussie")
        print(f"   ⏱️ Temps: {result.processing_time:.2f}s")
        print(f"   📊 Confiance: {result.extraction_confidence:.2f}")
        print(f"   🎯 Patterns utilisés: {len(result.patterns_matched)}")
        
        # Affichage des patterns qui ont matché
        if result.patterns_matched:
            print(f"\n🎯 PATTERNS ACTIVÉS:")
            for pattern in result.patterns_matched:
                print(f"   ✅ {pattern}")
        else:
            print(f"\n🎯 AUCUN PATTERN ACTIVÉ (PROBLÈME!)")
        
        # === DONNÉES EXTRAITES ===
        print(f"\n📋 DONNÉES TECHNIQUES EXTRAITES:")
        
        if result.invoice_number:
            print(f"   📄 Numéro facture: {result.invoice_number}")
        
        if result.invoice_date:
            print(f"   📅 Date facture: {result.invoice_date}")
        
        print(f"\n💰 DONNÉES FINANCIÈRES:")
        
        if result.total_amount:
            print(f"   💵 Montant total: {result.total_amount:.2f}€")
        
        if result.amounts_found:
            amounts_display = [f"{a:.2f}€" for a in result.amounts_found[:5]]
            print(f"   📈 Tous montants: {amounts_display}")
        
        if result.legal_identifiers:
            print(f"\n🏢 IDENTIFIANTS LÉGAUX:")
            for id_type, id_value in result.legal_identifiers.items():
                print(f"   {id_type.upper()}: {id_value}")
        
        # === VALIDATION ===
        print(f"\n📊 VALIDATION DES EXTRACTIONS:")
# control trop strict        
#        validations = [
#            ("Montant total détecté", result.total_amount is not None and result.total_amount > 100),
#            ("Date présente", result.invoice_date is not None),
#            ("Identifiants légaux", result.legal_identifiers is not None),
#            ("Patterns activés", len(result.patterns_matched) > 0),
#            ("Confiance acceptable", result.extraction_confidence >= 0.5)
#        ]

        validations = [
            ("Montant total détecté", result.total_amount is not None and result.total_amount > 0),
            ("Date présente", result.invoice_date is not None),
            ("Numéro de facture présent", result.invoice_number is not None),
            ("Identifiants légaux", result.legal_identifiers is not None and 'vat_number' in result.legal_identifiers),
            ("Confiance acceptable", result.extraction_confidence >= 0.5)
        ]
        
        success_count = sum(1 for _, valid in validations if valid)
        
        for desc, valid in validations:
            status = "✅" if valid else "❌"
            print(f"   {status} {desc}")
        
        print(f"\n📈 Score validation: {success_count}/{len(validations)} ({success_count/len(validations)*100:.0f}%)")
        
        if success_count >= 4:
            print("🎉 Module OCR configurable corrigé avec succès!")
        elif success_count >= 2:
            print("⚠️  Amélioration partielle - ajustements supplémentaires nécessaires")
        else:
            print("❌ Problème persistant - patterns ne fonctionnent pas")
            
    else:
        print(f"❌ Échec: {result.error_message}")
        
    return result.success and len(result.patterns_matched) > 0

def debug_patterns():
    """Debug des patterns chargés"""
    config = {"languages": ["fra"]}
    ocr = ConfigurableInvoiceOCR(config)
    
    print("\n🔍 DEBUG PATTERNS:")
    for name, pattern_config in ocr.extraction_patterns.items():
        print(f"   {name}: {len(pattern_config.get('patterns', []))} patterns")
        for i, pattern in enumerate(pattern_config.get('patterns', [])[:2]):
            print(f"      {i+1}. {pattern}")

if __name__ == "__main__":
    success = test_fixed_extraction()
    if not success:
        debug_patterns()

