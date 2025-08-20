# modules/ocr/intelligent_invoice_ocr.py
from typing import Dict, Optional, List
from pathlib import Path
import time

from .base_ocr import FiscalOCRModule, OCRResult
from .layout_detector import IntelligentLayoutDetector
from .field_extractor import UniversalFieldExtractor, InvoiceData

class IntelligentInvoiceOCR:
    """Module OCR intelligent pour factures universelles"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Composants intelligents
        self.base_ocr = FiscalOCRModule(config)
        self.layout_detector = IntelligentLayoutDetector()
        self.field_extractor = UniversalFieldExtractor()
        
        self.logger = self.base_ocr.logger
        
        self.logger.info("🧠 Module OCR Intelligent initialisé")
        self.logger.info("   - Détection de layout automatique")
        self.logger.info("   - Extraction de champs universelle")
        self.logger.info("   - Support multi-fournisseurs")
    
    def process_invoice(self, file_path: Path) -> Dict:
        """Traitement intelligent complet d'une facture"""
        start_time = time.time()
        
        try:
            self.logger.info(f"🧾 Traitement intelligent: {file_path.name}")
            
            # 1. OCR de base pour extraire le texte et données brutes
            base_result = self.base_ocr.process_document(file_path, "invoice")
            
            if not base_result.success:
                return {
                    'success': False,
                    'error': base_result.error_message,
                    'processing_time': time.time() - start_time
                }
            
            # 2. Analyse intelligente du layout
            # Note: On simule les données OCR détaillées nécessaires
            ocr_data = self._extract_detailed_ocr_data(file_path)
            regions = self.layout_detector.analyze_layout(ocr_data)
            
            self.logger.info(f"   📋 Layout analysé: {len(regions)} régions détectées")
            
            # 3. Extraction intelligente des champs
            invoice_data = self.field_extractor.extract_fields(regions)
            
            self.logger.info(f"   🏷️ {len([f for f in invoice_data.extracted_fields if f.value])} champs extraits")
            self.logger.info(f"   📊 Score de confiance: {invoice_data.confidence_score:.2f}")
            
            # 4. Construction du résultat final
            result = {
                'success': True,
                'processing_time': time.time() - start_time,
                'ocr_confidence': base_result.confidence,
                'extraction_confidence': invoice_data.confidence_score,
                
                # Données structurées de la facture
                'invoice_data': {
                    'supplier': {
                        'name': invoice_data.supplier_name,
                        'address': invoice_data.supplier_address,
                        'siret': invoice_data.supplier_siret,
                        'vat_number': invoice_data.supplier_vat,
                        'email': invoice_data.supplier_email,
                        'phone': invoice_data.supplier_phone
                    },
                    'client': {
                        'name': invoice_data.client_name,
                        'address': invoice_data.client_address,
                        'billing_address': invoice_data.billing_address,
                        'delivery_address': invoice_data.delivery_address
                    },
                    'references': {
                        'invoice_number': invoice_data.invoice_number,
                        'invoice_date': invoice_data.invoice_date,
                        'due_date': invoice_data.due_date,
                        'order_number': invoice_data.order_number,
                        'client_reference': invoice_data.client_reference
                    },
                    'amounts': {
                        'subtotal_ht': invoice_data.subtotal_ht,
                        'vat_amount': invoice_data.vat_amount,
                        'total_ttc': invoice_data.total_ttc,
                        'vat_rates': invoice_data.vat_rates
                    }
                },
                
                # Métadonnées techniques
                'regions_detected': len(regions),
                'fields_extracted': len(invoice_data.extracted_fields),
                'raw_text': base_result.text[:500] + "..." if len(base_result.text) > 500 else base_result.text
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement intelligent: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _extract_detailed_ocr_data(self, file_path: Path) -> Dict:
        """Extraction des données OCR détaillées avec coordonnées"""
        import pytesseract
        from PIL import Image
        import pdf2image
        
        try:
            # Conversion du fichier en image si nécessaire
            if file_path.suffix.lower() == '.pdf':
                pages = pdf2image.convert_from_path(file_path, dpi=300)
                image = pages[0] if pages else None
            else:
                image = Image.open(file_path)
            
            if not image:
                return {}
            
            # OCR avec données de position
            ocr_data = pytesseract.image_to_data(
                image,
                lang='+'.join(self.config.get('languages', ['fra', 'eng'])),
                config="--oem 3 --psm 6",
                output_type=pytesseract.Output.DICT
            )
            
            return ocr_data
            
        except Exception as e:
            self.logger.warning(f"⚠️ Impossible d'extraire les données OCR détaillées: {e}")
            return {}
    
    def get_supported_fields(self) -> Dict[str, List[str]]:
        """Liste des champs supportés par catégorie"""
        return {
            'supplier': [
                'name', 'address', 'siret', 'vat_number', 'email', 'phone'
            ],
            'client': [
                'name', 'address', 'billing_address', 'delivery_address'
            ],
            'references': [
                'invoice_number', 'invoice_date', 'due_date', 'order_number', 'client_reference'
            ],
            'amounts': [
                'subtotal_ht', 'vat_amount', 'total_ttc', 'vat_rates'
            ]
        }


# Fonction d'enregistrement pour le ModuleRegistry
def register_intelligent_invoice_ocr(registry):
    """Enregistrement du module OCR intelligent"""
    config_schema = {
        "languages": {
            "type": "list",
            "options": ["fra", "eng", "deu", "esp", "ita"],
            "default": ["fra", "eng"],
            "description": "Langues pour la reconnaissance OCR"
        },
        "confidence_threshold": {
            "type": "float",
            "range": [0.5, 1.0],
            "default": 0.7,
            "description": "Seuil minimum de confiance OCR"
        },
        "preprocessing": {
            "type": "list",
            "options": ["deskew", "denoise", "contrast", "sharpen"],
            "default": ["contrast", "denoise", "deskew"],
            "description": "Options de préprocessing des images"
        },
        "extract_layout": {
            "type": "boolean",
            "default": True,
            "description": "Analyse intelligente du layout"
        },
        "universal_extraction": {
            "type": "boolean", 
            "default": True,
            "description": "Extraction universelle de champs"
        }
    }
    
    registry.register_module("intelligent_invoice_ocr", IntelligentInvoiceOCR, config_schema)
    print("✅ Module OCR Intelligent pour factures enregistré")

