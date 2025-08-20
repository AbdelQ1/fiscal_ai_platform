# modules/ocr/adaptive_invoice_processor.py
"""
Processeur adaptatif qui apprend de ses erreurs
"""

from pathlib import Path
from typing import Dict, Any
from .intelligent_invoice_engine import IntelligentInvoiceEngine
from .learning_engine import InvoiceLearningEngine
from .invoice_extraction_result import InvoiceExtractionResult


class AdaptiveInvoiceProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.intelligent_engine = IntelligentInvoiceEngine(config)
        self.learning_engine = InvoiceLearningEngine()
        self.feedback_store = []

    def process_with_learning(self, pdf_path: Path) -> InvoiceExtractionResult:
        """Traite une facture et prépare l'apprentissage"""

        result = self.intelligent_engine.process_invoice(pdf_path)

        # Ajoute des métadonnées d'apprentissage
        result.learning_metadata = {
            'confidence_breakdown': self._analyze_confidence(result),
            'extraction_strategies': self._log_strategies_used(result),
            'potential_improvements': self._suggest_improvements(result)
        }

        return result

    def add_user_correction(self, pdf_path: Path, correct_data: Dict[str, Any]):
        """L'utilisateur corrige une extraction erronée"""

        text = self.intelligent_engine._extract_text(pdf_path)

        # Stocke la correction pour le réentraînement
        self.feedback_store.append((text, correct_data))

        # Réentraîne si assez de corrections
        if len(self.feedback_store) >= 10:
            self.learning_engine.train_from_corrections(self.feedback_store)
            self.feedback_store = []  # Reset

            print("🧠 Modèle réentraîné avec les corrections utilisateur")

    def get_confidence_explanation(self, result: InvoiceExtractionResult) -> str:
        """Explique pourquoi certains champs ont une faible confiance"""

        explanations = []

        if result.total_amount and result.extraction_confidence < 0.7:
            explanations.append("Montant détecté mais contexte ambigu")

        if not result.invoice_number:
            explanations.append("Aucun pattern de numéro de facture reconnu")

        return " • ".join(explanations)

    # Stub internes à compléter selon logique métier
    def _analyze_confidence(self, result: InvoiceExtractionResult) -> Dict[str, float]:
        return {
            "total_amount": 0.9 if result.total_amount else 0.0,
            "invoice_number": 0.8 if result.invoice_number else 0.0,
            "invoice_date": 0.7 if result.invoice_date else 0.0
        }

    def _log_strategies_used(self, result: InvoiceExtractionResult) -> Dict[str, str]:
        return {
            "amount_strategy": "AI + patterns",
            "number_strategy": "BERT context match",
            "date_strategy": "spaCy entity rule",
        }

    def _suggest_improvements(self, result: InvoiceExtractionResult) -> Dict[str, str]:
        suggestions = {}
        if not result.total_amount:
            suggestions["amount"] = "Ajouter un exemple d'entraînement avec montant TTC manquant"
        if not result.invoice_number:
            suggestions["invoice_number"] = "Renforcer les patterns de facture MCA"
        return suggestions