"""
BaseGenerator: abstract base class for all entity generators.
Each generator receives a ProjectProfile, implements generate(), returns rows.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, NamedTuple

import pandas as pd


class GenerationResult(NamedTuple):
    row_count: int
    output_path: Path


class BaseGenerator(ABC):

    def __init__(self, profile):
        self.profile = profile
        self.s = profile.settings

    def setting(self, category: str, key: str) -> str:
        return self.s.get(category, {}).get(key, "")

    @abstractmethod
    def generate(self, stores: List[Dict]) -> List[Dict]:
        """Return list of output row dicts. No file I/O here."""
        ...

    @property
    @abstractmethod
    def columns(self) -> List[str]:
        """Ordered list of output CSV column names."""
        ...

    def write(self, rows: List[Dict], path: Path) -> GenerationResult:
        df = pd.DataFrame(rows, columns=self.columns)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        return GenerationResult(row_count=len(df), output_path=path)
