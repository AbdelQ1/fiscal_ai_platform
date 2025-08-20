# core/engine/module_registry.py
"""
ModuleRegistry – registre dynamique des plug-ins.

CORRECTIFS-CLÉS
1.  config devient OPTIONNEL  →  les tests peuvent appeler
       registry.register_module("dummy")
    sans second argument.
2.  Alias public  self.modules  conservé.
3.  Support intégré du module factice « dummy ».
4.  Alias rétro-compat  load_module() / unload_module().
"""

from __future__ import annotations

import logging
from importlib import import_module
from types import ModuleType
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ModuleRegistry:
    """Registre dynamique des modules métier."""

    # ------------------------------------------------------------------ #
    #  INITIALISATION
    # ------------------------------------------------------------------ #
    def __init__(self) -> None:
        self._modules: Dict[str, Dict[str, Any]] = {}
        self.modules = self._modules          # ← alias public (anciennes suites)
        self._configs: Dict[str, Dict[str, Any]] = {}
        logger.info("🚀 ModuleRegistry initialisé")

    # ------------------------------------------------------------------ #
    #  ENREGISTREMENT / CHARGEMENT
    # ------------------------------------------------------------------ #
    def register_module(
        self,
        module_name: str,
        module_class: Optional[Any] = None,
        config_schema: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Enregistre une classe de module.

        • module_name   : nom du module.
        • module_class  : classe du module à enregistrer.
        • config_schema : schéma JSON optionnel.
        """

        if module_name in self._modules:
            logger.warning("⚠️  Module « %s » déjà enregistré", module_name)
            return False

        try:
            self._modules[module_name] = {
                "class": module_class,
                "instance": None,
                "status": "registered",
                "config_schema": config_schema or {}
            }
            logger.info("✅ Module '%s' enregistré", module_name)
            return True

        except Exception as exc:                           # pragma: no cover
            logger.error("❌ Échec d'enregistrement « %s » : %s", module_name, exc)
            return False

    def load_module(
        self,
        module_name: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Charge et instancie un module enregistré."""
        if module_name not in self._modules:
            logger.error("❌ Module '%s' non enregistré", module_name)
            return None

        module_info = self._modules[module_name]
        if module_info["instance"] is not None:
            return module_info["instance"]

        try:
            module_class = module_info["class"]
            instance = module_class(config or {})
            module_info["instance"] = instance
            module_info["status"] = "active"
            self._configs[module_name] = config or {}
            logger.info("✅ Module '%s' chargé et actif", module_name)
            return instance

        except Exception as exc:
            logger.error("❌ Échec chargement « %s » : %s", module_name, exc)
            return None

    def unload_module(self, module_name: str) -> bool:
        """Décharge un module actif.""" 
        if module_name not in self._modules:
            return False

        module_info = self._modules[module_name]
        if module_info["instance"] is not None:
            try:
                if hasattr(module_info["instance"], "cleanup"):
                    module_info["instance"].cleanup()
            except Exception as exc:
                logger.warning("⚠️  Erreur cleanup '%s': %s", module_name, exc)
            
            module_info["instance"] = None
            module_info["status"] = "loaded"
            logger.info("✅ Module '%s' déchargé", module_name)

        return True
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    #  DÉSENREGISTREMENT
    # ------------------------------------------------------------------ #
    def unregister_module(self, module_name: str) -> bool:
        """Désenregistre complètement un module."""
        if module_name in self._modules:
            # Décharger d'abord si nécessaire
            self.unload_module(module_name)
            # Supprimer complètement
            self._modules.pop(module_name)
            self._configs.pop(module_name, None)
            logger.info("✅ Module '%s' désenregistré", module_name)
            return True
        return False

    # ------------------------------------------------------------------ #
    #  ACCÈS & UTILITAIRES
    # ------------------------------------------------------------------ #
    def get_module(self, module_name: str):
        """Retourne l'instance d'un module."""
        module_info = self._modules.get(module_name)
        return module_info["instance"] if module_info else None

    def list_modules(self) -> Dict[str, Dict[str, Any]]:
        """Retourne la liste des modules avec leur statut."""
        result = {}
        for name, info in self._modules.items():
            result[name] = {
                "status": info["status"],
                "class": info["class"].__name__ if info["class"] else None,
                "instance": info["instance"] is not None
            }
        return result

    def get_module_status(self, module_name: str) -> str:
        return "loaded" if module_name in self._modules else "absent"

