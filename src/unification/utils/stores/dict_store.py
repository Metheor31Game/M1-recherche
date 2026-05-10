from typing import TypeVar, Iterator, Dict, Tuple, List
from .term_store import TermStore
from ..logique.litteral import Litteral

class DictStore(TermStore[Litteral]):
    def __init__(self):
        # Structure : { "Predicat": ( [Littéraux Positifs], [Littéraux Négatifs] ) }
        self._data: Dict[str, Tuple[List[Litteral], List[Litteral]]] = {}
        self._size = 0

    def push(self, item: Litteral) -> None:
        # Initialiser le tuple de listes si le prédicat n'existe pas encore
        if item.predicat not in self._data:
            self._data[item.predicat] = ([], [])
        
        # item.sign == True (Positif), False (Négatif)
        if item.sign:
            self._data[item.predicat][0].append(item)
        else:
            self._data[item.predicat][1].append(item)
            
        self._size += 1

    def pop(self) -> Litteral:
        if self.is_empty():
            raise IndexError("pop from empty DictStore")
        
        # On cherche le premier élément disponible et on le retire
        for key, (pos_list, neg_list) in self._data.items():
            if pos_list:
                self._size -= 1
                return pos_list.pop()
            if neg_list:
                self._size -= 1
                return neg_list.pop()

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Litteral]:
        # Permet à "for p in store:" de fonctionner comme avec SetStore/ListStore
        for pos_list, neg_list in self._data.values():
            for item in pos_list:
                yield item
            for item in neg_list:
                yield item

    def __str__(self) -> str:
        return str(self._data)
        
    def __repr__(self) -> str:
        return f"DictStore(size={self._size}, keys={list(self._data.keys())})"

    # --- METHODE D'OPTIMISATION ---
    def get_candidats_resolution(self, pred: Litteral) -> Iterator[Litteral]:
        """
        Retourne en O(1) uniquement les littéraux pertinents pour la résolution :
        - Même prédicat
        - Signe opposé
        - Même arité
        """
        if pred.predicat not in self._data:
            return iter([]) # Aucun candidat
        
        pos_list, neg_list = self._data[pred.predicat]
        
        # Si pred est positif, on veut unifier avec les négatifs (et inversement)
        candidats = neg_list if pred.sign else pos_list
        
        # On retourne un générateur qui filtre aussi sur l'arité
        return (c for c in candidats if c.arity == pred.arity)
