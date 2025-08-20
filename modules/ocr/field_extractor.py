# modules/ocr/field_extractor.py
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .layout_detector import TextRegion, LayoutType

@dataclass
class InvoiceField:
    """Champ d'une facture avec métadonnées"""
    name: str
    value: Any
    confidence: float
    source_region: Optional[LayoutType] = None
    raw_text: str = ""
    coordinates: Optional[tuple] = None

@dataclass 
class InvoiceData:
    """Structure complète des données d'une facture"""
    # Informations fournisseur
    supplier_name: Optional[str] = None
    supplier_address: Optional[str] = None
    supplier_siret: Optional[str] = None
    supplier_vat: Optional[str] = None
    supplier_email: Optional[str] = None
    supplier_phone: Optional[str] = None
    
    # Informations client
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
    
    # Références et dates
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    order_number: Optional[str] = None
    client_reference: Optional[str] = None
    
    # Montants
    subtotal_ht: Optional[float] = None
    vat_amount: Optional[float] = None
    total_ttc: Optional[float] = None
    vat_rates: List[float] = field(default_factory=list)
    
    # Métadonnées
    extracted_fields: List[InvoiceField] = field(default_factory=list)
    confidence_score: float = 0.0

class UniversalFieldExtractor:
    """Extracteur intelligent de champs pour factures universelles"""
    
    def __init__(self):
        self.field_patterns = self._load_field_patterns()
        
    def _load_field_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Patterns universels pour extraction de champs"""
        return {
            # === FOURNISSEUR ===
            'supplier_name': [
                re.compile(r'^([A-Z][A-Z\s&\.]{2,50})(?:\n|\s{3,})', re.MULTILINE),
                re.compile(r'(?:société|company|enterprise)[:\s]*([A-Z][A-Za-z\s&\.]{2,50})', re.IGNORECASE)
            ],
            
            'supplier_siret': [
                re.compile(r'(?:siret|siren)[:\s]*(\d{9,14})', re.IGNORECASE),
                re.compile(r'\b(\d{14})\b')  # SIRET exact
            ],
            
            'supplier_vat': [
                re.compile(r'(?:tva|vat|btw)[:\s]*([A-Z]{2}[A-Z0-9]{9,13})', re.IGNORECASE),
                re.compile(r'\b([A-Z]{2}[A-Z0-9]{9,13})\b')
            ],
            
            'supplier_email': [
                re.compile(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b')
            ],
            
            'supplier_phone': [
                re.compile(r'(?:tél|tel|phone)[:\s]*(\+?[\d\s\-\.()]{8,15})', re.IGNORECASE),
                re.compile(r'(\+33\s?[\d\s\-\.]{8,12})')  # Français
            ],
            
            # === CLIENT ===
            'client_name': [
                re.compile(r'(?:à|to|pour|for)[:\s]*([A-Z][A-Z\s&\.]{2,50})', re.IGNORECASE),
                re.compile(r'(?:client|customer)[:\s]*([A-Z][A-Za-z\s&\.]{2,50})', re.IGNORECASE)
            ],
            
            # === RÉFÉRENCES ===
            'invoice_number': [
                re.compile(r'(?:facture|invoice|bill|nota)[:\s#n°]*([A-Z0-9\-]{3,25})', re.IGNORECASE),
                re.compile(r'(?:n°|num|number)[:\s]*([A-Z0-9\-]{3,25})', re.IGNORECASE)
            ],
            
            'invoice_date': [
                re.compile(r'(?:date[:\s]*|du[:\s]*|le[:\s]*)(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})', re.IGNORECASE),
                re.compile(r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})', re.IGNORECASE)
            ],
            
            'due_date': [
                re.compile(r'(?:échéance|due\s+date|payment\s+due)[:\s]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})', re.IGNORECASE)
            ],
            
            'order_number': [
                re.compile(r'(?:commande|order|po)[:\s#n°]*([A-Z0-9\-]{3,25})', re.IGNORECASE)
            ],
            
            # === MONTANTS ===
            'amounts_eur': [
                re.compile(r'(\d{1,6}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.MULTILINE),
                re.compile(r'€\s*(\d{1,6}(?:[,\.]\d{3})*[,\.]\d{2})', re.MULTILINE)
            ],
            
            'total_ttc': [
                re.compile(r'(?:total|montant\s+total|grand\s+total|ttc)[:\s]*(\d{1,6}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.IGNORECASE),
                re.compile(r'(?:à\s+payer|to\s+pay)[:\s]*(\d{1,6}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.IGNORECASE)
            ],
            
            'subtotal_ht': [
                re.compile(r'(?:sous.total|subtotal|ht)[:\s]*(\d{1,6}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.IGNORECASE)
            ],
            
            'vat_amount': [
                re.compile(r'(?:tva|vat|tax)[:\s]*(\d{1,6}(?:[,\.]\d{3})*[,\.]\d{2})\s*€?', re.IGNORECASE)
            ],
            
            'vat_rate': [
                re.compile(r'(?:tva|vat)[:\s]*(\d{1,2}(?:[,\.]\d+)?)\s*%', re.IGNORECASE)
            ]
        }
    
    def extract_fields(self, regions: List[TextRegion]) -> InvoiceData:
        """Extraction intelligente de tous les champs"""
        invoice = InvoiceData()
        all_text = '\n'.join(region.text for region in regions)
        
        # Extraction par région pour plus de précision
        for region in regions:
            region_fields = self._extract_from_region(region)
            invoice.extracted_fields.extend(region_fields)
        
        # Consolidation des champs extraits
        invoice = self._consolidate_fields(invoice, all_text)
        
        # Calcul du score de confiance global
        invoice.confidence_score = self._calculate_confidence(invoice)
        
        return invoice
    
    def _extract_from_region(self, region: TextRegion) -> List[InvoiceField]:
        """Extraction de champs depuis une région spécifique"""
        fields = []
        
        # Sélection des patterns selon le type de région
        relevant_patterns = self._get_patterns_for_region(region.layout_type)
        
        for field_name, patterns in relevant_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(region.text)
                
                for match in matches:
                    # Nettoyage de la correspondance
                    if isinstance(match, tuple):
                        value = ' '.join(filter(None, match))
                    else:
                        value = match
                    
                    if value and value.strip():
                        field = InvoiceField(
                            name=field_name,
                            value=value.strip(),
                            confidence=region.confidence,
                            source_region=region.layout_type,
                            raw_text=region.text,
                            coordinates=region.coordinates
                        )
                        fields.append(field)
        
        return fields
    
    def _get_patterns_for_region(self, layout_type: LayoutType) -> Dict[str, List[re.Pattern]]:
        """Patterns pertinents selon le type de région"""
        if layout_type == LayoutType.SUPPLIER:
            return {k: v for k, v in self.field_patterns.items() 
                   if k.startswith('supplier_')}
        
        elif layout_type == LayoutType.CLIENT:
            return {k: v for k, v in self.field_patterns.items() 
                   if k.startswith('client_')}
        
        elif layout_type == LayoutType.REFERENCES:
            return {k: v for k, v in self.field_patterns.items() 
                   if k in ['invoice_number', 'invoice_date', 'due_date', 'order_number']}
        
        elif layout_type == LayoutType.TOTALS:
            return {k: v for k, v in self.field_patterns.items() 
                   if k in ['amounts_eur', 'total_ttc', 'subtotal_ht', 'vat_amount', 'vat_rate']}
        
        else:
            # Pour les régions non classifiées, utiliser tous les patterns
            return self.field_patterns
    
    def _consolidate_fields(self, invoice: InvoiceData, full_text: str) -> InvoiceData:
        """Consolidation et déduplication des champs extraits"""
        # Regroupement par nom de champ
        fields_by_name = {}
        for field in invoice.extracted_fields:
            if field.name not in fields_by_name:
                fields_by_name[field.name] = []
            fields_by_name[field.name].append(field)
        
        # Sélection de la meilleure valeur pour chaque champ
        for field_name, field_list in fields_by_name.items():
            best_field = self._select_best_field(field_list)
            
            # Attribution à l'objet invoice
            if hasattr(invoice, field_name):
                setattr(invoice, field_name, self._parse_field_value(best_field))
        
        # Post-traitement spécialisé
        invoice = self._post_process_amounts(invoice, full_text)
        invoice = self._extract_addresses(invoice, full_text)
        
        return invoice
    
    def _select_best_field(self, fields: List[InvoiceField]) -> InvoiceField:
        """Sélection du meilleur champ parmi plusieurs candidats"""
        if len(fields) == 1:
            return fields[0]
        
        # Tri par confiance et spécificité de la région source
        region_priority = {
            LayoutType.SUPPLIER: 3,
            LayoutType.CLIENT: 3,
            LayoutType.REFERENCES: 2,
            LayoutType.TOTALS: 2,
            LayoutType.HEADER: 1
        }
        
        scored_fields = []
        for field in fields:
            score = field.confidence
            if field.source_region:
                score += region_priority.get(field.source_region, 0) * 0.1
            scored_fields.append((score, field))
        
        # Retourne le champ avec le meilleur score
        return max(scored_fields, key=lambda x: x[0])[1]
    
    def _parse_field_value(self, field: InvoiceField) -> Any:
        """Parse la valeur selon le type de champ"""
        value = field.value
        
        # Montants : conversion en float
        if 'amount' in field.name or 'total' in field.name or field.name.endswith('_ht'):
            try:
                # Nettoyage et conversion
                clean_value = re.sub(r'[€\s]', '', value).replace(',', '.')
                return float(clean_value)
            except:
                return None
        
        # Taux : conversion en float
        if 'rate' in field.name:
            try:
                return float(value.replace(',', '.'))
            except:
                return None
        
        # Autres : string nettoyée
        return value.strip()
    
    def _post_process_amounts(self, invoice: InvoiceData, full_text: str) -> InvoiceData:
        """Post-traitement intelligent des montants"""
        # Extraction de tous les montants trouvés
        amount_fields = [f for f in invoice.extracted_fields if 'amount' in f.name or 'total' in f.name]
        
        if amount_fields:
            amounts = []
            for field in amount_fields:
                try:
                    value = self._parse_field_value(field)
                    if value and isinstance(value, (int, float)):
                        amounts.append(value)
                except:
                    continue
            
            if amounts:
                amounts.sort(reverse=True)
                # Le montant le plus élevé est généralement le total TTC
                if not invoice.total_ttc and amounts:
                    invoice.total_ttc = amounts[0]
        
        return invoice
    
    def _extract_addresses(self, invoice: InvoiceData, full_text: str) -> InvoiceData:
        """Extraction intelligente des adresses complètes"""
        # Pattern pour adresses françaises complètes
        address_pattern = re.compile(
            r'([A-Z][A-Z\s&\.]{2,50})\s*\n\s*'  # Nom/société
            r'(\d+(?:\s+[A-Za-z\s]+)*)\s*\n\s*'  # Adresse
            r'(\d{5})\s+([A-Za-z\s\-]+)',  # Code postal + ville
            re.MULTILINE
        )
        
        addresses = address_pattern.findall(full_text)
        
        if addresses:
            # Première adresse = fournisseur (généralement en haut)
            if not invoice.supplier_name and len(addresses) > 0:
                supplier_addr = addresses[0]
                invoice.supplier_name = supplier_addr[0].strip()
                invoice.supplier_address = f"{supplier_addr[1].strip()}, {supplier_addr[2]} {supplier_addr[3].strip()}"
            
            # Deuxième adresse = client
            if not invoice.client_name and len(addresses) > 1:
                client_addr = addresses[1]
                invoice.client_name = client_addr[0].strip()
                invoice.client_address = f"{client_addr[1].strip()}, {client_addr[2]} {client_addr[3].strip()}"
        
        return invoice
    
    def _calculate_confidence(self, invoice: InvoiceData) -> float:
        """Calcul du score de confiance global"""
        # Champs critiques pour une facture
        critical_fields = [
            'supplier_name', 'invoice_number', 'total_ttc', 'invoice_date'
        ]
        
        found_critical = sum(1 for field in critical_fields 
                           if getattr(invoice, field) is not None)
        
        # Score de base selon les champs critiques trouvés
        base_score = found_critical / len(critical_fields)
        
        # Bonus pour champs supplémentaires
        optional_fields = [
            'supplier_vat', 'client_name', 'subtotal_ht', 'vat_amount'
        ]
        
        found_optional = sum(1 for field in optional_fields 
                           if getattr(invoice, field) is not None)
        
        optional_bonus = (found_optional / len(optional_fields)) * 0.3
        
        return min(base_score + optional_bonus, 1.0)

