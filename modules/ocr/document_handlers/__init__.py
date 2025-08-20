# modules/ocr/document_handlers/__init__.py
"""
Package des gestionnaires de documents
"""

from .base_handler import BaseDocumentHandler
from .invoice_handler import InvoiceHandler

__all__ = ['BaseDocumentHandler', 'InvoiceHandler']

