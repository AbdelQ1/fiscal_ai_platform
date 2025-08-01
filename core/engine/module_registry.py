# core/engine/module_registry.py
from typing import Dict, Any, Optional
import logging
from datetime import datetime

class ModuleRegistry:
    """Gestionnaire central des modules de la plateforme"""
    
    def __init__(self):
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.configs: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🚀 ModuleRegistry initialisé")
    
    def register_module(self, name: str, module_class, config_schema: Dict[str, Any]) -> bool:
        """Enregistrement automatique des modules"""
        try:
            self.modules[name] = {
                'class': module_class,
                'schema': config_schema,
                'status': 'loaded',
                'instance': None,
                'registered_at': datetime.utcnow(),
                'version': getattr(module_class, '__version__', '1.0.0')
            }
            
            self.logger.info(f"✅ Module '{name}' enregistré avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur enregistrement module '{name}': {str(e)}")
            return False
    
    def load_module(self, name: str, config: Dict[str, Any]):
        """Chargement dynamique d'un module"""
        if name not in self.modules:
            raise ValueError(f"Module '{name}' non trouvé dans le registry")
        
        try:
            module_info = self.modules[name]
            
            # Validation de la configuration selon le schéma
            if not self._validate_config(config, module_info['schema']):
                raise ValueError(f"Configuration invalide pour le module '{name}'")
            
            # Instanciation du module
            instance = module_info['class'](config)
            
            # Mise à jour du registry
            module_info['instance'] = instance
            module_info['status'] = 'active'
            module_info['loaded_at'] = datetime.utcnow()
            module_info['config'] = config
            
            self.logger.info(f"✅ Module '{name}' chargé et actif")
            return instance
            
        except Exception as e:
            self.modules[name]['status'] = 'error'
            self.modules[name]['error'] = str(e)
            self.logger.error(f"❌ Erreur chargement module '{name}': {str(e)}")
            raise
    
    def get_module(self, name: str) -> Optional[Any]:
        """Récupération d'une instance de module"""
        if name not in self.modules:
            return None
        
        module_info = self.modules[name]
        if module_info['status'] == 'active' and module_info['instance']:
            return module_info['instance']
        
        return None
    
    def list_modules(self) -> Dict[str, Dict[str, Any]]:
        """Liste tous les modules avec leurs statuts"""
        return {
            name: {
                'status': info['status'],
                'version': info['version'],
                'registered_at': info['registered_at'],
                'loaded_at': info.get('loaded_at'),
                'has_instance': info['instance'] is not None
            }
            for name, info in self.modules.items()
        }
    
    def unload_module(self, name: str) -> bool:
        """Déchargement d'un module"""
        if name not in self.modules:
            return False
        
        try:
            module_info = self.modules[name]
            
            # Nettoyage si le module a une méthode cleanup
            if (module_info['instance'] and 
                hasattr(module_info['instance'], 'cleanup')):
                module_info['instance'].cleanup()
            
            # Réinitialisation
            module_info['instance'] = None
            module_info['status'] = 'loaded'
            module_info.pop('loaded_at', None)
            module_info.pop('config', None)
            
            self.logger.info(f"✅ Module '{name}' déchargé")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur déchargement module '{name}': {str(e)}")
            return False
    
    def _validate_config(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validation basique de la configuration"""
        # Validation simple - peut être étendue avec jsonschema
        for key, type_info in schema.items():
            if isinstance(type_info, dict) and 'required' in type_info:
                if type_info['required'] and key not in config:
                    return False
        return True
    
    def get_performance_metrics(self, name: str) -> Dict[str, Any]:
        """Récupération des métriques de performance d'un module"""
        return self.performance_metrics.get(name, {})
    
    def update_performance_metrics(self, name: str, metrics: Dict[str, Any]):
        """Mise à jour des métriques de performance"""
        if name not in self.performance_metrics:
            self.performance_metrics[name] = {}
        
        self.performance_metrics[name].update(metrics)
        self.performance_metrics[name]['last_updated'] = datetime.utcnow()

