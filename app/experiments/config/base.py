from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


@dataclass(frozen=True)
class BaseConfiguration:
    """Base class for all configuration objects."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def validate(self) -> None:
        """Validate configuration values."""
        pass


class ConfigurationValidationError(Exception):
    """Raised when configuration validation fails."""
    pass