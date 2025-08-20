# debug_patterns_precise.py
#!/usr/bin/env python3
"""Debug précis pour identifier où les patterns échouent"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.ocr.configurable_invoice_ocr import ConfigurableInvoiceOCR

def debug_step_by_step():
    """Debug étape par étape avec votre facture Amazon"""
    
    config = {"languages": ["fra", "eng"], "confidence_threshold": 0.65}
    ocr = ConfigurableInvoiceOCR(config)
    
    invoice_path = Path("/Users/abdel/Documents/Facture Batterie Bosch.pdf")
    
    print("🔍 DEBUG PRÉCIS - ÉTAPE PAR ÉTAPE")
    print("=" * 70)
    
    # 1. Extraction du texte brut
    print("1️⃣ EXTRACTION TEXTE...")
    raw_text = ocr._extract_text_with_base_ocr(invoice_path)
    
    if not raw_text:
        print("❌ ARRÊT: Aucun texte extrait")
        return
    
    print(f"✅ Texte extrait: {len(raw_text)} caractères")
    print(f"📄 Aperçu (300 premiers chars):")
    print(f"'{raw_text[:300]}...'")
    
    # 2. Test direct des patterns un par un
    print(f"\n2️⃣ TEST DIRECT DES PATTERNS...")
    
    test_patterns = {
        'montants_euros': r'(\d{1,4}[,\.]\d{2})\s*€?',
        'total': r'(?:total|montant)[:\s]*(\d{1,4}[,\.]\d{2})\s*€?',
        'dates_fr': r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})',
        'tva_fr': r'(FR[A-Z0-9]{11})',
        'facture_num': r'(?:facture|invoice)[:\s#n°]*([A-Z0-9\-]{3,20})'
    }
    
    found_matches = {}
    
    for pattern_name, pattern_str in test_patterns.items():
        try:
            pattern = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
            matches = pattern.findall(raw_text)
            
            found_matches[pattern_name] = matches
            
            print(f"   {pattern_name}: {len(matches)} matches")
            if matches:
                for i, match in enumerate(matches[:3]):
                    if isinstance(match, tuple):
                        match_str = ' '.join(str(m) for m in match if m)
                    else:
                        match_str = str(match)
                    print(f"      {i+1}. '{match_str}'")
            else:
                print(f"      ❌ Aucun match")
                
        except Exception as e:
            print(f"      ❌ Erreur pattern {pattern_name}: {e}")
    
    # 3. Simulation du processus de mapping
    print(f"\n3️⃣ SIMULATION MAPPING DONNÉES...")
    
    # Simulation extraction montants
    if found_matches.get('montants_euros'):
        print(f"   💰 Montants trouvés: {found_matches['montants_euros']}")
        
        valid_amounts = []
        for amount_str in found_matches['montants_euros']:
            try:
                # Nettoyage
                clean_amount = str(amount_str).replace(',', '.').replace('€', '').strip()
                amount_value = float(clean_amount)
                
                if 0.01 <= amount_value <= 10000:
                    valid_amounts.append(amount_value)
                    print(f"      ✅ Montant valide: {amount_value}€")
                else:
                    print(f"      ❌ Montant hors limites: {amount_value}€")
                    
            except Exception as e:
                print(f"      ❌ Erreur conversion '{amount_str}': {e}")
        
        if valid_amounts:
            total_probable = max(valid_amounts)
            print(f"   🎯 MONTANT TOTAL PROBABLE: {total_probable}€")
        else:
            print(f"   ❌ Aucun montant valide après nettoyage")
    
    # Simulation extraction date
    if found_matches.get('dates_fr'):
        print(f"   📅 Dates trouvées: {found_matches['dates_fr']}")
        for date_tuple in found_matches['dates_fr']:
            if isinstance(date_tuple, tuple) and len(date_tuple) >= 3:
                date_str = f"{date_tuple[0]} {date_tuple[1]} {date_tuple[2]}"
                print(f"      ✅ Date formatée: '{date_str}'")
    
    # Simulation extraction TVA
    if found_matches.get('tva_fr'):
        print(f"   🏛️ TVA trouvées: {found_matches['tva_fr']}")
        for tva in found_matches['tva_fr']:
            print(f"      ✅ TVA valide: {tva}")
    
    # 4. Test de la méthode complète OCR
    print(f"\n4️⃣ TEST MÉTHODE COMPLÈTE OCR...")
    
    try:
        result = ocr.process_invoice(invoice_path)
        
        print(f"   Succès: {result.success}")
        print(f"   Patterns matched: {result.patterns_matched}")
        print(f"   Confiance: {result.extraction_confidence}")
        
        if result.extracted_entities:
            print(f"   Entités extraites: {len(result.extracted_entities)}")
            for key, value in result.extracted_entities.items():
                print(f"      {key}: {value}")
        else:
            print(f"   ❌ Aucune entité dans extracted_entities")
            
    except Exception as e:
        print(f"   ❌ Erreur méthode complète: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n📊 CONCLUSIONS DU DEBUG:")
    print(f"   - Texte extrait: {'✅' if raw_text else '❌'}")
    print(f"   - Patterns qui matchent: {sum(1 for matches in found_matches.values() if matches)}/5")
    print(f"   - Mapping fonctionnel: À vérifier selon résultats ci-dessus")

if __name__ == "__main__":
    debug_step_by_step()

