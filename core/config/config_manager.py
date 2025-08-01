import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Import conditionnel de YAML
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

class ConfigManager:
    """Gestionnaire de configuration avec support JSON et YAML"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True, parents=True)
        self.configs: Dict[str, Dict[str, Any]] = {}
        self._config_history: Dict[str, list] = {}
        
        # Configuration logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"📁 ConfigManager initialisé - Répertoire: {self.config_dir}")
    
    def load_config(self, config_name: str, file_format: str = "json") -> Dict[str, Any]:
        """Chargement configuration depuis fichier"""
        try:
            config_data = {}
            
            if file_format.lower() == "json":
                config_path = self.config_dir / f"{config_name}.json"
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                else:
                    self.logger.warning(f"⚠️  Fichier '{config_name}.json' non trouvé")
                    return {}
            
            elif file_format.lower() == "yaml":
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML n'est pas installé. Utilisez: pip install pyyaml")
                
                config_path = self.config_dir / f"{config_name}.yaml"
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f) or {}
                else:
                    self.logger.warning(f"⚠️  Fichier '{config_name}.yaml' non trouvé")
                    return {}
            else:
                raise ValueError(f"Format non supporté: {file_format}")
            
            # Sauvegarde en mémoire
            self.configs[config_name] = config_data
            
            # Historique
            if config_name not in self._config_history:
                self._config_history[config_name] = []
            
            self._config_history[config_name].append({
                'timestamp': datetime.utcnow(),
                'action': 'loaded',
                'file_format': file_format
            })
            
            self.logger.info(f"✅ Configuration '{config_name}' chargée depuis {file_format.upper()}")
            return config_data
        
        except Exception as e:
            self.logger.error(f"❌ Erreur chargement configuration '{config_name}': {str(e)}")
            return {}
    
    def save_config(self, config_name: str, config_data: Dict[str, Any], 
                   file_format: str = "json", backup: bool = True) -> bool:
        """Sauvegarde configuration vers fichier"""
        try:
            # Backup de la configuration existante si demandé
            if backup:
                self._backup_config(config_name, file_format)
            
            if file_format.lower() == "json":
                config_path = self.config_dir / f"{config_name}.json"
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            elif file_format.lower() == "yaml":
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML n'est pas installé. Utilisez: pip install pyyaml")
                
                config_path = self.config_dir / f"{config_name}.yaml"
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_data, f, default_flow_style=False, 
                              allow_unicode=True, indent=2)
            else:
                raise ValueError(f"Format non supporté: {file_format}")
            
            # Mise à jour mémoire et historique
            self.configs[config_name] = config_data
            
            if config_name not in self._config_history:
                self._config_history[config_name] = []
            
            self._config_history[config_name].append({
                'timestamp': datetime.utcnow(),
                'action': 'saved',
                'file_format': file_format,
                'backup_created': backup
            })
            
            self.logger.info(f"✅ Configuration '{config_name}' sauvegardée en {file_format.upper()}")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Erreur sauvegarde configuration '{config_name}': {str(e)}")
            return False
    
    def get_config(self, config_name: str, key_path: Optional[str] = None) -> Any:
        """Récupération d'une configuration ou d'une clé spécifique"""
        if config_name not in self.configs:
            self.logger.warning(f"⚠️  Configuration '{config_name}' non chargée")
            return None
        
        config = self.configs[config_name]
        
        if key_path is None:
            return config
        
        # Navigation dans la configuration avec point notation
        keys = key_path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            self.logger.warning(f"⚠️  Clé '{key_path}' non trouvée dans configuration '{config_name}'")
            return None
    
    def update_config(self, config_name: str, updates: Dict[str, Any], 
                      save_to_file: bool = True) -> bool:
        """Mise à jour d'une configuration existante"""
        try:
            if config_name not in self.configs:
                self.configs[config_name] = {}
            
            # Merge récursif
            self._deep_merge(self.configs[config_name], updates)
            
            # Sauvegarde automatique si demandée
            if save_to_file:
                return self.save_config(config_name, self.configs[config_name])
            
            self.logger.info(f"✅ Configuration '{config_name}' mise à jour en mémoire")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Erreur mise à jour configuration '{config_name}': {str(e)}")
            return False
    
    def list_configs(self) -> Dict[str, Dict[str, Any]]:
        """Liste toutes les configurations avec métadonnées"""
        result = {}
        
        for config_name in self.configs:
            history = self._config_history.get(config_name, [])
            result[config_name] = {
                'loaded_in_memory': True,
                'history_entries': len(history),
                'last_activity': (
                    history[-1]['timestamp'] if history else None
                )
            }
        
        return result
    
    def _backup_config(self, config_name: str, file_format: str):
        """Création d'un backup d'une configuration"""
        try:
            backup_dir = self.config_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{config_name}_{timestamp}.{file_format}"
            
            source_path = self.config_dir / f"{config_name}.{file_format}"
            backup_path = backup_dir / backup_name
            
            if source_path.exists():
                import shutil
                shutil.copy2(source_path, backup_path)
                self.logger.info(f"📦 Backup créé: {backup_name}")
        
        except Exception as e:
            self.logger.warning(f"⚠️  Impossible de créer le backup: {str(e)}")
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Merge récursif de dictionnaires"""
        for key, value in source.items():
            if (
                key in target and 
                isinstance(target[key], dict) and 
                isinstance(value, dict)
            ):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
