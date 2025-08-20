"""
BaseOCR – couche minimale commune à tous les moteurs OCR
(pour pouvoir hériter dans ConfigurableInvoiceOCR, IntelligentOCR, etc.).
"""

from __future__ import annotations
import time
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

import pytesseract
from PIL import Image, ImageFilter  # ← ImageFilter était manquant

logger = logging.getLogger(__name__)


class BaseOCR:
    """
    Socle OCR :
    • applique un pré-traitement très léger (optionnel)
    • extrait le texte avec Tesseract
    • renvoie (texte, confiance)
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.languages = "+".join(config.get("languages", ["fra", "eng"]))
        self.conf_threshold = float(config.get("confidence_threshold", 0.65))
        self.preprocessing = config.get("preprocessing", [])
        logger.info("🔍 Module OCR fiscal initialisé")
        logger.info("   - Langues: %s", self.languages.split("+"))
        logger.info("   - Seuil de confiance: %s", self.conf_threshold)
        logger.info("   - Préprocessing: %s", self.preprocessing)

    # ------------------------------------------------------------------ #
    #  POINT D’ENTRÉE PUBLIC
    # ------------------------------------------------------------------ #
    def extract_text(self, file_path: Path) -> Tuple[str, float]:
        """
        Retourne le texte OCR + score de confiance global rudimentaire.

        Le score est la moyenne des confidences Tesseract (0-1).
        """
        start = time.perf_counter()

        image = self._load_image(file_path)
        image = self._apply_preprocessing(image)

        data = pytesseract.image_to_data(
            image, lang=self.languages, output_type=pytesseract.Output.DICT
        )
        confidences = [
            float(c) / 100 for c in data["conf"] if c and c != "-1"
        ]
        text = "\n".join(data["text"])
        conf = sum(confidences) / len(confidences) if confidences else 0.0

        logger.info("🔍 Traitement document: %s", file_path.name)
        logger.info(
            "✅ Document traité en %.2fs - Confiance: %.2f",
            time.perf_counter() - start,
            conf,
        )
        return text, conf

    # ------------------------------------------------------------------ #
    #  OUTILS INTERNS
    # ------------------------------------------------------------------ #
    @staticmethod
    def _load_image(file_path: Path) -> Image.Image:
        if file_path.suffix.lower() == ".pdf":
            try:
                from pdf2image import convert_from_path
            except ImportError as exc:  # pragma: no cover
                raise ImportError("pdf2image manquant : pip install pdf2image") from exc
            return convert_from_path(str(file_path))[0]
        return Image.open(file_path)

    def _apply_preprocessing(self, img: Image.Image) -> Image.Image:
        # pré-traitements très basiques ; à étoffer si nécessaire
        if "contrast" in self.preprocessing:
            from PIL import ImageEnhance
            img = ImageEnhance.Contrast(img).enhance(1.5)

        if "denoise" in self.preprocessing:
            img = img.filter(ImageFilter.MedianFilter(size=3))

        if "deskew" in self.preprocessing:
            # deskew simpliste : pas de rotation si bibliothèque absente
            try:
                import cv2
                import numpy as np

                gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
                coords = cv2.findNonZero(cv2.bitwise_not(gray))
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                (h, w) = gray.shape
                M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
                img = Image.fromarray(cv2.warpAffine(np.array(img), M, (w, h)))
            except Exception:
                pass

        return img