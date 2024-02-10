import json
from pathlib import Path
from typing import Any, List

REGISTRY_DIR = Path(__file__).parent / "_registry"


class RegistryNotFoundError(Exception):
    pass


class Registry:
    def get(self, key: str, raise_on_not_found: bool = False) -> Any:
        raise NotImplementedError

    def set(self, key: str, value: Any):
        raise NotImplementedError

    def delete(self, key: str):
        raise NotImplementedError

    def list(self) -> List[str]:
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class JsonFileRegistry(Registry):
    def __init__(self, name: str):
        self.name = name
        if not REGISTRY_DIR.exists():
            REGISTRY_DIR.mkdir(exist_ok=True, parents=True)
        self.registry_file = REGISTRY_DIR / (self.name + ".json")
        if not self.registry_file.exists():
            with open(self.registry_file, "w") as file:
                json.dump({}, file)
        with open(self.registry_file, "r") as file:
            self.registry_data: dict[str, Any] = json.load(file)

    def get(self, key: str, raise_on_not_found: bool = False) -> Any | None:
        with open(self.registry_file, "r") as file:
            self.registry_data: dict[str, Any] = json.load(file)
        data = self.registry_data.get(key)
        if raise_on_not_found and data is None:
            raise RegistryNotFoundError(key)
        return data

    def set(self, key: str, value: Any):
        self.registry_data[key] = value
        # persist
        with open(self.registry_file, "w") as file:
            json.dump(self.registry_data, file)

    def delete(self, key: str):
        with open(self.registry_file, "r") as file:
            self.registry_data: dict[str, Any] = json.load(file)
        self.registry_data.pop(key)
        # persist
        with open(self.registry_file, "w") as file:
            json.dump(self.registry_data, file)

    def list(self) -> List[str]:
        with open(self.registry_file, "r") as file:
            self.registry_data: dict[str, Any] = json.load(file)
        return list(self.registry_data.keys())

    def clear(self):
        with open(self.registry_file, "w") as file:
            json.dump({}, file)
        self.registry_data = {}
