from .term_store import TermStore
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
    
# Exemple d'utilisation 
if __name__ == "__main__":
    storeList = ListStore()
    print(f"Etat de la structure avant ajouts : {storeList}")
    storeList.push(14)
    storeList.push(7)
    storeList.push(23)
    storeList.push(2)
    print(f"Etat de la structure après ajouts : {storeList}")
    storeList.pop()
    print(f"Etat de la structure après un pop : {storeList}")