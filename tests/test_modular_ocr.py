#!/usr/bin/env python3
"""Test de l'architecture OCR modulaire"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.ocr.modular_ocr import ModularOCRProcessor

def test_modular_architecture():
    """Test de l'architecture modulaire"""
    config = {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.65,
        "preprocessing": ["contrast", "denoise", "deskew"],
        "auto_detect": True
    }
    
    processor = ModularOCRProcessor(config)
    
    print("🏗️ Test Architecture OCR Modulaire")
    print("=" * 60)
    
    # Affichage des handlers disponibles
    handlers = processor.get_available_handlers()
    print("📋 Handlers disponibles:")
    for name, info in handlers.items():
        print(f"   {name}: {info['document_type']} ({info['patterns_count']} patterns)")
    
    # Test avec votre facture
    invoice_path = Path("/Users/abdel/Documents/Facture Batterie Bosch.pdf")
    
    if invoice_path.exists():
        print(f"\n🧾 Test sur facture: {invoice_path.name}")
        
        # Test avec détection automatique
        result = processor.process_document(invoice_path)
        
        if result.success:
            print(f"✅ Traitement réussi")
            print(f"   Type détecté: {getattr(result, 'document_type_detected', 'N/A')}")
            print(f"   Handler utilisé: {getattr(result, 'handler_used', 'N/A')}")
            print(f"   Confiance: {result.confidence:.2f}")
            print(f"   Entités: {len(result.extracted_entities or {})}")
            
            if result.extracted_entities:
                print(f"\n🏷️ Entités extraites:")
                for entity_type, values in result.extracted_entities.items():
                    display_vals = values[:2] if isinstance(values, list) else values
                    print(f"   {entity_type}: {display_vals}{'...' if isinstance(values, list) and len(values) > 2 else ''}")
        
        # Test avec type forcé
        print(f"\n🎯 Test avec type forcé 'fiscal':")
        result_fiscal = processor.process_document(invoice_path, 'fiscal')
        
        if result_fiscal.success:
            print(f"   Entités fiscales: {len(result_fiscal.extracted_entities or {})}")
    
    else:
        print("⚠️ Fichier de test non trouvé")
    
    print(f"\n✅ Test terminé")

if __name__ == "__main__":
    test_modular_architecture()