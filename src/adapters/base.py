"""Abstract base class that all source adapters must implement."""
from __future__ import annotations

from abc import ABC, abstractmethod

from src.models.raw_record import RawRecord


class BaseAdapter(ABC):
    """Contract for every source adapter.

    Each adapter is responsible for exactly one source type. It must:
    - Decide whether it can handle a given path/URL (can_handle).
    - Load the source and return normalized-free RawRecord objects (load).
    - Never raise on a missing or malformed source — return [] instead.
    """

    SOURCE_NAME: str = ""  # Override in every subclass, e.g. "csv", "github"

    @abstractmethod
    def can_handle(self, path: str) -> bool:
        """Return True if this adapter can process the given path or URL.

        Args:
            path: File path or URL string to evaluate.

        Returns:
            True if this adapter should be used for the given input.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self, path: str) -> list[RawRecord]:
        """Load the source at path and return a list of RawRecord objects.

        Contract:
        - Must never raise on a missing, empty, or malformed source.
        - Returns [] (not None) on any failure.
        - All values must be raw strings — no normalization applied here.
        - Each returned record has source_name and source_path populated.

        Args:
            path: File path or URL to load.

        Returns:
            List of RawRecord objects. May be empty.
        """
        raise NotImplementedError
