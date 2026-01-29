import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from typing import Optional, Dict

from Util.TermStore.TermStore import TermStore
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from Util.TermStore.term import NodeTerm, VAR_TAG
from Util.TermStore import Equation


Substitution = Dict[str, NodeTerm]


def occurs_check(var_name: str, term: NodeTerm, subst: Substitution) -> bool:
    """
    Vérifie si une variable apparaît dans un terme (après application de la substitution).
    Empêche les unifications cycliques comme X = f(X).
    
    Args:
        var_name: Le nom de la variable à chercher.
        term: Le terme dans lequel chercher.
        subst: La substitution courante.
    
    Returns:
        True si la variable apparaît dans le terme, False sinon.
    """
    if term.tag == VAR_TAG:
        if term.name == var_name:
            return True
        # Si la variable est dans la substitution, vérifier récursivement
        if term.name in subst:
            return occurs_check(var_name, subst[term.name], subst)
        return False
    elif term.tag == "const":
        return False
    else:
        # C'est une fonction, vérifier tous les enfants
        return any(occurs_check(var_name, child, subst) for child in term.children)


def apply_subst(term: NodeTerm, subst: Substitution) -> NodeTerm:
    """
    Applique une substitution à un terme.
    
    Args:
        term: Le terme auquel appliquer la substitution.
        subst: La substitution à appliquer.
    
    Returns:
        Le terme avec les variables substituées.
    """
    if term.tag == VAR_TAG:
        if term.name in subst:
            # Appliquer récursivement pour les substitutions chaînées
            return apply_subst(subst[term.name], subst)
        return term
    elif term.tag == "const":
        return term
    else:
        # C'est une fonction, appliquer aux enfants
        new_children = [apply_subst(child, subst) for child in term.children]
        return NodeTerm(term.name, term.tag, new_children)


def unify(t1: NodeTerm, t2: NodeTerm, store: TermStore) -> Optional[Substitution]:
    """
    Algorithme d'unification de Robinson (version itérative).
    
    Args:
        t1: Premier terme à unifier.
        t2: Second terme à unifier.
        store: Structure de données pour stocker les équations
    
    Returns:
        La substitution unificatrice si elle existe, None sinon.
    """
    store.push(Equation(t1, t2))
    subst: Substitution = {}
    
    while not store.is_empty():
        eq = store.pop()
        left = apply_subst(eq.left, subst)
        right = apply_subst(eq.right, subst)
        
        # Cas 1: Les termes sont identiques (même nom et même tag)
        if left.name == right.name and left.tag == right.tag:
            if left.tag not in [VAR_TAG, "const"]:
                # C'est une fonction, ajouter les équations pour les enfants
                for child_left, child_right in zip(left.children, right.children):
                    store.push(Equation(child_left, child_right))
            # Sinon (const ou var identiques), rien à faire
            continue
        
        # Cas 2: Le terme gauche est une variable
        if left.tag == VAR_TAG:
            if occurs_check(left.name, right, subst):
                return None  # Échec: cycle détecté
            subst[left.name] = right
            continue
        
        # Cas 3: Le terme droit est une variable
        if right.tag == VAR_TAG:
            if occurs_check(right.name, left, subst):
                return None  # Échec: cycle détecté
            subst[right.name] = left
            continue
        
        # Cas 4: Symboles différents ou arités différentes (a remplacer par une vérification de clash)
        return None
    
    return subst