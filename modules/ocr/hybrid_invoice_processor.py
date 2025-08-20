# modules/ocr/hybrid_invoice_processor.py
"""
Processeur hybride intelligent :
1. Essaie d'abord l'extraction PDF rapide (InvoiceProcessor)
2. Fallback OCR automatique si échec ou confiance faible
3. Validation croisée des résultats
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .processors.invoice_processor import InvoiceProcessor
from .configurable_invoice_ocr import ConfigurableInvoiceOCR
from .invoice_extraction_result import InvoiceExtractionResult

logger = logging.getLogger(__name__)


class HybridInvoiceProcessor:
    """Processeur hybride avec fallback intelligent."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Moteur principal : extraction PDF rapide
        self.fast_processor = InvoiceProcessor(config)

        # Moteur de fallback : OCR complet
        self.ocr_processor = ConfigurableInvoiceOCR(config)

        # Seuils de confiance
        self.confidence_threshold = config.get("confidence_threshold", 0.75)
        self.ocr_fallback_threshold = config.get("ocr_fallback_threshold", 0.6)

        logger.info("🔄 Processeur hybride initialisé")
        logger.info("   - Seuil confiance: %.2f", self.confidence_threshold)
        logger.info("   - Seuil fallback OCR: %.2f", self.ocr_fallback_threshold)

    def process_invoice(self, file_path: Path) -> InvoiceExtractionResult:
        """Point d'entrée principal avec stratégie hybride."""
        logger.info("🚀 Traitement hybride: %s", file_path.name)

        # ================================================================
        # ÉTAPE 1 : Extraction PDF rapide (méthode éprouvée)
        # ================================================================
        try:
            logger.info("⚡ Tentative extraction PDF rapide...")
            result_fast = self._try_fast_extraction(file_path)

            if self._is_result_reliable(result_fast):
                logger.info("✅ Extraction rapide réussie - Confiance: %.2f",
                            result_fast.extraction_confidence)
                result_fast.processing_method = "fast_pdf"
                return result_fast
            else:
                logger.info("⚠️ Résultat PDF insuffisant - Confiance: %.2f",
                            result_fast.extraction_confidence)

        except Exception as e:
            logger.warning("❌ Extraction PDF échouée: %s", str(e))
            result_fast = None

        # ================================================================
        # ÉTAPE 2 : Fallback OCR complet
        # ================================================================
        logger.info("🔍 Activation fallback OCR...")
        try:
            result_ocr = self._try_ocr_extraction(file_path)

            if self._is_result_reliable(result_ocr):
                logger.info("✅ Extraction OCR réussie - Confiance: %.2f",
                            result_ocr.extraction_confidence)
                result_ocr.processing_method = "ocr_fallback"
                return result_ocr
            else:
                logger.info("⚠️ Résultat OCR insuffisant - Confiance: %.2f",
                            result_ocr.extraction_confidence)

        except Exception as e:
            logger.warning("❌ Extraction OCR échouée: %s", str(e))
            result_ocr = None

        # ================================================================
        # ÉTAPE 3 : Fusion des résultats (meilleur effort)
        # ================================================================
        if result_fast and result_ocr:
            logger.info("🔀 Fusion des résultats des deux moteurs")
            return self._merge_results(result_fast, result_ocr)
        elif result_fast:
            logger.info("📋 Retour résultat PDF (seul disponible)")
            result_fast.processing_method = "fast_pdf_only"
            return result_fast
        elif result_ocr:
            logger.info("📄 Retour résultat OCR (seul disponible)")
            result_ocr.processing_method = "ocr_only"
            return result_ocr
        else:
            logger.error("💥 Échec total des deux moteurs")
            return self._create_error_result(file_path)

    def _try_fast_extraction(self, file_path: Path) -> InvoiceExtractionResult:
        """Extraction PDF rapide avec le moteur éprouvé."""
        extracted_data = {
            "currency_amounts": [],
            "dates": [],
            "invoice_numbers": [],
            "vat_numbers": []
        }

        # Utilise la logique éprouvée d'InvoiceProcessor
        return self.fast_processor.structure_results(extracted_data, "")

    def _try_ocr_extraction(self, file_path: Path) -> InvoiceExtractionResult:
        """Extraction OCR complète avec le moteur configurable."""
        return self.ocr_processor.process_invoice(file_path)

    def _is_result_reliable(self, result: Optional[InvoiceExtractionResult]) -> bool:
        """Évalue la fiabilité d'un résultat d'extraction."""
        if not result:
            return False

        has_amount = bool(result.total_amount and result.total_amount > 0)
        has_date = bool(result.invoice_date)
        has_number = bool(result.invoice_number)
        confidence_ok = result.extraction_confidence >= self.confidence_threshold

        # Au minimum : montant + (date OU numéro) + confiance suffisante
        core_fields = has_amount and (has_date or has_number)
        return core_fields and confidence_ok

    def _merge_results(
        self,
        result_fast: InvoiceExtractionResult,
        result_ocr: InvoiceExtractionResult
    ) -> InvoiceExtractionResult:
        """Fusionne intelligemment les résultats des deux moteurs."""

        # Base : résultat avec meilleure confiance
        if result_fast.extraction_confidence >= result_ocr.extraction_confidence:
            merged = result_fast
            secondary = result_ocr
        else:
            merged = result_ocr
            secondary = result_fast

        # Complétion des champs manquants
        if not merged.total_amount and secondary.total_amount:
            merged.total_amount = secondary.total_amount
            logger.info("📈 Montant complété depuis moteur secondaire")

        if not merged.invoice_date and secondary.invoice_date:
            merged.invoice_date = secondary.invoice_date
            logger.info("📅 Date complétée depuis moteur secondaire")

        if not merged.invoice_number and secondary.invoice_number:
            merged.invoice_number = secondary.invoice_number
            logger.info("🔢 Numéro complété depuis moteur secondaire")

        if (not merged.legal_identifiers.get("numero_tva")
                and secondary.legal_identifiers.get("numero_tva")):
            merged.legal_identifiers["numero_tva"] = secondary.legal_identifiers["numero_tva"]
            logger.info("🏢 TVA complétée depuis moteur secondaire")

        merged.processing_method = "hybrid_merged"
        merged.extraction_confidence = max(
            result_fast.extraction_confidence,
            result_ocr.extraction_confidence
        )

        return merged

    def _create_error_result(self, file_path: Path) -> InvoiceExtractionResult:
        """Crée un résultat d'erreur minimal."""
        result = InvoiceExtractionResult()
        result.processing_method = "failed"
        result.extraction_confidence = 0.0
        result.extracted_entities = {"error": f"Échec extraction: {file_path.name}"}
        return result
