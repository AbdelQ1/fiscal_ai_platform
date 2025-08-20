#!/usr/bin/env python3
"""
Analyse du PDF sans OCR - extraction du texte brut si possible
"""

import sys
from pathlib import Path

def analyze_pdf_without_ocr():
    pdf_path = Path("invoices_to_test/Facture MCA Syno RAM 8G 2024.pdf")
    
    print(f"🔍 Analyse du fichier: {pdf_path}")
    print(f"📁 Taille: {pdf_path.stat().st_size} bytes")
    
    # Essayer d'extraire du texte avec des méthodes simples
    try:
        import PyPDF2
        print("📄 Tentative d'extraction avec PyPDF2...")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"📖 Nombre de pages: {len(pdf_reader.pages)}")
            
            for i, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                print(f"\n--- PAGE {i+1} ---")
                print(f"Longueur du texte: {len(text)} caractères")
                if text.strip():
                    print("Contenu:")
                    print(text[:500] + "..." if len(text) > 500 else text)
                else:
                    print("❌ Aucun texte extractible (PDF image/scanné)")
                    
    except ImportError:
        print("⚠️ PyPDF2 non disponible")
        
    try:
        import pdfplumber
        print("\n📄 Tentative d'extraction avec pdfplumber...")
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"📖 Nombre de pages: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                print(f"\n--- PAGE {i+1} (pdfplumber) ---")
                if text:
                    print(f"Longueur: {len(text)} caractères")
                    print("Contenu:")
                    print(text[:500] + "..." if len(text) > 500 else text)
                else:
                    print("❌ Aucun texte extractible")
                    
    except ImportError:
        print("⚠️ pdfplumber non disponible")
    
    # Info sur le fichier
    print(f"\n📊 Informations fichier:")
    print(f"Nom: {pdf_path.name}")
    print(f"Taille: {pdf_path.stat().st_size:,} bytes")
    print(f"Date modification: {pdf_path.stat().st_mtime}")

if __name__ == "__main__":
    analyze_pdf_without_ocr()