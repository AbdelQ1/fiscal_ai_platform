# tests/test_hybrid_processor.py
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from modules.ocr.hybrid_invoice_processor import HybridInvoiceProcessor

def test_hybrid_performance():
    """Teste les performances du processeur hybride."""
    config = {
        "languages": ["fra", "eng"],
        "confidence_threshold": 0.75,
        "ocr_fallback_threshold": 0.6,
        "preprocessing": ["contrast", "denoise", "deskew"]
    }
    
    processor = HybridInvoiceProcessor(config)
    test_files = list((project_root / "invoices_to_test").glob("*.pdf"))
    
    results = {
        "fast_only": 0,
        "ocr_fallback": 0, 
        "hybrid_merged": 0,
        "failed": 0
    }
    
    for file_path in test_files:
        result = processor.process_invoice(file_path)
        method = getattr(result, 'processing_method', 'unknown')
        results[method] = results.get(method, 0) + 1
        
        print(f"📄 {file_path.name}")
        print(f"   • Méthode: {method}")
        print(f"   • Total: {result.total_amount}€")
        print(f"   • Confiance: {result.extraction_confidence:.2f}")
        print()
    
    print("📊 STATISTIQUES HYBRIDES:")
    for method, count in results.items():
        print(f"   • {method}: {count} documents")

if __name__ == "__main__":
    test_hybrid_performance()

