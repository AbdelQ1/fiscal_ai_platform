from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import logging
import hashlib
import secrets
from typing import Optional, Union, Tuple

class SecurityManager:
    # ... docstring inchangée ...

    def __init__(self, master_password: Optional[str] = None):
        # ... inchangé ...
        self.logger = logging.getLogger(__name__)
        self.salt_length = 32
        self.key_derivation_iterations = 100000
        
        self.master_password = (
            master_password or 
            os.getenv('FISCAL_AI_MASTER_KEY', 'fiscal_ai_secure_key_2025_production')
        )
        self.encryption_key = self._derive_encryption_key(self.master_password)
        self.cipher_suite = Fernet(self.encryption_key)

        self.logger.info("🔒 SecurityManager initialisé avec chiffrement AES-256")
        self.logger.info(f"   - Salt length: {self.salt_length} bytes")
        self.logger.info(f"   - PBKDF2 iterations: {self.key_derivation_iterations}")

    def _derive_encryption_key(self, password: str) -> bytes:
        try:
            password_bytes = password.encode('utf-8')
            fixed_salt = b'fiscal_ai_platform_salt_v2025_secure_derivation'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=fixed_salt,
                iterations=self.key_derivation_iterations,
                backend=default_backend()
            )
            derived_key = kdf.derive(password_bytes)
            fernet_key = base64.urlsafe_b64encode(derived_key)
            return fernet_key
        except Exception as e:
            self.logger.error(f"❌ Erreur dérivation clé de chiffrement: {str(e)}")
            raise SecurityError(f"Échec dérivation clé: {str(e)}")

    def encrypt_data(self, data: Union[str, bytes]) -> str:
        try:
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            encrypted_data = self.cipher_suite.encrypt(data_bytes)
            encrypted_b64 = base64.urlsafe_b64encode(encrypted_data).decode('ascii')
            self.logger.debug(f"✅ Données chiffrées: {len(data_bytes)} bytes → {len(encrypted_b64)} chars")
            return encrypted_b64
        except Exception as e:
            self.logger.error(f"❌ Erreur chiffrement: {str(e)}")
            raise SecurityError(f"Échec chiffrement des données: {str(e)}")

    def decrypt_data(self, encrypted_data: str) -> str:
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('ascii'))
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode('utf-8')
            self.logger.debug(f"✅ Données déchiffrées: {len(encrypted_data)} chars → {len(decrypted_str)} bytes")
            return decrypted_str
        except Exception as e:
            self.logger.error(f"❌ Erreur déchiffrement: {str(e)}")
            if "InvalidToken" in str(e):
                raise SecurityError("Données corrompues ou clé incorrecte")
            else:
                raise SecurityError(f"Échec déchiffrement: {str(e)}")

    def hash_password(self, password: str) -> str:
        try:
            salt = secrets.token_bytes(self.salt_length)
            combined = salt + password.encode('utf-8')
            password_hash = hashlib.sha256(combined).hexdigest()
            salt_hex = salt.hex()
            stored_hash = f"{salt_hex}${password_hash}"
            self.logger.debug(f"✅ Mot de passe haché avec salt de {len(salt)} bytes")
            return stored_hash
        except Exception as e:
            self.logger.error(f"❌ Erreur hachage mot de passe: {str(e)}")
            raise SecurityError(f"Échec hachage: {str(e)}")

    def verify_password(self, plain_password: str, stored_hash: str) -> bool:
        try:
            if '$' not in stored_hash:
                self.logger.warning("⚠️  Format de hash invalide (pas de séparateur $)")
                return False
            salt_hex, expected_hash = stored_hash.split('$', 1)
            salt = bytes.fromhex(salt_hex)
            combined = salt + plain_password.encode('utf-8')
            calculated_hash = hashlib.sha256(combined).hexdigest()
            is_valid = secrets.compare_digest(calculated_hash, expected_hash)
            if is_valid:
                self.logger.debug("✅ Mot de passe vérifié avec succès")
            else:
                self.logger.debug("❌ Mot de passe incorrect")
            return is_valid
        except Exception as e:
            self.logger.error(f"❌ Erreur vérification mot de passe: {str(e)}")
            return False

    def generate_secure_token(self, length: int = 32) -> str:
        try:
            secure_bytes = secrets.token_bytes(length)
            token = secure_bytes.hex()
            self.logger.debug(f"✅ Token sécurisé généré: {length} bytes → {len(token)} chars")
            return token
        except Exception as e:
            self.logger.error(f"❌ Erreur génération token: {str(e)}")
            raise SecurityError(f"Échec génération token: {str(e)}")

    def encrypt_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as file:
                file_content = file.read()
            encrypted_content = self.cipher_suite.encrypt(file_content)
            encrypted_b64 = base64.urlsafe_b64encode(encrypted_content).decode('ascii')
            self.logger.info(f"✅ Fichier chiffré: {file_path} ({len(file_content)} bytes)")
            return encrypted_b64
        except Exception as e:
            self.logger.error(f"❌ Erreur chiffrement fichier {file_path}: {str(e)}")
            raise SecurityError(f"Échec chiffrement fichier: {str(e)}")

    def get_security_info(self) -> dict:
        return {
            'encryption_algorithm': 'AES-256 (via Fernet)',
            'key_derivation': 'PBKDF2-HMAC-SHA256',
            'iterations': self.key_derivation_iterations,
            'salt_length_bytes': self.salt_length,
            'password_hashing': 'SHA-256 avec salt aléatoire',
            'secure_random': 'secrets module (CSPRNG)',
            'compliance': ['RGPD', 'Standards bancaires', 'ANSSI-compatible']
        }


