# modules/ocr/layout_detector.py
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class LayoutType(Enum):
    HEADER = "header"
    SUPPLIER = "supplier"
    CLIENT = "client"
    REFERENCES = "references"
    ITEMS = "items"
    TOTALS = "totals"
    FOOTER = "footer"

@dataclass
class TextRegion:
    text: str
    coordinates: Tuple[int, int, int, int]  # x, y, width, height
    layout_type: LayoutType
    confidence: float

class IntelligentLayoutDetector:
    """Détecteur intelligent de layout pour factures universelles"""
    
    def __init__(self):
        self.layout_patterns = self._load_layout_patterns()
        
    def _load_layout_patterns(self) -> Dict[LayoutType, List[re.Pattern]]:
        """Patterns pour détecter les différentes sections d'une facture"""
        return {
            LayoutType.HEADER: [
                re.compile(r'facture|invoice|bill|nota|rechnung', re.IGNORECASE),
                re.compile(r'n°\s*(?:facture|invoice|bill)', re.IGNORECASE)
            ],
            LayoutType.SUPPLIER: [
                re.compile(r'(?:expéditeur|vendeur|fournisseur|from|seller)', re.IGNORECASE),
                re.compile(r'siret|siren|tva|vat|rcs', re.IGNORECASE)
            ],
            LayoutType.CLIENT: [
                re.compile(r'(?:destinataire|client|acheteur|to|buyer|ship\s+to|bill\s+to)', re.IGNORECASE),
                re.compile(r'adresse\s+(?:de\s+)?(?:facturation|livraison)', re.IGNORECASE)
            ],
            LayoutType.REFERENCES: [
                re.compile(r'(?:référence|ref|commande|order|date)', re.IGNORECASE),
                re.compile(r'échéance|due\s+date|payment', re.IGNORECASE)
            ],
            LayoutType.TOTALS: [
                re.compile(r'(?:total|montant|amount|sum|price)', re.IGNORECASE),
                re.compile(r'(?:ht|ttc|vat|tax|net|gross)', re.IGNORECASE)
            ]
        }
    
    def analyze_layout(self, ocr_data: Dict) -> List[TextRegion]:
        """Analyse intelligente du layout de la facture"""
        regions = []
        
        if not ocr_data or 'text' not in ocr_data:
            return regions
        
        # Reconstruction des blocs de texte avec position
        text_blocks = self._create_text_blocks(ocr_data)
        
        # Classification de chaque bloc
        for block in text_blocks:
            layout_type = self._classify_text_block(block['text'])
            
            region = TextRegion(
                text=block['text'],
                coordinates=block['coordinates'],
                layout_type=layout_type,
                confidence=block['confidence']
            )
            regions.append(region)
        
        return self._post_process_regions(regions)
    
    def _create_text_blocks(self, ocr_data: Dict) -> List[Dict]:
        """Crée des blocs de texte cohérents à partir des données OCR"""
        # Regroupement par ligne basé sur la position verticale
        lines = []
        current_line = []
        last_top = -1
        line_threshold = 15  # Seuil pour regrouper sur la même ligne
        
        for i, word in enumerate(ocr_data['text']):
            if not word.strip():
                continue
                
            top = ocr_data.get('top', [0] * len(ocr_data['text']))[i]
            left = ocr_data.get('left', [0] * len(ocr_data['text']))[i]
            width = ocr_data.get('width', [0] * len(ocr_data['text']))[i]
            height = ocr_data.get('height', [0] * len(ocr_data['text']))[i]
            conf = int(ocr_data.get('conf', [0] * len(ocr_data['text']))[i])
            
            if last_top == -1 or abs(top - last_top) <= line_threshold:
                current_line.append({
                    'word': word,
                    'left': left,
                    'top': top,
                    'width': width,
                    'height': height,
                    'conf': conf
                })
            else:
                if current_line:
                    lines.append(current_line)
                current_line = [{
                    'word': word,
                    'left': left,
                    'top': top,
                    'width': width,
                    'height': height,
                    'conf': conf
                }]
            
            last_top = top
        
        if current_line:
            lines.append(current_line)
        
        # Conversion des lignes en blocs de texte
        text_blocks = []
        for line in lines:
            if not line:
                continue
                
            # Tri des mots par position horizontale
            line.sort(key=lambda x: x['left'])
            
            # Assemblage du texte de la ligne
            line_text = ' '.join(word['word'] for word in line)
            
            # Calcul des coordonnées du bloc
            min_left = min(word['left'] for word in line)
            min_top = min(word['top'] for word in line)
            max_right = max(word['left'] + word['width'] for word in line)
            max_bottom = max(word['top'] + word['height'] for word in line)
            
            # Confiance moyenne
            avg_conf = sum(word['conf'] for word in line) / len(line)
            
            text_blocks.append({
                'text': line_text,
                'coordinates': (min_left, min_top, max_right - min_left, max_bottom - min_top),
                'confidence': avg_conf / 100.0
            })
        
        return text_blocks
    
    def _classify_text_block(self, text: str) -> LayoutType:
        """Classification intelligente d'un bloc de texte"""
        text_lower = text.lower()
        
        # Score par type de layout
        scores = {layout_type: 0 for layout_type in LayoutType}
        
        for layout_type, patterns in self.layout_patterns.items():
            for pattern in patterns:
                matches = len(pattern.findall(text))
                scores[layout_type] += matches * 0.3
        
        # Heuristiques supplémentaires
        if re.search(r'\d+[,\.]\d{2}\s*€', text):
            scores[LayoutType.TOTALS] += 0.4
        
        if re.search(r'\d{14}', text):  # SIRET
            scores[LayoutType.SUPPLIER] += 0.3
        
        if re.search(r'\d{5}\s+[A-Z]', text):  # Code postal + ville
            scores[LayoutType.CLIENT] += 0.2
        
        # Retourne le type avec le meilleur score
        best_type = max(scores.items(), key=lambda x: x[1])
        return best_type[0] if best_type[1] > 0.1 else LayoutType.HEADER
    
    def _post_process_regions(self, regions: List[TextRegion]) -> List[TextRegion]:
        """Post-traitement des régions détectées"""
        # Tri par position verticale (haut vers bas)
        regions.sort(key=lambda r: r.coordinates[1])
        
        # Regroupement des régions adjacentes du même type
        merged_regions = []
        current_group = []
        current_type = None
        
        for region in regions:
            if region.layout_type == current_type:
                current_group.append(region)
            else:
                if current_group:
                    merged_regions.append(self._merge_region_group(current_group))
                current_group = [region]
                current_type = region.layout_type
        
        if current_group:
            merged_regions.append(self._merge_region_group(current_group))
        
        return merged_regions
    
    def _merge_region_group(self, group: List[TextRegion]) -> TextRegion:
        """Fusion d'un groupe de régions du même type"""
        if len(group) == 1:
            return group[0]
        
        # Assemblage du texte
        combined_text = '\n'.join(region.text for region in group)
        
        # Calcul des coordonnées englobantes
        min_x = min(region.coordinates[0] for region in group)
        min_y = min(region.coordinates[1] for region in group)
        max_x = max(region.coordinates[0] + region.coordinates[2] for region in group)
        max_y = max(region.coordinates[1] + region.coordinates[3] for region in group)
        
        # Confiance moyenne
        avg_confidence = sum(region.confidence for region in group) / len(group)
        
        return TextRegion(
            text=combined_text,
            coordinates=(min_x, min_y, max_x - min_x, max_y - min_y),
            layout_type=group[0].layout_type,
            confidence=avg_confidence
        )

