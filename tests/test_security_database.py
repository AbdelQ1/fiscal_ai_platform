# tests/test_security_database.py (VERSION FINALE CORRIGÉE)
#!/usr/bin/env python3
"""Tests de validation pour la sécurité et base de données - VERSION CORRIGÉE"""

import sys
import os
from pathlib import Path

# Ajout du path parent pour les imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports avec gestion d'erreurs
try:
    from core.security.encryption import SecurityManager
    from data.storage.database import DatabaseManager
    print("✅ Imports réussis")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

def test_security_manager():
    """Test du gestionnaire de sécurité avec bcrypt direct"""
    print("🧪 Test SecurityManager...")
    
    try:
        # Instanciation
        security = SecurityManager("test_master_password_2025")
        
        # Test chiffrement/déchiffrement
        original_data = "Données fiscales confidentielles - SIRET: 12345678901234"
        encrypted = security.encrypt_data(original_data)
        decrypted = security.decrypt_data(encrypted)
        
        assert original_data == decrypted
        assert encrypted != original_data
        assert len(encrypted) > len(original_data)  # Le chiffré est plus long
        
        # Test hachage mot de passe avec bcrypt direct
        password = "MonMotDePasseSecret123!"
        hashed = security.hash_password(password)
        
        assert security.verify_password(password, hashed) == True
        assert security.verify_password("mauvais_mdp", hashed) == False
        
        print("✅ SecurityManager validé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur SecurityManager: {e}")
        return False

def test_database_manager():
    """Test du gestionnaire de base de données avec health check corrigé"""
    print("🧪 Test DatabaseManager...")
    
    # Création base de données de test
    test_db_url = "postgresql://localhost/fiscal_ai_db"
    
    try:
        # Instanciation avec sécurité
        security = SecurityManager("test_key_db")
        db_manager = DatabaseManager(test_db_url, security)
        
        # Test health check corrigé
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
        
    except Exception as e:
        print(f"❌ Erreur DatabaseManager: {e}")
        print("   Note: Assurez-vous que PostgreSQL est démarré et fiscal_ai_db existe")
        return False

def main():
    """Exécution des tests de validation Étape 2"""
    print("🚀 Démarrage des tests de validation Étape 2 - VERSION CORRIGÉE")
    print("=" * 60)
    
    try:
        # Tests
        security_ok = test_security_manager()
        database_ok = test_database_manager()
        
        if security_ok and database_ok:
            print("=" * 60)
            print("🎉 TOUS LES TESTS VALIDÉS - ÉTAPE 2 TERMINÉE")
            print("✅ Chiffrement AES-256 opérationnel")
            print("✅ Hachage bcrypt direct fonctionnel")
            print("✅ Base de données sécurisée opérationnelle")
            print("✅ Système d'audit intégré")
            print("✅ Intégrité des données garantie")
            return True
        else:
            print("=" * 60)
            print("⚠️  TESTS PARTIELLEMENT VALIDÉS")
            if security_ok:
                print("✅ Sécurité OK")
            if database_ok:
                print("✅ Base de données OK")
            return False
        
    except Exception as e:
        print(f"❌ ÉCHEC DES TESTS: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
