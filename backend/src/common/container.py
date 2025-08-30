"""Dependency injection container for the application."""

import logging
from typing import Dict, Any, TypeVar, Type

T = TypeVar("T")


class DIContainer:
    """Simple dependency injection container."""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)

    def register_singleton(self, service_type: Type[T], instance: T) -> None:
        """Register a singleton instance."""
        key = self._get_key(service_type)
        self._singletons[key] = instance
        self._logger.info(f"Registered singleton: {key}")

    def register_transient(self, service_type: Type[T], factory: callable) -> None:
        """Register a transient service factory."""
        key = self._get_key(service_type)
        self._services[key] = factory
        self._logger.info(f"Registered transient: {key}")

    def get(self, service_type: Type[T]) -> T:
        """Get a service instance."""
        key = self._get_key(service_type)

        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]

        # Check transient services
        if key in self._services:
            factory = self._services[key]
            return factory()

        raise ValueError(f"Service not registered: {key}")

    def _get_key(self, service_type: Type) -> str:
        """Get the key for a service type."""
        return f"{service_type.__module__}.{service_type.__name__}"


# Global container instance
container = DIContainer()
