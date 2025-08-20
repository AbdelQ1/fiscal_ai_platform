# modules/ocr/document_handlers/invoice_handler.py
import re
from typing import Dict, List
from .base_handler import DocumentHandler

class InvoiceHandler(DocumentHandler):
    """Gestionnaire spécialisé pour factures commerciales"""
    
    def __init__(self):
        super().__init__(
            document_type="invoice",
            supported_extensions=['.pdf', '.png', '.jpg', '.jpeg'],
            confidence_threshold=0.70,
            preprocessing_options=['contrast', 'denoise', 'deskew']
        )
    
    def get_patterns(self) -> Dict[str, re.Pattern]:
        """Patterns spécialisés factures commerciales"""
        return {
            # Montants
            'montant_euro': re.compile(r'(?:\d{1,3}(?:[,\.\s]\d{3})*[,\.]\d{2})\s*€?'),
            'montant_total': re.compile(r'(?:total|à\s+payer|grand\s+total)[:\s]*(\d{1,3}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.IGNORECASE),
            'montant_ht': re.compile(r'(?:ht|hors\s+taxe)[:\s]*(\d{1,3}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.IGNORECASE),
            'montant_ttc': re.compile(r'(?:ttc|toutes?\s+taxes?)[:\s]*(\d{1,3}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.IGNORECASE),
            
            # Références
            'numero_facture': re.compile(r'(?:facture|invoice)[:\s#n°]*([A-Z0-9\-]{3,20})', re.IGNORECASE),
            'numero_commande': re.compile(r'(?:commande|order)[:\s#n°]*([A-Z0-9\-]{3,20})', re.IGNORECASE),
            
            # Dates
            'date_facture': re.compile(r'(?:date\s+facture|invoice\s+date)[:\s]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})', re.IGNORECASE),
            'date_echeance': re.compile(r'(?:échéance|due\s+date)[:\s]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})', re.IGNORECASE),
            
            # Entreprise
            'tva_number': re.compile(r'(?:TVA|VAT)[:\s]*([A-Z]{2}[A-Z0-9]{9,13})', re.IGNORECASE),
            'siret': re.compile(r'\b\d{14}\b'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'telephone': re.compile(r'(?:tél|tel|phone)[:\s]*(\+?[\d\s\-\.]{8,15})', re.IGNORECASE),
            
            # Adresse
            'code_postal': re.compile(r'\b\d{5}\b'),
            'adresse_complete': re.compile(r'(\d+\s+[A-Za-z\s]+)\s+(\d{5})\s+([A-Za-z\s]+)', re.MULTILINE),
        }
    
    def get_tesseract_config(self) -> str:
        """Configuration Tesseract pour factures"""
        # Configuration permissive pour factures commerciales variées
        return "--oem 3 --psm 6"
    
    def postprocess_entities(self, entities: Dict, text: str) -> Dict:
        """Post-traitement spécialisé factures"""
        # Identification du montant total probable
        if 'montant_euro' in entities and len(entities['montant_euro']) > 1:
            try:
                amounts = []
                for amount_str in entities['montant_euro']:
                    clean_amount = re.sub(r'[€\s]', '', amount_str).replace(',', '.')
                    if clean_amount.replace('.', '').isdigit():
                        amounts.append((float(clean_amount), amount_str))
                
                if amounts:
                    amounts.sort(reverse=True)
                    entities['montant_total_probable'] = [amounts[0][1]]
            except Exception:
                pass
        
        # Validation numéros de facture
        if 'numero_facture' in entities:
            valid_numbers = [n for n in entities['numero_facture'] 
                           if len(n) >= 3 and n.lower() not in ['description', 'total']]
            entities['numero_facture'] = valid_numbers
        
        return entities
    
    def validate_document(self, text: str) -> float:
        """Score de validation pour facture"""
        score = 0.0
        text_lower = text.lower()
        
        # Mots-clés facture
        invoice_keywords = ['facture', 'invoice', 'bill', 'total', 'tva', 'ht', 'ttc']
        score += sum(0.15 for keyword in invoice_keywords if keyword in text_lower)
        
        # Patterns montants
        if re.search(r'\d+[,\.]\d{2}\s*€', text):
            score += 0.3
        
        # Numéro de facture
        if re.search(r'(?:facture|invoice)[:\s#n°]', text_lower):
            score += 0.2
        
        return min(score, 1.0)
