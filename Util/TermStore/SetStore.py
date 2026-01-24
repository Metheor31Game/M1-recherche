from .TermStore import TermStore
from typing import TypeVar, Generic, Iterator

T = TypeVar('T')

class SetStore(TermStore[T]):
    """Implémentation avec un ensemble (ordre non déterministe)."""
    
    def __init__(self):
        self._data: set[T] = set()
    
    def pop(self) -> T:
        return self._data.pop()
    
    def push(self, item: T) -> None:
        self._data.add(item)
    
    def is_empty(self) -> bool:
        return len(self._data) == 0
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __str__(self) -> str:
        return f"SetStore({self._data})"
    
    def __repr__(self) -> str:
        return f"SetStore(data={self._data!r}, len={len(self._data)})"

    def __iter__(self) -> Iterator[T]:
        return iter(self._data)