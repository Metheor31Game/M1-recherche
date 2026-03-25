from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Iterator

T = TypeVar('T')


class TermStore(ABC, Generic[T]):
    """Interface abstraite pour stocker les équations à unifier."""
    
    @abstractmethod
    def pop(self) -> T:
        """Récupère et retire un élement"""
        ...

    # @abstractmethod
    # def remove(self, item: T) -> str:
    #     """Retire un élement donné"""
    #     ...
    
    @abstractmethod
    def push(self, item: T) -> None:
        """Ajoute un élement"""
        ...
    
    @abstractmethod
    def is_empty(self) -> bool:
        """Vérifie s'il reste des élements"""
        ...
    
    @abstractmethod
    def __len__(self) -> int:
        """Retourne le nombre d'élements"""
        ...
    
    @abstractmethod
    def __str__(self) -> str:
        """Permet d'utiliser print"""
        ...
    
    @abstractmethod
    def __repr__(self) -> str:
        """améliore l'affichage dans le shell"""
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        """Permet l'itération"""
        ...

    @abstractmethod
    def pretraitement(self, pred: 'Litteral') -> 'TermStore[T]':
        """
        Filtre le store pour ne retenir que les littéraux compatibles avec pred.
        
        On garde les littéraux qui ont :
        - Le même prédicat que pred
        - Le même arité que pred
        - Le signe opposé de pred
        
        Args:
            pred (Litteral): Le littéral de référence pour le filtrage.
        
        Returns:
            TermStore[T]: Un nouveau store contenant uniquement les littéraux compatibles.
        """
        ...