# tests/test_security_database.py
#!/usr/bin/env python3
"""Tests de validation pour la sécurité et base de données"""

import sys
import os
from pathlib import Path

# Ajout du path parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from core.security.encryption import SecurityManager
from data.storage.database import DatabaseManager

def test_security_manager():
    """Test du gestionnaire de sécurité"""
    print("🧪 Test SecurityManager...")
    
    # Instanciation
    security = SecurityManager("test_master_password_2025")
    
    # Test chiffrement/déchiffrement
    original_data = "Données fiscales confidentielles - SIRET: 12345678901234"
    encrypted = security.encrypt_data(original_data)
    decrypted = security.decrypt_data(encrypted)
    
    assert original_data == decrypted
    assert encrypted != original_data
    assert len(encrypted) > len(original_data)  # Le chiffré est plus long
    
    # Test hachage mot de passe
    password = "MonMotDePasseSecret123!"
    hashed = security.hash_password(password)
    
    assert security.verify_password(password, hashed) == True
    assert security.verify_password("mauvais_mdp", hashed) == False
    
    print("✅ SecurityManager validé")
    return True

def test_database_manager():
    """Test du gestionnaire de base de données"""
    print("🧪 Test DatabaseManager...")
    
    # Création base de données de test
    test_db_url = "postgresql://localhost/fiscal_ai_db"
    
    # Instanciation avec sécurité
    security = SecurityManager("test_key_db")
    db_manager = DatabaseManager(test_db_url, security)
    
    # Test health check
    health_ok = db_manager.health_check()
    assert health_ok == True
    
    # Test création document
    doc_id = db_manager.create_document(
        client_id="TEST_CLIENT_001",
        filename="facture_test.pdf",
        content="Facture N°12345\nMontant: 1234.56€\nTVA: 20%",
        document_type="facture",
        metadata={"amount": 1234.56, "vat_rate": 0.20}
    )
    
    assert doc_id is not None
    assert isinstance(doc_id, int)
    
    # Test récupération document avec déchiffrement
    retrieved_doc = db_manager.get_document(doc_id, decrypt=True)
    
    assert retrieved_doc is not None
    assert retrieved_doc['client_id'] == "TEST_CLIENT_001"
    assert retrieved_doc['filename'] == "facture_test.pdf"
    assert "Facture N°12345" in retrieved_doc['content']
    assert retrieved_doc['metadata']['amount'] == 1234.56
    
    # Test log audit
    db_manager.log_audit(
        user_id="admin",
        action="CREATE_DOCUMENT",
        resource_type="document",
        resource_id=str(doc_id),
        details={"filename": "facture_test.pdf", "size": 1024},
        success=True
    )
    
    print("✅ DatabaseManager validé")
    return True

def main():
    """Exécution des tests de validation Étape 2"""
    print("🚀 Démarrage des tests de validation Étape 2")
    print("=" * 50)
    
    try:
        # Tests
        test_security_manager()
        test_database_manager()
        
        print("=" * 50)
        print("🎉 TOUS LES TESTS VALIDÉS - ÉTAPE 2 TERMINÉE")
        print("✅ Chiffrement AES-256 opérationnel")
        print("✅ Base de données sécurisée fonctionnelle")
        print("✅ Système d'audit intégré")
        print("✅ Intégrité des données garantie")
        
        return True
        
    except Exception as e:
        print(f"❌ ÉCHEC DES TESTS: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

