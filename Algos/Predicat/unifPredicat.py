import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.Litteral.Litteral import Litteral
from Algos.Robinson.robinson import unifyAll
from Util.TermStore.TermStore import TermStore
from Util.TermStore.SetStore import SetStore
from Util.TermStore.DictStore import DictStore
from Util.TermStore.ListStore import ListStore
from Util.TermStore.terme import NoeudTerme

from typing import Optional, Dict, Iterable


def unifPredicat(p1: Litteral, p2: Litteral, algo):
    """
    Essaie d'unifier deux prédicats ensemble.
    
    Args:
        p1: Littéral 1.
        p2: Littéral 2.
        algo: Chaine de caractère qui appellera l'algo d'unification que l'on souhaite (Robinson, MM etc).
    
    Returns:
        Substitution commune entre p1 et p2 si possible, None sinon.
    """
    # vérification du signe
    if p1.sign == p2.sign:
        return None
    
    # vérification du nom
    if p1.predicat != p2.predicat:
        return None
    
    # vérification de l'arité
    if p1.arity != p2.arity:
        return None
    
    # appel de la fonction d'unification
    if algo == "Robinson":
        subst = {}
        
        # Pour chaque paire de termes (t1, t2), unifier en accumulant les substitutions
        for t1, t2 in zip(p1.enfants, p2.enfants):
            # Créer un TermStore avec un seul terme (t2)
            termes = SetStore()
            termes.push(t2)
            
            # Utiliser unifyAll avec la substitution accumulée
            subst = unifyAll(t1, termes, SetStore(), subst)
            
            if subst is None:
                return None
        
        return subst
    
    return None

def rechercherUnifiablesSimple(p1: Litteral, preds: TermStore[Litteral], algo: str = "Robinson") -> Dict[Litteral, Dict]:
    """
    Recherche "bêtement" tous les littéraux unifiables avec p1 dans un ensemble de littéraux.
    
    Parcourt tous les littéraux de l'ensemble et teste l'unification avec p1.
    Chaque test d'unification est indépendant (substitution vide au départ).
    
    Args:
        p1 (Litteral): Le littéral de référence à unifier.
        preds (TermStore[Litteral]): Ensemble de littéraux candidats.
        algo (str): Algorithme d'unification à utiliser (par défaut "Robinson").
    
    Returns:
        Dict[Litteral, Dict]: Dictionnaire associant chaque littéral unifiable à sa substitution.
                              Retourne {} si aucun littéral n'est unifiable.
    
    Example:
        >>> p1 = Litteral("P", [X, Y], True)
        >>> preds = SetStore()
        >>> preds.push(Litteral("P", [a, b], False))
        >>> result = rechercherUnifiablesSimple(p1, preds)
        >>> # result = {¬P(a, b): {X/a, Y/b}}
    """
    result = {}
    for p in preds:
        subst = unifPredicat(p1, p, algo)
        if subst is not None:
            result[p] = subst
    return result

def rechercherUnifiablesOptimise(p1: Litteral, preds: TermStore[Litteral], algo: str = "Robinson") -> Dict[Litteral, Dict]:
    """
    Recherche optimisée qui exploite l'indexation de DictStore si disponible.
    Si un autre store est passé, se rabat sur la méthode simple.
    """
    result = {}
    
    # Si c'est notre dictionnaire optimisé, on ne parcourt QUE les candidats valides
    if isinstance(preds, DictStore):
        candidats = preds.get_candidats_resolution(p1)
    else:
        # Fallback pour ListStore et SetStore : on parcourt tout le monde
        candidats = preds
        
    for p in candidats:
        subst = unifPredicat(p1, p, algo)
        if subst is not None:
            result[p] = subst
            
    return result


def afficherResultat(p1: Litteral, resultat: dict):
    """
    Affiche le résultat correctement pour que ce soit plus lisible
    """
    print("\n=== Resultats de la recherche d'unification ===")
    print(f"Litteral de reference : {p1}")

    if not resultat:
        print("Aucun litteral unifiable trouve.")
        return

    for i, (litteral, substitution) in enumerate(resultat.items(), start=1):
        print(f"\n{i}. Litteral unifiable : {litteral}")

        if not substitution:
            print("   Substitution : vide")
            continue

        print("   Substitution :")
        for var, terme_subst in substitution.items():
            print(f"     {var} -> {terme_subst}")



    
