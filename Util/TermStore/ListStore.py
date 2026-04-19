from .TermStore import TermStore
from typing import TypeVar, Generic, Iterator

T = TypeVar('T')

class ListStore(TermStore[T]):
    """Implémentation avec une liste"""
    
    def __init__(self):
        self._data: list[T] = []
    
    def pop(self) -> T:
        return self._data.pop()
    
    def push(self, item: T) -> None:
        self._data.append(item)
    
    def is_empty(self) -> bool:
        return len(self._data) == 0
    
    def __len__(self) -> int:
        return len(self._data)
    
    def __str__(self) -> str:
        return f"ListStore({self._data})"
    
    def __repr__(self) -> str:
        return f"ListStore(data={self._data!r}, len={len(self._data)})"
    
    def __iter__(self) -> Iterator[T]:
        return iter(self._data)
    
    def pretraitement(self, pred) -> 'ListStore[T]':
        """
        Filtre le store pour ne retenir que les littéraux compatibles avec pred.
        
        Seuls sont gardés les littéraux qui ont :
        - Le même prédicat que pred
        - Le même arité que pred
        - Le signe opposé de pred
        
        Args:
            pred: Le littéral de référence pour le filtrage.
        
        Returns:
            ListStore[T]: Un nouveau store contenant uniquement les littéraux compatibles.
        """
        self._data = [
        litteral for litteral in self._data
        if (litteral.predicat == pred.predicat
            and litteral.arity == pred.arity
            and litteral.sign != pred.sign)
        ]
    
    