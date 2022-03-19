from abc import ABC, abstractmethod


class Script(ABC):
    """Abstract class of Script-object."""

    _name = "Script's name"
    _description = "Script's description"
    _author = "Script's author"

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def author(self):
        return self._author

    @abstractmethod
    def run(self):
        """Runs Script job."""
        pass
