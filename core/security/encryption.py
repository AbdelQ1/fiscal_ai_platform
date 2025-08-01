from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
import logging

class SecurityManager:
    """Gestionnaire de sécurité avec chiffrement AES-256"""
    
    def __init__(self, master_password: str = None):
        self.master_password = master_password or os.getenv('MASTER_PASSWORD', 'fiscal_ai_default_key_2025')
        self.key = self._derive_key(self.master_password)
        self.cipher = Fernet(self.key)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🔒 SecurityManager initialisé avec chiffrement AES-256")
    
    def _derive_key(self, password: str) -> bytes:
        """Dérivation de clé à partir du mot de passe maître"""
        password_bytes = password.encode()
        # En production, utiliser un salt unique par installation
        salt = b'fiscal_ai_platform_salt_2025'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Chiffrement des données sensibles"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"❌ Erreur chiffrement: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Déchiffrement des données"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"❌ Erreur déchiffrement: {str(e)}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hachage sécurisé des mots de passe"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérification des mots de passe"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
