from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import text
import logging

Base = declarative_base()

class Document(Base):
    """Table des documents avec chiffrement"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(String(50), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    document_type = Column(String(50), index=True)
    content_encrypted = Column(Text)  # Contenu chiffré
    metadata_encrypted = Column(Text)  # Métadonnées chiffrées
    file_hash = Column(String(64))  # Hash SHA-256 pour intégrité
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, error
    
    # Index composé pour optimiser les requêtes
    __table_args__ = (
        Index('idx_client_type', 'client_id', 'document_type'),
        Index('idx_created_processed', 'created_at', 'processed'),
    )

class AuditLog(Base):
    """Table d'audit pour traçabilité complète"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))  # document, config, module
    resource_id = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(String(500))
    details_encrypted = Column(Text)  # Détails chiffrés
    success = Column(Boolean, default=True)

class User(Base):
    """Table des utilisateurs avec rôles"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), default='user')  # admin, manager, user, readonly
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)

class DatabaseManager:
    """Gestionnaire de base de données avec sécurité intégrée"""
    
    def __init__(self, database_url: str, security_manager=None):
        self.database_url = database_url
        self.security_manager = security_manager
        self.logger = logging.getLogger(__name__)
        
        # Configuration moteur avec pool de connexions
        self.engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Vérification connexions
            echo=False  # Mettre à True pour debug SQL
        )
        
        # Session factory
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        
        # Création des tables
        Base.metadata.create_all(self.engine)
        self.logger.info("✅ Base de données initialisée avec succès")
    
    def get_session(self):
        """Récupération d'une session de base de données"""
        return self.SessionLocal()
    
    def create_document(self, client_id: str, filename: str, content: str, 
                        document_type: str = "unknown", metadata: dict = None) -> int:
        """Création sécurisée d'un document"""
        session = self.get_session()
        try:
            # Chiffrement du contenu si security_manager disponible
            if self.security_manager:
                content_encrypted = self.security_manager.encrypt_data(content)
                metadata_encrypted = self.security_manager.encrypt_data(
                    str(metadata) if metadata else "{}"
                )
            else:
                content_encrypted = content
                metadata_encrypted = str(metadata) if metadata else "{}"
            
            # Calcul hash pour intégrité
            import hashlib
            file_hash = hashlib.sha256(content.encode()).hexdigest()
            
            document = Document(
                client_id=client_id,
                filename=filename,
                document_type=document_type,
                content_encrypted=content_encrypted,
                metadata_encrypted=metadata_encrypted,
                file_hash=file_hash
            )
            
            session.add(document)
            session.commit()
            
            doc_id = document.id
            self.logger.info(f"✅ Document {doc_id} créé pour client {client_id}")
            
            return doc_id
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"❌ Erreur création document: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_document(self, document_id: int, decrypt: bool = True) -> dict:
        """Récupération sécurisée d'un document"""
        session = self.get_session()
        try:
            document = session.query(Document).filter_by(id=document_id).first()
            
            if not document:
                return None
            
            result = {
                'id': document.id,
                'client_id': document.client_id,
                'filename': document.filename,
                'document_type': document.document_type,
                'created_at': document.created_at,
                'processed': document.processed,
                'processing_status': document.processing_status
            }
            
            # Déchiffrement si demandé et possible
            if decrypt and self.security_manager:
                try:
                    result['content'] = self.security_manager.decrypt_data(document.content_encrypted)
                    result['metadata'] = eval(self.security_manager.decrypt_data(document.metadata_encrypted))
                except Exception as e:
                    self.logger.warning(f"⚠️  Impossible de déchiffrer document {document_id}: {str(e)}")
                    result['content'] = "[CHIFFRÉ]"
                    result['metadata'] = {}
            else:
                result['content'] = document.content_encrypted
                result['metadata'] = document.metadata_encrypted
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération document {document_id}: {str(e)}")
            raise
        finally:
            session.close()
    
    def log_audit(self, user_id: str, action: str, resource_type: str = None, 
                  resource_id: str = None, details: dict = None, success: bool = True):
        """Enregistrement d'audit sécurisé"""
        session = self.get_session()
        try:
            # Chiffrement des détails
            details_encrypted = ""
            if details and self.security_manager:
                details_encrypted = self.security_manager.encrypt_data(str(details))
            
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details_encrypted=details_encrypted,
                success=success
            )
            
            session.add(audit_log)
            session.commit()
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"❌ Erreur log audit: {str(e)}")
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Vérification de l'état de la base de données"""
        try:
            session = self.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            return True
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {str(e)}")
            return False
