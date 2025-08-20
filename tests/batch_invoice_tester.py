# tests/batch_invoice_tester.py
"""
Testeur batch pour l'extraction de factures avec support du prix HT
"""

import time
from pathlib import Path
from typing import List, Tuple
import sys
import os

# Ajouter le dossier parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.ocr.fast_pdf_invoice_engine import FastPdfInvoiceEngine
from modules.ocr.invoice_extraction_result import InvoiceExtractionResult


class BatchInvoiceTester:
    """Testeur batch pour valider les extractions de factures."""
    
    def __init__(self, invoice_folder: str = "invoices_to_test"):
        self.invoice_folder = Path(invoice_folder)
        self.processor = FastPdfInvoiceEngine({})
        
        # Extensions de fichiers supportées
        self.supported_extensions = {'.pdf'}
        
    def run_tests(self):
        """Lance les tests sur tous les fichiers du dossier."""
        
        print("🚀 LANCEMENT DU TEST HYBRIDE" + "="*81)
        
        # Trouve tous les fichiers PDF
        files = self._find_invoice_files()
        if not files:
            print(f"❌ Aucun fichier trouvé dans {self.invoice_folder}")
            return
        
        results = []
        total_time = 0
        
        # Traite chaque fichier
        for i, file_path in enumerate(files, 1):
            result, processing_time = self._process_file_with_timing(file_path)
            total_time += processing_time
            
            # Calcule le score de complétude
            completeness_score = self._calculate_completeness(result)
            
            # Affichage du statut
            status = "✅" if completeness_score == 6 else "❌"
            method = result.processing_method if result else "error"
            
            # Tronque le nom si trop long
            display_name = self._truncate_filename(file_path.name, 30)
            
            print(f"[{i}/{len(files)}] {status} {display_name:<30} - {method:<12} - {processing_time:>6} ms - {completeness_score}/6")
            
            results.append((file_path, result, processing_time, completeness_score))
        
        # Affichage du tableau détaillé
        print("\n📊 EXTRACTIONS STRUCTURÉES" + "-"*82)
        self._display_results_table(results)
        
        # Résumé global
        print("\n📈 RÉSUMÉ")
        self._display_summary(results, total_time)
    
    def _find_invoice_files(self) -> List[Path]:
        """Trouve tous les fichiers de factures dans le dossier."""
        if not self.invoice_folder.exists():
            return []
        
        files = []
        for file_path in self.invoice_folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                files.append(file_path)
        
        return sorted(files)
    
    def _process_file_with_timing(self, file_path: Path) -> Tuple[InvoiceExtractionResult, int]:
        """Traite un fichier et mesure le temps d'exécution."""
        try:
            start_time = time.time()
            result = self.processor.process_invoice(file_path)
            end_time = time.time()
            
            processing_time = int((end_time - start_time) * 1000)  # en ms
            return result, processing_time
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {file_path.name}: {e}")
            return None, 0
    
    def _calculate_completeness(self, result: InvoiceExtractionResult) -> int:
        """Calcule le score de complétude (0-6 champs)."""
        if not result:
            return 0
        
        score = 0
        
        # Champs principaux (4 points)
        if result.total_amount:
            score += 1
        if result.invoice_date:
            score += 1
        if result.invoice_number:
            score += 1
        if result.legal_identifiers and result.legal_identifiers.get("numero_tva"):
            score += 1
        
        # Champs TVA (2 points)
        if result.vat_rate is not None:
            score += 1
        if result.amount_ht is not None:  # NOUVEAU
            score += 1
            
        return score
    
    def _display_results_table(self, results: List[Tuple]):
        """Affiche le tableau détaillé des résultats avec Prix HT."""
        
        # En-têtes avec nouvelle colonne Prix HT
        headers = ["Fichier", "Total TTC", "Prix HT", "Date facture", "N° Facture", "N° TVA", "Taux TVA", "Méthode", "Temps"]
        
        # Largeurs de colonnes ajustées
        col_widths = [25, 12, 12, 15, 18, 13, 9, 10, 7]
        
        # Ligne d'en-tête
        header_line = "| " + " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths)) + " |"
        separator = "-" * len(header_line)
        
        print(header_line)
        print(separator)
        
        # Lignes de données
        for file_path, result, proc_time, score in results:
            if not result:
                continue
                
            # Formatage des valeurs
            filename = self._truncate_filename(file_path.name, col_widths[0])
            
            total_amount = f"{result.total_amount:.2f}€" if result.total_amount else "—"
            amount_ht = f"{result.amount_ht:.2f}€" if result.amount_ht else "—"  # NOUVEAU
            invoice_date = result.invoice_date or "—"
            invoice_number = self._truncate_text(result.invoice_number or "—", col_widths[4])
            vat_number = self._truncate_text(
                result.legal_identifiers.get("numero_tva", "—"), col_widths[5]
            )
            
            # Formatage du taux de TVA
            vat_rate = f"{result.vat_rate}%" if result.vat_rate is not None else "—"
            
            method = result.processing_method
            timing = f"{proc_time} ms"
            
            # Construction de la ligne avec prix HT
            row_data = [filename, total_amount, amount_ht, invoice_date, invoice_number, 
                       vat_number, vat_rate, method, timing]
            
            row_line = "| " + " | ".join(f"{d:<{w}}" for d, w in zip(row_data, col_widths)) + " |"
            print(row_line)
    
    def _display_summary(self, results: List[Tuple], total_time: int):
        """Affiche le résumé global."""
        
        total_files = len([r for r in results if r[1] is not None])
        total_fields = sum(r[3] for r in results if r[1] is not None)
        max_possible_fields = total_files * 6  # 6 champs maintenant (avec prix HT)
        
        success_rate = (total_fields / max_possible_fields * 100) if max_possible_fields > 0 else 0
        avg_time = total_time // total_files if total_files > 0 else 0
        
        print(f"   • Documents traités  : {total_files}")
        print(f"   • Réussite globale   : {success_rate:.2f}% ({total_fields}/{max_possible_fields})")
        print(f"   • Temps moyen/fichier: {avg_time} ms")
        
        if success_rate >= 95:
            print("🎉 PARFAIT !")
        elif success_rate >= 80:
            print("✅ TRÈS BIEN !")
        else:
            print("⚠️  Des champs manquent.")
    
    @staticmethod
    def _truncate_filename(filename: str, max_length: int) -> str:
        """Tronque un nom de fichier pour l'affichage."""
        if len(filename) <= max_length:
            return filename
        
        # Garde le début et la fin avec [...]
        if max_length < 10:
            return filename[:max_length]
        
        start_chars = (max_length - 5) // 2
        end_chars = max_length - 5 - start_chars
        
        return f"{filename[:start_chars]} [...] {filename[-end_chars:]}" if end_chars > 0 else f"{filename[:start_chars]} [...]"
    
    @staticmethod
    def _truncate_text(text: str, max_length: int) -> str:
        """Tronque un texte pour l'affichage."""
        if len(text) <= max_length:
            return text
        return text[:max_length-1] + "…"


def main():
    """Point d'entrée principal."""
    tester = BatchInvoiceTester()
    tester.run_tests()


if __name__ == "__main__":
    main()
