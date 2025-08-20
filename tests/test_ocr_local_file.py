#!/usr/bin/env python3
"""
Test du module OCR fiscal avec fichier local
Usage: python test_ocr_local_file.py /chemin/vers/votre/document.pdf
"""

import sys
import argparse
from pathlib import Path
import time
from typing import Dict

# Ajout du path parent
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from modules.ocr.base_ocr import FiscalOCRModule
    print("✅ Import du module OCR réussi")
except ImportError as e:
    print(f"❌ Erreur d'import OCR: {e}")
    sys.exit(1)

class LocalFileTester:
    """Testeur OCR pour fichiers locaux"""
    
    def __init__(self):
        """Initialisation avec configuration optimisée pour documents réels"""
        self.ocr_config = {
            "languages": ["fra", "eng"],  # Français et anglais
            "confidence_threshold": 0.65,  # Seuil adapté aux vrais documents
            "preprocessing": ["contrast", "denoise", "deskew"],  # Préprocessing complet
            "fiscal_mode": True  # Mode spécialisé fiscal français
        }
        
        self.ocr_module = FiscalOCRModule(self.ocr_config)
        
        print("🔍 Module OCR fiscal initialisé pour test fichier local")
        print(f"   - Langues: {self.ocr_config['languages']}")
        print(f"   - Seuil de confiance: {self.ocr_config['confidence_threshold']}")
        print(f"   - Préprocessing: {', '.join(self.ocr_config['preprocessing'])}")

    def test_local_file(self, file_path: str, document_type: str = "auto") -> Dict:
        """Test OCR sur un fichier local"""
        file_path = Path(file_path)
        
        print(f"\n🔍 ANALYSE OCR DU FICHIER LOCAL")
        print("=" * 60)
        print(f"📁 Fichier: {file_path.name}")
        print(f"📂 Chemin: {file_path}")
        print(f"📄 Type: {document_type}")
        
        # Vérifications préalables
        if not file_path.exists():
            print(f"❌ ERREUR: Le fichier '{file_path}' n'existe pas")
            return {"success": False, "error": "Fichier introuvable"}
        
        if not file_path.is_file():
            print(f"❌ ERREUR: '{file_path}' n'est pas un fichier")
            return {"success": False, "error": "Chemin invalide"}
        
        # Vérification du format
        supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        if file_path.suffix.lower() not in supported_extensions:
            print(f"❌ ERREUR: Format '{file_path.suffix}' non supporté")
            print(f"   Formats supportés: {', '.join(supported_extensions)}")
            return {"success": False, "error": "Format non supporté"}
        
        file_size = file_path.stat().st_size
        print(f"📊 Taille: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        # Auto-détection du type de document
        if document_type == "auto":
            document_type = self._detect_document_type(file_path.name.lower())
            print(f"🤖 Type détecté automatiquement: {document_type}")
        
        print(f"\n⏳ Traitement en cours...")
        start_time = time.time()
        
        try:
            # Traitement OCR
            result = self.ocr_module.process_document(file_path, document_type)
            processing_time = time.time() - start_time
            
            # Affichage des résultats détaillés
            self._display_results(result, processing_time, file_path)
            
            return {
                "success": result.success,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "word_count": result.word_count,
                "text_length": len(result.text),
                "entities_found": len(result.extracted_entities or {}),
                "file_path": str(file_path),
                "document_type": document_type
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"\n❌ ERREUR LORS DU TRAITEMENT:")
            print(f"   {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": processing_time,
                "file_path": str(file_path)
            }

    def _detect_document_type(self, filename: str) -> str:
        """Détection automatique du type de document selon le nom"""
        filename = filename.lower()
        
        # Patterns de détection
        if any(word in filename for word in ['paie', 'salaire', 'bulletin']):
            return "fiche_paie"
        elif any(word in filename for word in ['impot', 'imposition', 'fiscal', 'declaration']):
            return "declaration_fiscale"
        elif any(word in filename for word in ['taxe', 'fonciere', 'foncier']):
            return "taxe_fonciere"
        elif any(word in filename for word in ['facture', 'invoice', 'fact']):
            return "facture"
        elif any(word in filename for word in ['devis', 'quote', 'estimation']):
            return "devis"
        elif any(word in filename for word in ['releve', 'statement', 'compte']):
            return "releve_bancaire"
        else:
            return "document_fiscal"

    def _display_results(self, result, processing_time: float, file_path: Path):
        """Affichage détaillé des résultats OCR"""
        print(f"\n📊 RÉSULTATS DE L'ANALYSE OCR")
        print("=" * 60)
        
        if result.success:
            print(f"✅ TRAITEMENT RÉUSSI")
            print(f"   📈 Confiance globale: {result.confidence:.2f} ({result.confidence*100:.1f}%)")
            print(f"   ⏱️  Temps de traitement: {result.processing_time:.2f}s")
            print(f"   📄 Pages traitées: {result.page_count}")
            print(f"   📝 Mots extraits: {result.word_count}")
            print(f"   🔧 Préprocessing appliqué: {', '.join(result.preprocessing_applied)}")
            
            if result.confidence >= 0.8:
                confidence_emoji = "🟢"
                confidence_text = "EXCELLENTE"
            elif result.confidence >= 0.6:
                confidence_emoji = "🟡"
                confidence_text = "BONNE"
            else:
                confidence_emoji = "🔴"
                confidence_text = "FAIBLE"
            
            print(f"   {confidence_emoji} Qualité: {confidence_text}")
            
            # Aperçu du texte extrait
            if result.text:
                print(f"\n📖 APERÇU DU TEXTE EXTRAIT:")
                print("-" * 40)
                
                # Affichage des premières lignes
                lines = result.text.split('\n')
                preview_lines = [line.strip() for line in lines[:15] if line.strip()]
                
                for i, line in enumerate(preview_lines, 1):
                    if len(line) > 80:
                        line = line[:77] + "..."
                    print(f"   {i:2d}. {line}")
                
                if len(lines) > 15:
                    print(f"   ... et {len(lines) - 15} lignes supplémentaires")
                
                print("-" * 40)
                print(f"📊 Statistiques texte:")
                print(f"   - Lignes totales: {len(lines)}")
                print(f"   - Caractères: {len(result.text):,}")
                print(f"   - Mots: {result.word_count}")
            
            # Entités fiscales détectées
            if result.extracted_entities:
                print(f"\n🏷️  ENTITÉS FISCALES DÉTECTÉES:")
                print("-" * 40)
                for entity_type, values in result.extracted_entities.items():
                    entity_name = {
                        'siret': 'SIRET',
                        'siren': 'SIREN', 
                        'tva_number': 'N° TVA',
                        'montant_euro': 'Montants €',
                        'date_fr': 'Dates',
                        'numero_facture': 'N° Facture',
                        'taux_tva': 'Taux TVA',
                        'rib_iban': 'RIB/IBAN',
                        'code_comptable': 'Code comptable'
                    }.get(entity_type, entity_type.title())
                    
                    print(f"   💼 {entity_name}: {len(values)} trouvé(s)")
                    for value in values[:3]:  # Afficher les 3 premiers
                        print(f"      ▪ {value}")
                    if len(values) > 3:
                        print(f"      ... et {len(values) - 3} autre(s)")
                print("-" * 40)
            else:
                print(f"\n🏷️  Aucune entité fiscale spécifique détectée")
                print("   (Normal pour certains types de documents)")
        
        else:
            print(f"❌ TRAITEMENT ÉCHOUÉ")
            print(f"   ⏱️  Temps avant échec: {result.processing_time:.2f}s")
            print(f"   📝 Erreur: {result.error_message}")
            
            # Suggestions d'amélioration
            print(f"\n💡 SUGGESTIONS D'AMÉLIORATION:")
            if "format" in result.error_message.lower():
                print("   - Vérifiez que le fichier est dans un format supporté")
                print("   - Convertissez en PDF ou PNG si nécessaire")
            elif "quality" in result.error_message.lower() or result.confidence < 0.3:
                print("   - Améliorez la qualité de l'image (résolution, contraste)")
                print("   - Scannez à 300 DPI minimum")
                print("   - Évitez les images floues ou inclinées")
            else:
                print("   - Vérifiez que le document contient du texte lisible")
                print("   - Essayez avec un document plus simple pour tester")

def main():
    """Point d'entrée principal avec arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Test OCR fiscal sur fichier local",
        epilog="Exemple: python test_ocr_local_file.py ~/Documents/facture.pdf"
    )
    
    parser.add_argument(
        "file_path",
        help="Chemin vers le fichier à analyser (PDF, PNG, JPG, etc.)"
    )
    
    parser.add_argument(
        "--type", "-t",
        dest="document_type",
        default="auto",
        choices=["auto", "facture", "fiche_paie", "declaration_fiscale", "taxe_fonciere", "devis", "releve_bancaire"],
        help="Type de document (détection automatique par défaut)"
    )
    
    parser.add_argument(
        "--confidence", "-c",
        type=float,
        default=0.65,
        help="Seuil de confiance OCR (0.0-1.0, défaut: 0.65)"
    )
    
    parser.add_argument(
        "--save-text", "-s",
        action="store_true",
        help="Sauvegarder le texte extrait dans un fichier .txt"
    )
    
    args = parser.parse_args()
    
    # Validation des arguments
    if not (0.0 <= args.confidence <= 1.0):
        print("❌ ERREUR: Le seuil de confiance doit être entre 0.0 et 1.0")
        sys.exit(1)
    
    try:
        # Initialisation du testeur
        tester = LocalFileTester()
        
        # Ajustement du seuil de confiance si spécifié
        if args.confidence != 0.65:
            tester.ocr_config["confidence_threshold"] = args.confidence
            tester.ocr_module.confidence_threshold = args.confidence
            print(f"🔧 Seuil de confiance ajusté à {args.confidence}")
        
        # Lancement du test
        result = tester.test_local_file(args.file_path, args.document_type)
        
        # Sauvegarde du texte si demandée
        if args.save_text and result.get("success"):
            output_file = Path(args.file_path).with_suffix('.txt')
            try:
                # Récupération du texte depuis le module OCR
                ocr_result = tester.ocr_module.process_document(args.file_path, args.document_type)
                if ocr_result.success and ocr_result.text:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Extraction OCR de {Path(args.file_path).name}\n")
                        f.write(f"# Généré le {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"# Confiance: {ocr_result.confidence:.2f}\n\n")
                        f.write(ocr_result.text)
                    print(f"\n💾 Texte sauvegardé dans: {output_file}")
                else:
                    print(f"\n⚠️  Impossible de sauvegarder: pas de texte extrait")
            except Exception as e:
                print(f"\n❌ Erreur sauvegarde: {e}")
        
        # Code de sortie selon le résultat
        if result.get("success"):
            print(f"\n🎉 TEST TERMINÉ AVEC SUCCÈS")
            if result.get("confidence", 0) >= 0.8:
                print("✅ Excellente qualité d'extraction")
                sys.exit(0)
            elif result.get("confidence", 0) >= 0.6:
                print("⚠️  Qualité acceptable, possibles améliorations")
                sys.exit(0)
            else:
                print("⚠️  Qualité faible, document difficile à lire")
                sys.exit(1)
        else:
            print(f"\n❌ TEST ÉCHOUÉ")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