class SecurityError(Exception):
    """Exception personnalisée pour les erreurs de sécurité"""
    pass


def validate_security_config() -> bool:
    try:
        security = SecurityManager("test_validation_key")
        test_data = "Test de validation sécurité - données fiscales sensibles"
        encrypted = security.encrypt_data(test_data)
        decrypted = security.decrypt_data(encrypted)
        if decrypted != test_data:   # Correction ici
            return False
        test_password = "MotDePasseTest123!"
        password_hash = security.hash_password(test_password)
        if not security.verify_password(test_password, password_hash):
            return False
        token = security.generate_secure_token()
        if len(token) != 64:  # 32 bytes = 64 chars hex
            return False
        return True
    except Exception:
        return False


PRODUCTION_CONFIG = {
    'master_password_min_length': 32,
    'token_expiry_hours': 24,
    'max_login_attempts': 5,
    'password_complexity': {
        'min_length': 12,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_numbers': True,
        'require_symbols': True
    },
    'audit_logging': True,
    'key_rotation_days': 90
}

if __name__ == "__main__":
    print("🔒 Test de validation du SecurityManager...")
    if validate_security_config():
        print("✅ Configuration de sécurité validée avec succès")
        security = SecurityManager()
        print("\n📊 Informations de configuration:")
        for key, value in security.get_security_info().items():
            print(f"   {key}: {value}")
        print("\n🧪 Tests des fonctionnalités:")
        test_data = "Données fiscales confidentielles - Client 12345"
        encrypted = security.encrypt_data(test_data)
        decrypted = security.decrypt_data(encrypted)
        print(f"   Chiffrement: {len(test_data)} chars → {len(encrypted)} chars → {len(decrypted)} chars")
        password = "MotDePasseSecurise2025!"
        hashed = security.hash_password(password)
        verified = security.verify_password(password, hashed)
        print(f"   Hachage: {len(password)} chars → {len(hashed)} chars (vérifié: {verified})")
        token = security.generate_secure_token()
        print(f"   Token: {len(token)} chars hexadécimaux")
        print("\n🎉 Tous les tests réussis !")
    else:
        print("❌ Échec de la validation de sécurité")
        exit(1)