# tests/test_privacy_compliant_ocr.py
#!/usr/bin/env python3
"""Test du module OCR respectueux de la vie privée"""

import sys
from typing import List
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.ocr.privacy_compliant_ocr import PrivacyCompliantOCR

def test_privacy_compliant_extraction():
    """Test d'extraction respectueuse de la vie privée"""
    
    config = {
        "languages": ["fra", "eng"],
        "anonymize_personal_data": True,  # Activation anonymisation
        "confidence_threshold": 0.65
    }
    
    privacy_ocr = PrivacyCompliantOCR(config)
    
    # Votre facture (traitée de manière anonymisée)
    invoice_path = Path("/Users/abdel/Documents/Facture Batterie Bosch.pdf")
    
    print("🔒 TEST MODULE OCR PRIVACY-COMPLIANT")
    print("=" * 60)
    
    if not invoice_path.exists():
        print("❌ Fichier non trouvé!")
        return
    
    # Traitement anonymisé
    result = privacy_ocr.process_invoice_anonymized(invoice_path)
    
    print(f"✅ Traitement anonymisé terminé")
    print(f"   🆔 ID fournisseur anonyme: {result.supplier_id}")
    print(f"   🆔 ID client anonyme: {result.client_id}")
    
    # Affichage des données NON personnelles extraites
    print(f"\n💰 DONNÉES FINANCIÈRES (NON PERSONNELLES):")
    if result.total_ttc:
        print(f"   Total TTC: {result.total_ttc:.2f}€")
    if result.subtotal_ht:
        print(f"   Sous-total HT: {result.subtotal_ht:.2f}€")
    if result.vat_amount:
        print(f"   TVA: {result.vat_amount:.2f}€")
    
    print(f"\n📋 RÉFÉRENCES TECHNIQUES (NON PERSONNELLES):")
    if result.invoice_number:
        print(f"   Numéro facture: {result.invoice_number}")
    if result.invoice_date:
        print(f"   Date facture: {result.invoice_date}")
    
    print(f"\n🏢 DONNÉES LÉGALES PUBLIQUES (NON PERSONNELLES):")
    if result.supplier_siret:
        print(f"   SIRET: {result.supplier_siret}")
    if result.supplier_vat:
        print(f"   N° TVA: {result.supplier_vat}")
    
    print(f"\n🌍 ZONES GÉOGRAPHIQUES ANONYMISÉES:")
    if result.supplier_region:
        print(f"   Région fournisseur: {result.supplier_region}")
    if result.client_postal_area:
        print(f"   Zone client: {result.client_postal_area}")
    
    # Rapport de conformité RGPD
    privacy_report = privacy_ocr.get_privacy_report()
    print(f"\n🔒 RAPPORT CONFORMITÉ RGPD:")
    print(f"   Statut: {privacy_report['data_protection_status']}")
    print(f"   Données personnelles traitées: {privacy_report['personal_data_processed']}")
    print(f"   Anonymisation: {'✅' if privacy_report['anonymization_active'] else '❌'}")
    
    print(f"\n📊 TYPES DE DONNÉES EXTRAITES (CONFORMES):")
    for data_type in privacy_report['data_types_extracted']:
        print(f"   ✅ {data_type}")
    
    print(f"\n🛡️ DONNÉES PERSONNELLES ANONYMISÉES:")
    for data_type in privacy_report['personal_data_types_anonymized']:
        print(f"   🔒 {data_type}")
    
    print(f"\n🎯 GARANTIES JURIDIQUES:")
    for guarantee in privacy_report['compliance_guarantees']:
        print(f"   ⚖️ {guarantee}")

if __name__ == "__main__":
    test_privacy_compliant_extraction()

