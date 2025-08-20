# test_patterns_corriges.py
#!/usr/bin/env python3
"""Test avec les patterns corrigés basés sur vos données réelles"""

import re

# Votre texte OCR réel (extrait du diagnostic)
text_ocr = """=== PAGE 1 ===
amazonfr Factur acture Payé Référence de paiement Vendu par Amazon EU Succursale Frangaise TVA FR12487773327 Date de la facture/Date de Ia livraison 24 février 2024 REGRAGUI la f. de la acture FR49RG8YA RUE AMELIE Total payer ,04 LE PLESSIS ROBINSON, 92350 pay FR Veuillez Contacter le Service Client en Visitant le lien Suivant: Adresse de facturation Adresse de livraison Vendu par REGRAGuI REGRAGUI Amazon EU S.à Succursale Française rue Amélie rue Amélie 67 Boulevard du General Le"""

# Patterns corrigés
patterns_corriges = {
    'montants': r'(\d{1,3},\d{2})',
    'total': r'Total\s+payer[:\s]*(\d{1,3},\d{2})',
    'dates': r'(\d{1,2})\s+(février|janvier|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})',
    'tva': r'(FR\d{11})',
    'ref_facture': r'(FR\d{2}[A-Z0-9]{8})'
}

print("🧪 TEST PATTERNS CORRIGÉS SUR VOTRE TEXTE")
print("=" * 60)

for nom, pattern in patterns_corriges.items():
    try:
        matches = re.findall(pattern, text_ocr, re.IGNORECASE)
        print(f"{nom:15} : {len(matches)} matches - {matches}")
    except Exception as e:
        print(f"{nom:15} : ERREUR - {e}")

print(f"\n📊 RÉSULTATS ATTENDUS :")
print(f"   montants     : 4+ matches incluant 169,04 et 140,87")
print(f"   dates        : 1 match avec ('24', 'février', '2024')")
print(f"   tva          : 1 match avec FR12487773327")
print(f"   ref_facture  : 1 match avec FR49RG8YA...")

