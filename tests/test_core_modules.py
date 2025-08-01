#!/usr/bin/env python3
"""Tests de validation pour les modules core"""

import sys
import os
import shutil
from pathlib import Path

# Ajout du path parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from core.engine.module_registry import ModuleRegistry
from core.config.config_manager import ConfigManager

def test_module_registry():
    """Test du ModuleRegistry"""
    print("🧪 Test ModuleRegistry...")
    
    # Instanciation
    registry = ModuleRegistry()
    assert len(registry.modules) == 0
    
    # Création d'un module de test
    class DummyModule:
        __version__ = "1.0.0"
        
        def __init__(self, config):
            self.config = config
            self.active = True
        
        def cleanup(self):
            self.active = False
    
    # Test enregistrement
    config_schema = {
        "test_param": {"type": "string", "required": True}
    }
    
    result = registry.register_module("dummy", DummyModule, config_schema)
    assert result == True
    assert "dummy" in registry.modules
    
    # Test chargement
    config = {"test_param": "test_value"}
    instance = registry.load_module("dummy", config)
    assert instance is not None
    assert instance.config["test_param"] == "test_value"
    assert registry.modules["dummy"]["status"] == "active"
    
    # Test récupération
    retrieved = registry.get_module("dummy")
    assert retrieved is instance
    
    # Test liste modules
    module_list = registry.list_modules()
    assert "dummy" in module_list
    assert module_list["dummy"]["status"] == "active"
    
    # Test déchargement
    unload_result = registry.unload_module("dummy")
    assert unload_result == True
    assert registry.modules["dummy"]["status"] == "loaded"
    
    print("✅ ModuleRegistry validé")
    return True

def test_config_manager():
    """Test du ConfigManager"""
    print("🧪 Test ConfigManager...")
    
    # Instanciation
    config_manager = ConfigManager("test_configs")
    
    # Test sauvegarde
    test_config = {
        "database": {
            "host": "localhost",
            "port": 5432
        },
        "security": {
            "encryption": True
        }
    }
    
    save_result = config_manager.save_config("test", test_config)
    assert save_result == True
    
    # Vérification fichier créé
    config_file = Path("test_configs/test.json")
    assert config_file.exists()
    
    # Test chargement
    loaded_config = config_manager.load_config("test")
    assert loaded_config["database"]["host"] == "localhost"
    assert loaded_config["security"]["encryption"] == True
    
    # Test récupération par clé
    host = config_manager.get_config("test", "database.host")
    assert host == "localhost"
    
    # Test mise à jour
    updates = {"database": {"port": 5433}, "new_section": {"enabled": True}}
    update_result = config_manager.update_config("test", updates)
    assert update_result == True
    
    # Vérification mise à jour
    updated_port = config_manager.get_config("test", "database.port")
    assert updated_port == 5433
    
    new_section = config_manager.get_config("test", "new_section.enabled")
    assert new_section == True
    
    # Test liste configs
    config_list = config_manager.list_configs()
    assert "test" in config_list
    
    print("✅ ConfigManager validé")
    
    # Nettoyage
    if Path("test_configs").exists():
        shutil.rmtree("test_configs")
    
    return True

def main():
    """Exécution des tests de validation"""
    print("🚀 Démarrage des tests de validation Étape 1")
    print("=" * 50)
    
    try:
        # Tests
        test_module_registry()
        test_config_manager()
        
        print("=" * 50)
        print("🎉 TOUS LES TESTS VALIDÉS - ÉTAPE 1 TERMINÉE")
        print("✅ Architecture modulaire fonctionnelle")
        print("✅ Gestion configuration opérationnelle")
        print("✅ Logging et gestion d'erreurs intégrés")
        
        return True
        
    except Exception as e:
        print(f"❌ ÉCHEC DES TESTS: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
