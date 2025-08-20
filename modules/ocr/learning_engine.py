# modules/ocr/learning_engine.py
"""
Moteur d'apprentissage pour améliorer l'extraction
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any  # Ajout de Any
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier


class InvoiceLearningEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 3))
        self.amount_classifier = RandomForestClassifier(n_estimators=100)
        self.number_classifier = RandomForestClassifier(n_estimators=100)

        self.training_data = []

    def add_training_example(self, text: str, correct_extractions: Dict[str, Any]):
        """Ajoute un exemple d'entraînement"""
        self.training_data.append({
            'text': text,
            'extractions': correct_extractions
        })

    def train_from_corrections(self, corrections: List[Tuple[str, Dict[str, Any]]]):
        """Entraîne le modèle à partir de corrections utilisateur"""

        # Prépare les données d'entraînement
        texts = []
        amount_labels = []
        number_labels = []

        for text, correct_data in corrections:
            # Extrait les features du texte
            texts.append(text)

            # Labels pour les montants (position dans le texte)
            amount_position = self._find_positions(text, correct_data.get('total_amount'))
            amount_labels.append(amount_position)

            # Labels pour les numéros
            number_position = self._find_positions(text, correct_data.get('invoice_number'))
            number_labels.append(number_position)

        # Entraîne les classificateurs
        if texts:
            X = self.vectorizer.fit_transform(texts)
            self.amount_classifier.fit(X, amount_labels)
            self.number_classifier.fit(X, number_labels)

    def predict_best_extraction(self, text: str) -> Dict[str, float]:
        """Prédit les meilleures extractions avec scores de confiance"""

        X = self.vectorizer.transform([text])

        # Probabilités de classification
        amount_proba = self.amount_classifier.predict_proba(X)[0]
        number_proba = self.number_classifier.predict_proba(X)[0]

        return {
            'amount_confidence': max(amount_proba),
            'number_confidence': max(number_proba)
        }

    def _find_positions(self, text: str, value: Any) -> int:
        """Retourne un index approximatif dans le texte (fallback simple)"""
        if not value:
            return 0
        try:
            return text.index(str(value))
        except ValueError:
            return 0

    def _extract_features(self, text: str) -> Dict[str, Any]:
        """Méthode placeholder (optionnelle si features étendues à l'avenir)"""
        return {"length": len(text)}
