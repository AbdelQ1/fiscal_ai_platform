# modules/ocr/modular_ocr.py
import logging
from typing import Dict, List, Optional, Type
from pathlib import Path
import time

from .base_ocr import OCRResult
from .document_handlers.base_handler import DocumentHandler
from .document_handlers.invoice_handler import InvoiceHandler
from .document_handlers.fiscal_handler import FiscalHandler

class ModularOCRProcessor:
    """Processeur OCR modulaire et dynamique"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration générale
        self.languages = config.get('languages', ['fra', 'eng'])
        self.lang_string = '+'.join(self.languages)
        self.auto_detect = config.get('auto_detect', True)
        
        # Enregistrement des handlers disponibles
        self.handlers: Dict[str, DocumentHandler] = {}
        self._register_default_handlers()
        
        self.logger.info(f"🔧 Processeur OCR modulaire initialisé")
        self.logger.info(f"   - Langues: {self.languages}")
        self.logger.info(f"   - Auto-détection: {self.auto_detect}")
        self.logger.info(f"   - Handlers: {list(self.handlers.keys())}")
    
    def _register_default_handlers(self):
        """Enregistrement des handlers par défaut"""
        self.register_handler('invoice', InvoiceHandler())
        self.register_handler('fiscal', FiscalHandler())
        # Ajout automatique d'autres handlers ici
    
    def register_handler(self, name: str, handler: DocumentHandler):
        """Enregistrement dynamique d'un nouveau handler"""
        self.handlers[name] = handler
        self.logger.info(f"📋 Handler '{name}' enregistré pour type: {handler.document_type}")
    
    def detect_document_type(self, text: str, filename: str) -> str:
        """Détection automatique du type de document"""
        if not self.auto_detect:
            return 'generic'
        
        scores = {}
        
        # Score basé sur le nom du fichier
        filename_lower = filename.lower()
        for handler_name, handler in self.handlers.items():
            file_score = 0
            if handler.document_type in filename_lower:
                file_score = 0.3
            elif 'facture' in filename_lower and handler.document_type == 'invoice':
                file_score = 0.3
            elif any(word in filename_lower for word in ['impot', 'fiscal', 'taxe']) and handler.document_type == 'fiscal':
                file_score = 0.3
            
            scores[handler_name] = file_score
        
        # Score basé sur le contenu
        for handler_name, handler in self.handlers.items():
            content_score = handler.validate_document(text)
            scores[handler_name] = scores.get(handler_name, 0) + content_score
        
        # Sélection du meilleur handler
        if scores:
            best_handler = max(scores.items(), key=lambda x: x[1])
            if best_handler[1] > 0.4:  # Seuil de confiance
                self.logger.info(f"🎯 Type détecté: {best_handler[0]} (score: {best_handler[1]:.2f})")
                return best_handler[0]
        
        self.logger.info("🎯 Type générique sélectionné")
        return 'generic'
    
    def process_document(self, file_path: Path, document_type: Optional[str] = None) -> OCRResult:
        """Traitement modulaire d'un document"""
        start_time = time.time()
        
        try:
            # Lecture OCR de base (réutilise la logique existante)
            from .base_ocr import FiscalOCRModule
            
            # Configuration temporaire pour OCR de base
            base_config = {
                "languages": self.languages,
                "confidence_threshold": self.config.get('confidence_threshold', 0.7),
                "preprocessing": self.config.get('preprocessing', ['contrast', 'denoise']),
                "fiscal_mode": False  # Désactivé car on gère manuellement
            }
            
            base_ocr = FiscalOCRModule(base_config)
            
            # OCR de base pour extraire le texte
            base_result = base_ocr.process_document(file_path, "generic")
            
            if not base_result.success:
                return base_result
            
            # Détection du type de document si non spécifié
            if document_type is None or document_type == 'auto':
                document_type = self.detect_document_type(base_result.text, file_path.name)
            
            # Sélection du handler approprié
            handler = self.handlers.get(document_type)
            if not handler:
                self.logger.warning(f"⚠️ Handler '{document_type}' non trouvé, utilisation générique")
                # Retour du résultat de base
                return base_result
            
            # Traitement spécialisé avec le handler
            patterns = handler.get_patterns()
            entities = self._extract_entities_with_patterns(base_result.text, patterns)
            entities = handler.postprocess_entities(entities, base_result.text)
            
            # Construction du résultat final
            final_result = OCRResult(
                text=base_result.text,
                confidence=base_result.confidence,
                word_count=base_result.word_count,
                processing_time=time.time() - start_time,
                preprocessing_applied=base_result.preprocessing_applied,
                page_count=base_result.page_count,
                detected_language=base_result.detected_language,
                extracted_entities=entities,
                success=True
            )
            
            # Ajout métadonnées spécialisées
            final_result.document_type_detected = document_type
            final_result.handler_used = type(handler).__name__
            
            self.logger.info(f"✅ Document traité avec handler '{document_type}' - {len(entities)} entités")
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement modulaire: {str(e)}")
            return OCRResult(
                text="", confidence=0.0, word_count=0,
                processing_time=time.time() - start_time,
                preprocessing_applied=[], success=False,
                error_message=str(e)
            )
    
    def _extract_entities_with_patterns(self, text: str, patterns: Dict) -> Dict:
        """Extraction d'entités avec patterns personnalisés"""
        entities = {}
        
        for entity_name, pattern in patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Nettoyage des matches
                clean_matches = []
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else (match[1] if len(match) > 1 else "")
                    if match and match.strip():
                        clean_matches.append(match.strip())
                
                if clean_matches:
                    entities[entity_name] = list(set(clean_matches))
                    self.logger.debug(f"   🏷️ {entity_name}: {len(clean_matches)} trouvé(s)")
        
        return entities
    
    def get_available_handlers(self) -> Dict[str, Dict]:
        """Informations sur les handlers disponibles"""
        return {
            name: {
                'document_type': handler.document_type,
                'supported_extensions': handler.supported_extensions,
                'confidence_threshold': handler.confidence_threshold,
                'preprocessing_options': handler.preprocessing_options,
                'patterns_count': len(handler.get_patterns())
            }
            for name, handler in self.handlers.items()
        }


def register_modular_ocr(registry):
    """Enregistrement du module OCR modulaire"""
    config_schema = {
        "languages": {
            "type": "list",
            "options": ["fra", "eng", "deu", "esp", "ita"],
            "default": ["fra", "eng"]
        },
        "confidence_threshold": {
            "type": "float",
            "range": [0.5, 1.0],
            "default": 0.7
        },
        "preprocessing": {
            "type": "list",
            "options": ["deskew", "denoise", "contrast", "sharpen"],
            "default": ["contrast", "denoise", "deskew"]
        },
        "auto_detect": {
            "type": "boolean",
            "default": True,
            "description": "Détection automatique du type de document"
        }
    }
    
    registry.register_module("modular_ocr", ModularOCRProcessor, config_schema)
    print("✅ Module OCR modulaire enregistré")

