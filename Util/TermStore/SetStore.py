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
    
    def pretraitement(self, pred) -> 'SetStore[T]':
        """
        Filtre le store pour ne retenir que les littéraux compatibles avec pred.
        
        on garde les littéraux qui ont :
        - Le même prédicat que pred
        - Le même arité que pred
        - Le signe opposé de pred
        
        Args:
            pred: Le littéral de référence pour le filtrage.
        
        Returns:
            SetStore[T]: Un nouveau store contenant uniquement les littéraux compatibles.
        """
        nouveau_store = SetStore()
        for litteral in self._data:
            # Vérifier compatibilité : même prédicat, même arité, signe opposé
            if (litteral.predicat == pred.predicat and 
                litteral.arity == pred.arity and 
                litteral.sign != pred.sign):
                nouveau_store.push(litteral)
        return nouveau_store