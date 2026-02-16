import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.Litteral.Litteral import Litteral
from Algos.Robinson.robinson import unifyAll
from Util.TermStore.SetStore import SetStore
from Util.TermStore.terme import NoeudTerme

from typing import Optional, Dict


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
    
