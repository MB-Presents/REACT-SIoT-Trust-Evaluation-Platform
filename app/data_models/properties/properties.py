

from typing import Any


class GenericProperty:
    def __init__(self, name: str, value: Any, description: str = None):
        self.name = name
        self.value = value
        self.description = description


class NumericProperty(GenericProperty):
    def __init__(self, name: str, value: Any, description: str = None, unit: str = None):
        super().__init__(name, value, description)
        self.unit = unit
        
        


