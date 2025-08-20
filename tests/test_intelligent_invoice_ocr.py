# tests/test_intelligent_invoice_ocr.py
#!/usr/bin/env python3
"""Test du système OCR intelligent universel"""

import sys
from typing import List
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.ocr.intelligent_invoice_ocr import IntelligentInvoiceOCR

def test_universal_invoice_extraction():
    """Test de l'extraction universelle sur votre facture Amazon"""
    
    config = {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.65,
        "preprocessing": ["contrast", "denoise", "deskew"],
        "extract_layout": True,
        "universal_extraction": True
    }
    
    intelligent_ocr = IntelligentInvoiceOCR(config)
    
    # Votre facture Amazon
    invoice_path = Path("/Users/abdel/Documents/Facture Batterie Bosch.pdf")
    
    print("🧠 TEST SYSTÈME OCR INTELLIGENT UNIVERSEL")
    print("=" * 70)
    
    if not invoice_path.exists():
        print("❌ Fichier non trouvé!")
        return
    
    # Traitement intelligent
    result = intelligent_ocr.process_invoice(invoice_path)
    
    if result['success']:
        print(f"✅ Traitement réussi")
        print(f"   ⏱️ Temps: {result['processing_time']:.2f}s")
        print(f"   🔍 Confiance OCR: {result['ocr_confidence']:.2f}")
        print(f"   🧠 Confiance extraction: {result['extraction_confidence']:.2f}")
        print(f"   📋 Régions détectées: {result['regions_detected']}")
        print(f"   🏷️ Champs extraits: {result['fields_extracted']}")
        
        # Analyse des données extraites
        invoice_data = result['invoice_data']
        
        print(f"\n📊 DONNÉES EXTRAITES PAR CATÉGORIE:")
        
        # Fournisseur
        supplier = invoice_data['supplier']
        print(f"\n🏢 FOURNISSEUR:")
        for field, value in supplier.items():
            if value:
                print(f"   {field}: {value}")
        
        # Client
        client = invoice_data['client']
        print(f"\n👤 CLIENT:")
        for field, value in client.items():
            if value:
                print(f"   {field}: {value}")
        
        # Références
        references = invoice_data['references']
        print(f"\n📋 RÉFÉRENCES:")
        for field, value in references.items():
            if value:
                print(f"   {field}: {value}")
        
        # Montants
        amounts = invoice_data['amounts']
        print(f"\n💰 MONTANTS:")
        for field, value in amounts.items():
            if value is not None:
                if isinstance(value, (int, float)):
                    print(f"   {field}: {value:.2f}€")
                else:
                    print(f"   {field}: {value}")
        
        # Validation des attentes
        print(f"\n🎯 VALIDATION DES ATTENTES:")
        
        expectations = [
            ("Nom fournisseur", supplier.get('name'), lambda x: 'amazon' in str(x).lower() if x else False),
            ("Numéro de facture", references.get('invoice_number'), lambda x: x is not None and len(str(x)) > 3),
            ("Date facture", references.get('invoice_date'), lambda x: x is not None),
            ("Nom client", client.get('name'), lambda x: x is not None and len(str(x)) > 2),
            ("Adresse client", client.get('address'), lambda x: x is not None and '92350' in str(x)),
            ("Montant total", amounts.get('total_ttc'), lambda x: x is not None and 150 <= float(x) <= 200),
            ("Numéro TVA", supplier.get('vat_number'), lambda x: x is not None and 'FR' in str(x))
        ]
        
        success_count = 0
        for desc, value, check in expectations:
            is_valid = check(value)
            status = "✅" if is_valid else "❌"
            print(f"   {status} {desc}: {value if value else 'Non trouvé'}")
            if is_valid:
                success_count += 1
        
        print(f"\n📈 Score de réussite: {success_count}/{len(expectations)} ({success_count/len(expectations)*100:.0f}%)")
        
        if success_count >= len(expectations) * 0.7:
            print("🎉 Extraction majoritairement réussie!")
        else:
            print("⚠️ Extraction partielle - système à améliorer")
    
    else:
        print(f"❌ Échec: {result['error']}")
    
    # Affichage des champs supportés
    print(f"\n📋 CHAMPS SUPPORTÉS PAR LE SYSTÈME:")
    supported = intelligent_ocr.get_supported_fields()
    for category, fields in supported.items():
        print(f"   {category.upper()}: {', '.join(fields)}")

if __name__ == "__main__":
    test_universal_invoice_extraction()

