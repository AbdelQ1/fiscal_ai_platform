# modules/ocr/document_handlers/fiscal_handler.py
import re
from typing import Dict
from .base_handler import DocumentHandler

class FiscalHandler(DocumentHandler):
    """Gestionnaire spécialisé pour documents fiscaux officiels"""
    
    def __init__(self):
        super().__init__(
            document_type="fiscal",
            supported_extensions=['.pdf', '.png', '.jpg', '.jpeg'],
            confidence_threshold=0.75,
            preprocessing_options=['contrast', 'denoise', 'deskew', 'sharpen']
        )
    
    def get_patterns(self) -> Dict[str, re.Pattern]:
        """Patterns spécialisés documents fiscaux"""
        return {
            # Identifiants fiscaux
            'siret': re.compile(r'\b\d{14}\b'),
            'siren': re.compile(r'\b\d{9}\b'),
            'tva_number': re.compile(r'FR[A-Z0-9]{2}\s?\d{9}'),
            'numero_fiscal': re.compile(r'(?:numéro\s+fiscal|n°\s+fiscal)[:\s]*(\d{10,15})', re.IGNORECASE),
            
            # Montants fiscaux
            'montant_euro': re.compile(r'\d{1,3}(?:[,\.\s]\d{3})*[,\.]\d{2}\s*€?'),
            'impot_du': re.compile(r'(?:impôt\s+dû|impôt\s+sur\s+le\s+revenu)[:\s]*(\d{1,3}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.IGNORECASE),
            'revenus_declares': re.compile(r'(?:revenus?\s+déclarés?)[:\s]*(\d{1,3}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.IGNORECASE),
            
            # Dates fiscales
            'date_avis': re.compile(r'(?:date\s+avis|établi\s+le)[:\s]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})', re.IGNORECASE),
            'date_limite': re.compile(r'(?:date\s+limite|à\s+payer\s+avant)[:\s]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4})', re.IGNORECASE),
            
            # Codes et références fiscales
            'code_commune': re.compile(r'(?:commune|code\s+commune)[:\s]*(\d{3,5})', re.IGNORECASE),
            'reference_avis': re.compile(r'(?:référence\s+avis|avis\s+n°)[:\s]*([A-Z0-9]+)', re.IGNORECASE),
            
            # Taxe foncière spécifique
            'valeur_locative': re.compile(r'(?:valeur\s+locative)[:\s]*(\d{1,3}(?:[,\.]\d{3})*[,\.]\d{2})', re.IGNORECASE),
            'taxe_communale': re.compile(r'(?:taxe\s+communale)[:\s]*(\d{1,3}(?:[,\.]\d{3})*[,\.]\d{2})', re.IGNORECASE),
            
            # Adresse fiscale
            'adresse_fiscale': re.compile(r'([A-Z][A-Z\s]+)\s+(\d+\s+[A-Za-z\s]+)\s+(\d{5})\s+([A-Z\s]+)', re.MULTILINE),
        }
    
    def get_tesseract_config(self) -> str:
        """Configuration Tesseract pour documents fiscaux"""
        # Configuration stricte pour documents officiels
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        chars += "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"
        chars += "€%.,()-/°N°: "
        
        return f"--oem 3 --psm 6 -c tessedit_char_whitelist={chars}"
    
    def postprocess_entities(self, entities: Dict, text: str) -> Dict:
        """Post-traitement spécialisé documents fiscaux"""
        # Classification du type de document fiscal
        text_lower = text.lower()
        
        if 'avis d\'imposition' in text_lower or 'impôt sur le revenu' in text_lower:
            entities['type_document_fiscal'] = ['avis_imposition']
        elif 'taxe foncière' in text_lower:
            entities['type_document_fiscal'] = ['taxe_fonciere']
        elif 'declaration' in text_lower:
            entities['type_document_fiscal'] = ['declaration_fiscale']
        
        # Validation des identifiants fiscaux
        if 'siret' in entities:
            # Validation longueur SIRET
            entities['siret'] = [s for s in entities['siret'] if len(s) == 14]
        
        if 'siren' in entities:
            # Validation longueur SIREN
            entities['siren'] = [s for s in entities['siren'] if len(s) == 9]
        
        return entities
    
    def validate_document(self, text: str) -> float:
        """Score de validation pour document fiscal"""
        score = 0.0
        text_lower = text.lower()
        
        # Mots-clés fiscaux officiels
        fiscal_keywords = ['impôt', 'fiscal', 'taxe', 'avis', 'déclaration', 'revenus', 'siret']
        score += sum(0.12 for keyword in fiscal_keywords if keyword in text_lower)
        
        # Organismes officiels
        official_orgs = ['dgfip', 'service public', 'république française', 'trésor public']
        score += sum(0.2 for org in official_orgs if org in text_lower)
        
        # Numéros fiscaux
        if re.search(r'FR[A-Z0-9]{11}', text):
            score += 0.15
        
        return min(score, 1.0)

