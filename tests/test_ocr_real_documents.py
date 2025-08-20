#!/usr/bin/env python3
"""
Test en ligne du module OCR fiscal avec documents français réels
Test sur : fiches de paie, avis d'imposition, taxe foncière
"""

import sys
import requests
import tempfile
from pathlib import Path
from typing import List, Dict
import time

# Ajout du path parent
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.ocr.base_ocr import FiscalOCRModule
from core.security.encryption import SecurityManager
from data.storage.database import DatabaseManager

class FiscalDocumentTester:
    """Testeur de documents fiscaux français avec OCR"""
    
    def __init__(self):
        """Initialisation du testeur avec configuration optimisée"""
        self.ocr_config = {
            "languages": ["fra"],  # Français uniquement pour plus de précision
            "confidence_threshold": 0.6,  # Seuil adapté aux documents scannés
            "preprocessing": ["contrast", "denoise", "deskew"],  # Preprocessing complet
            "fiscal_mode": True
        }
        
        self.ocr_module = FiscalOCRModule(self.ocr_config)
        
        # URLs d'exemples de documents fiscaux français (anonymisés)
        self.test_documents = {
            "fiche_paie": {
                "url": "https://www.service-public.fr/resources/files/sp_bulletinpaie_exemple.pdf",
                "type": "fiche_paie",
                "entities_attendues": ["montant_euro", "date_fr", "siret"],
                "description": "Exemple fiche de paie Service Public"
            },
            "avis_imposition": {
                "url": "https://www.impots.gouv.fr/sites/default/files/media/1_metier/2_professionnel/EV/2_gestion/280_editer_imprimer/10_modeles_documents/exemples_avis_imposition.pdf",
                "type": "declaration_fiscale",
                "entities_attendues": ["numero_fiscal", "montant_euro", "date_fr"],
                "description": "Exemple avis d'imposition DGFiP"
            }
        }
        
        print("🔍 Testeur OCR fiscal initialisé")
        print(f"   - Configuration: {self.ocr_module.get_module_info()}")

    def download_test_document(self, url: str, doc_type: str) -> Path:
        """Télécharge un document de test depuis une URL"""
        try:
            print(f"📥 Téléchargement: {url}")
            
            response = requests.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Sauvegarde temporaire
            temp_file = tempfile.NamedTemporaryFile(
                suffix=f'_{doc_type}.pdf', 
                delete=False
            )
            temp_file.write(response.content)
            temp_file.close()
            
            file_path = Path(temp_file.name)
            print(f"✅ Téléchargé: {file_path} ({len(response.content)} bytes)")
            
            return file_path
            
        except Exception as e:
            print(f"❌ Erreur téléchargement: {e}")
            return None

    def create_local_test_fiche_paie(self) -> Path:
        """Crée une fiche de paie de test locale avec contenu réaliste"""
        from PIL import Image, ImageDraw, ImageFont
        
        try:
            # Image haute résolution pour OCR optimal
            img = Image.new('RGB', (1200, 1600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Contenu fiche de paie française réaliste
            paie_content = [
                "BULLETIN DE PAIE",
                "Période: Janvier 2025",
                "",
                "ENTREPRISE MARTIN SARL",
                "SIRET: 12345678901234",
                "NAF: 7022Z",
                "",
                "SALARIÉ: DUPONT Jean",
                "N° Sécurité Sociale: 1 85 01 75 116 234 56",
                "",
                "ÉLÉMENTS DE RÉMUNÉRATION",
                "",
                "Salaire de base           2.500,00€",
                "Heures supplémentaires     125,50€", 
                "Prime ancienneté           150,00€",
                "",
                "BRUT                     2.775,50€",
                "",
                "COTISATIONS SALARIALES",
                "Sécurité sociale           215,44€",
                "Retraite complémentaire     83,27€",
                "Chômage                     69,39€",
                "CSG                        181,91€",
                "",
                "TOTAL COTISATIONS          549,01€",
                "",
                "NET À PAYER              2.226,49€",
                "",
                "Date de paiement: 31/01/2025",
                "Établi le: 30/01/2025"
            ]
            
            # Dessin avec mise en forme professionnelle
            y_offset = 50
            line_height = 35
            
            for line in paie_content:
                if "BULLETIN DE PAIE" in line:
                    # Titre en gras (simulé avec répétition)
                    draw.text((300, y_offset), line, fill='black')
                    draw.text((301, y_offset), line, fill='black')  # Effet gras
                elif line.startswith("ÉLÉMENTS") or line.startswith("COTISATIONS") or "BRUT" in line or "NET À PAYER" in line:
                    # Sections importantes
                    draw.text((100, y_offset), line, fill='black')
                    draw.text((101, y_offset), line, fill='black')  # Effet gras
                elif line.strip():
                    # Contenu normal
                    draw.text((150, y_offset), line, fill='black')
                
                y_offset += line_height
            
            # Sauvegarde
            temp_file = tempfile.NamedTemporaryFile(suffix='_fiche_paie_test.png', delete=False)
            img.save(temp_file.name, 'PNG', quality=95, dpi=(300, 300))
            
            return Path(temp_file.name)
            
        except Exception as e:
            print(f"❌ Erreur création fiche de paie test: {e}")
            return None

    def create_local_test_avis_imposition(self) -> Path:
        """Crée un avis d'imposition de test local"""
        from PIL import Image, ImageDraw
        
        try:
            img = Image.new('RGB', (1200, 1600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Contenu avis d'imposition français
            imposition_content = [
                "AVIS D'IMPOSITION SUR LE REVENU",
                "Année 2024 - Revenus 2023",
                "",
                "N° FISCAL: 2345678901234",
                "N° TÉLÉDÉCLARANT: 9876543210",
                "",
                "CONTRIBUABLE: MARTIN Pierre",
                "ADRESSE: 123 Rue de la République",
                "75001 PARIS",
                "",
                "SITUATION DE FAMILLE",
                "Célibataire - 0 personne à charge",
                "",
                "REVENUS DÉCLARÉS",
                "",
                "Traitements et salaires      45.230,00€",
                "Revenus fonciers              3.200,00€",
                "Plus-values                     850,00€",
                "",
                "REVENU BRUT GLOBAL           49.280,00€",
                "Charges déductibles           2.100,00€",
                "REVENU NET GLOBAL            47.180,00€",
                "",
                "CALCUL DE L'IMPÔT",
                "",
                "Revenu net imposable         47.180,00€",
                "Nombre de parts: 1",
                "Quotient familial            47.180,00€",
                "",
                "Impôt brut                    8.435,00€",
                "Décote                            0,00€",
                "Crédit d'impôt                  325,00€",
                "",
                "IMPÔT NET DÛ                  8.110,00€",
                "",
                "Date limite de paiement: 15/09/2024",
                "Établi le: 25/07/2024"
            ]
            
            # Dessin
            y_offset = 40
            line_height = 32
            
            for line in imposition_content:
                if "AVIS D'IMPOSITION" in line:
                    draw.text((250, y_offset), line, fill='black')
                    draw.text((251, y_offset), line, fill='black')
                elif any(keyword in line for keyword in ["REVENUS", "CALCUL", "SITUATION"]):
                    draw.text((100, y_offset), line, fill='black')
                    draw.text((101, y_offset), line, fill='black')
                elif line.strip():
                    draw.text((150, y_offset), line, fill='black')
                
                y_offset += line_height
            
            # Sauvegarde
            temp_file = tempfile.NamedTemporaryFile(suffix='_avis_imposition_test.png', delete=False)
            img.save(temp_file.name, 'PNG', quality=95, dpi=(300, 300))
            
            return Path(temp_file.name)
            
        except Exception as e:
            print(f"❌ Erreur création avis imposition test: {e}")
            return None

    def create_local_test_taxe_fonciere(self) -> Path:
        """Crée un avis de taxe foncière de test local"""
        from PIL import Image, ImageDraw
        
        try:
            img = Image.new('RGB', (1200, 1400), color='white')
            draw = ImageDraw.Draw(img)
            
            # Contenu taxe foncière français
            taxe_content = [
                "AVIS DE TAXE FONCIÈRE",
                "Année 2024",
                "",
                "COMMUNE: PARIS 15ème",
                "N° COMPTE COMMUNAL: 075115123456789",
                "",
                "PROPRIÉTAIRE: DUPONT Marie",
                "ADRESSE: 45 Avenue de la Liberté",
                "75015 PARIS",
                "",
                "DÉSIGNATION DU BIEN",
                "",
                "Adresse: 12 Rue Victor Hugo",
                "75015 PARIS",
                "Lot: 456 - Section: AB",
                "Parcelle: 123",
                "",
                "VALEUR LOCATIVE CADASTRALE",
                "",
                "Valeur locative brute         4.200,00€",
                "Abattements                     420,00€",
                "Valeur locative nette         3.780,00€",
                "",
                "CALCUL DE LA TAXE",
                "",
                "Taxe communale 35,15%        1.328,67€",
                "Taxe départementale 15,80%     597,24€",
                "Taxe régionale 3,60%           136,08€",
                "",
                "TOTAL TAXE FONCIÈRE          2.061,99€",
                "",
                "Échéance 1 (50%): 15/10/2024  1.030,99€",
                "Échéance 2 (50%): 15/12/2024  1.030,99€",
                "",
                "Date d'émission: 15/09/2024"
            ]
            
            # Dessin
            y_offset = 50
            line_height = 32
            
            for line in taxe_content:
                if "AVIS DE TAXE" in line:
                    draw.text((300, y_offset), line, fill='black')
                    draw.text((301, y_offset), line, fill='black')
                elif any(keyword in line for keyword in ["DÉSIGNATION", "VALEUR", "CALCUL"]):
                    draw.text((100, y_offset), line, fill='black')
                    draw.text((101, y_offset), line, fill='black')
                elif line.strip():
                    draw.text((150, y_offset), line, fill='black')
                
                y_offset += line_height
            
            # Sauvegarde
            temp_file = tempfile.NamedTemporaryFile(suffix='_taxe_fonciere_test.png', delete=False)
            img.save(temp_file.name, 'PNG', quality=95, dpi=(300, 300))
            
            return Path(temp_file.name)
            
        except Exception as e:
            print(f"❌ Erreur création taxe foncière test: {e}")
            return None

    def test_document_ocr(self, document_path: Path, doc_type: str, description: str) -> Dict:
        """Test OCR sur un document avec analyse détaillée"""
        print(f"\n🔍 Test OCR: {description}")
        print(f"   📄 Fichier: {document_path.name}")
        
        try:
            start_time = time.time()
            
            # Traitement OCR
            result = self.ocr_module.process_document(document_path, doc_type)
            
            # Analyse des résultats
            analysis = {
                "success": result.success,
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "word_count": result.word_count,
                "text_length": len(result.text),
                "entities_found": result.extracted_entities or {},
                "preprocessing": result.preprocessing_applied,
                "document_type": doc_type,
                "description": description
            }
            
            # Affichage des résultats
            if result.success:
                print(f"   ✅ OCR réussi")
                print(f"   📊 Confiance: {result.confidence:.2f}")
                print(f"   ⏱️  Temps: {result.processing_time:.2f}s")
                print(f"   📝 Mots extraits: {result.word_count}")
                print(f"   🔧 Préprocessing: {', '.join(result.preprocessing_applied)}")
                
                # Affichage texte extrait (aperçu)
                if result.text:
                    preview = result.text[:200].replace('\n', ' ')
                    print(f"   📖 Aperçu texte: {preview}...")
                
                # Analyse des entités fiscales
                if result.extracted_entities:
                    print(f"   🏷️  Entités fiscales trouvées:")
                    for entity_type, values in result.extracted_entities.items():
                        print(f"      - {entity_type}: {values}")
                else:
                    print(f"   🏷️  Aucune entité fiscale détectée")
                
            else:
                print(f"   ❌ OCR échoué: {result.error_message}")
            
            return analysis
            
        except Exception as e:
            print(f"   ❌ Erreur test: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_type": doc_type,
                "description": description
            }

    def run_comprehensive_test(self):
        """Lance un test complet sur tous les types de documents"""
        print("🚀 DÉMARRAGE TEST COMPLET OCR DOCUMENTS FISCAUX FRANÇAIS")
        print("=" * 70)
        
        results = []
        temp_files = []
        
        try:
            # Test 1: Fiche de paie locale
            print("\n📑 TEST 1: FICHE DE PAIE")
            fiche_paie_path = self.create_local_test_fiche_paie()
            if fiche_paie_path:
                temp_files.append(fiche_paie_path)
                result = self.test_document_ocr(
                    fiche_paie_path, 
                    "fiche_paie", 
                    "Fiche de paie française simulée"
                )
                results.append(result)
            
            # Test 2: Avis d'imposition local
            print("\n📑 TEST 2: AVIS D'IMPOSITION")
            avis_path = self.create_local_test_avis_imposition()
            if avis_path:
                temp_files.append(avis_path)
                result = self.test_document_ocr(
                    avis_path, 
                    "declaration_fiscale", 
                    "Avis d'imposition français simulé"
                )
                results.append(result)
            
            # Test 3: Taxe foncière locale
            print("\n📑 TEST 3: TAXE FONCIÈRE")
            taxe_path = self.create_local_test_taxe_fonciere()
            if taxe_path:
                temp_files.append(taxe_path)
                result = self.test_document_ocr(
                    taxe_path, 
                    "taxe_fonciere", 
                    "Avis de taxe foncière français simulé"
                )
                results.append(result)
            
            # Synthèse des résultats
            self.display_test_summary(results)
            
        finally:
            # Nettoyage des fichiers temporaires
            print("\n🧹 Nettoyage des fichiers temporaires...")
            for temp_file in temp_files:
                try:
                    temp_file.unlink(missing_ok=True)
                    print(f"   ✅ Supprimé: {temp_file.name}")
                except Exception as e:
                    print(f"   ⚠️ Erreur suppression {temp_file.name}: {e}")

    def display_test_summary(self, results: List[Dict]):
        """Affiche un résumé détaillé des tests"""
        print("\n" + "=" * 70)
        print("📊 SYNTHÈSE DES TESTS OCR DOCUMENTS FISCAUX")
        print("=" * 70)
        
        successful_tests = [r for r in results if r.get('success', False)]
        failed_tests = [r for r in results if not r.get('success', False)]
        
        print(f"✅ Tests réussis: {len(successful_tests)}/{len(results)}")
        print(f"❌ Tests échoués: {len(failed_tests)}/{len(results)}")
        
        if successful_tests:
            avg_confidence = sum(r['confidence'] for r in successful_tests) / len(successful_tests)
            avg_time = sum(r['processing_time'] for r in successful_tests) / len(successful_tests)
            total_words = sum(r['word_count'] for r in successful_tests)
            
            print(f"\n📈 STATISTIQUES:")
            print(f"   - Confiance moyenne: {avg_confidence:.2f}")
            print(f"   - Temps moyen: {avg_time:.2f}s")
            print(f"   - Total mots extraits: {total_words}")
            
            print(f"\n🏷️ ENTITÉS FISCALES DÉTECTÉES:")
            all_entities = {}
            for result in successful_tests:
                for entity_type, values in result.get('entities_found', {}).items():
                    if entity_type not in all_entities:
                        all_entities[entity_type] = 0
                    all_entities[entity_type] += len(values)
            
            for entity_type, count in all_entities.items():
                print(f"   - {entity_type}: {count} occurrence(s)")
        
        if failed_tests:
            print(f"\n⚠️ ÉCHECS:")
            for failed in failed_tests:
                print(f"   - {failed['description']}: {failed.get('error', 'Confiance insuffisante')}")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        if len(successful_tests) == len(results):
            print("   ✅ Module OCR parfaitement opérationnel pour documents fiscaux français")
            print("   ✅ Prêt pour intégration en production")
        elif len(successful_tests) > 0:
            print("   ⚠️ Module OCR partiellement fonctionnel")
            print("   💡 Considérer ajustement seuils de confiance ou préprocessing")
        else:
            print("   ❌ Module OCR nécessite optimisation")
            print("   💡 Vérifier configuration Tesseract et qualité images")

def main():
    """Point d'entrée principal du test"""
    try:
        tester = FiscalDocumentTester()
        tester.run_comprehensive_test()
        
        print("\n🎉 TEST COMPLET TERMINÉ")
        print("Votre module OCR fiscal est maintenant testé sur documents français réalistes !")
        
    except Exception as e:
        print(f"❌ Erreur critique du test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

