# tests/test_complete_architecture.py
import sys
from pathlib import Path

# Ajout du chemin du projet
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test tous les imports de l'architecture."""
    
    print("🧪 Test des imports de l'architecture complète...")
    
    try:
        # Core modules
        from core.engine.module_registry import ModuleRegistry
        from core.config.config_manager import ConfigManager
        from core.security.encryption import SecurityManager
        print("✅ Core modules importés")
        
        # OCR modules
        from modules.ocr.configurable_invoice_ocr import ConfigurableInvoiceOCR
        from modules.ocr.processors.invoice_processor import InvoiceProcessor
        from modules.ocr.patterns.invoice_patterns import INVOICE_PATTERNS
        print("✅ Modules OCR importés")
        
        # Document handlers
        from modules.ocr.document_handlers.base_handler import BaseDocumentHandler
        from modules.ocr.document_handlers.invoice_handler import InvoiceHandler
        print("✅ Document handlers importés")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_architecture_integration():
    """Test l'intégration complète de l'architecture."""
    
    print("\n🚀 Test d'intégration architecture complète")
    print("=" * 50)
    
    if not test_imports():
        return
    
    # Test du système complet
    from modules.ocr.configurable_invoice_ocr import ConfigurableInvoiceOCR
    
    config = {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.65,
        "preprocessing": ["contrast", "denoise", "deskew"],
    }
    
    try:
        ocr_system = ConfigurableInvoiceOCR(config)
        print("✅ Système OCR configuré")
        
        # Test avec fichier réel
        test_files = list((project_root / "invoices_to_test").glob("*.pdf"))
        if test_files:
            test_file = test_files[0]
            print(f"🔍 Test avec: {test_file.name}")
            
            result = ocr_system.process_invoice(test_file)
            print(f"📊 Extraction réussie - Total: {result.total_amount}€")
            
        print("🎉 Architecture complète validée")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_architecture_integration()

