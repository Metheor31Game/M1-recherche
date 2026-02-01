import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from typing import Optional, Dict, Tuple, List

from Util.TermStore.TermStore import TermStore
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from Util.TermStore.terme import NoeudTerme, ETIQUETTE_VAR
from Util.TermStore.TermList import Equation


# La substitution est un dictionnaire avec comme clé le nom, et valeur le terme
# Exemple : {"X" : a}
Substitution = Dict[str, NoeudTerme]

"""
Docstrings prégénérés par IA, puis modifiés ensuite pour être plus exactes.
sources utilisées : 
https://stackoverflow.com/questions/1396558/how-can-i-implement-the-unification-algorithm-in-a-language-like-java-or-c

"""

def afficher(t1: NoeudTerme, t2: NoeudTerme, store: TermStore):
    print(f"Terme 1 : {t1}")
    print(f"Terme 2 : {t2}")
    print()
    result = unify(t1, t2, SetStore(), {})
    print(result)

    if result is None:
        print("Échec de l'unification")
    else:
        print("Unification réussie")
        print("Substitution susbt :")
        for var, terme in result.items():
            print(f"  {var} -> {terme}")

def afficherAll(t1: NoeudTerme, tn: TermStore, store: TermStore):
    print("unification de ", t1, "avec un groupe de ", len(tn), " termes")
    result = unifyAll(t1, tn, store)
    print(result)

    if result is None:
        print("Échec de l'unification")
    else:
        print("Unification réussie")
        print("Substitution susbt :")
        for var, terme in result.items():
            print(f"  {var} -> {terme}")

def afficherMax(t1: NoeudTerme, tn: TermStore, store: TermStore):
    size = len(tn)
    print("unification de ", t1, "avec un groupe de ", size, " termes")
    subst, compatibles = unifyMax(t1, tn, store)
    
    print(f"\n{len(compatibles)} termes compatibles sur {size} :")
    for t in compatibles:
        print(f"  - {t}")
    
    print("\nSubstitution :")
    if not subst:
        print("  (vide)")
    else:
        for var, terme in subst.items():
            print(f"  {var} -> {terme}")


def occurs_check(var_name: str, term: NoeudTerme, subst: Substitution) -> bool:
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
    if term.etiquette == ETIQUETTE_VAR:
        if term.nom == var_name:
            return True
        # Si la variable est dans la substitution, vérifier récursivement
        if term.nom in subst:
            return occurs_check(var_name, subst[term.nom], subst)
        return False
    elif term.etiquette == "const":
        return False
    else:
        # C'est une fonction, vérifier tous les enfants
        return any(occurs_check(var_name, child, subst) for child in term.enfants)


def apply_subst(term: NoeudTerme, subst: Substitution) -> NoeudTerme:
    """
    Applique une substitution à un terme. Peux faire une substitution chainée.
    
    Args:
        term: Le terme auquel appliquer la substitution.
        subst: La substitution à appliquer.

    Example:
        >>> terme = f(X, Y)
        >>> subst = {X -> a}
        >>> apply_subst(f(X, Y), subst):
            f est une fonction :
                apply_subst(X, subst) → X ∈ subst → retourne a
                apply_subst(Y, subst) → Y ∉ subst → retourne Y
            
        Substitution chainee : 
        >>> terme = g(X)
        >>> subst = {X → Y, Y → a}
            g est une fonction : 
                >>> apply_subst(X, susbt):
                >>> X ∈ subst → subst[X] = Y
                >>> return apply_subst(Y, susbt):
                    >>> Y ∈ susbt → susbt[Y] = a
                    >>> return apply_susbt(a, susbt):
                        >>> a est un terme et n'est pas dans susbt : return a
    Returns:
        Le terme avec les variables substituées.
    """
    if term.etiquette == ETIQUETTE_VAR:

        if term.nom in subst:
            # Appliquer récursivement pour les substitutions chaînées
            return apply_subst(subst[term.nom], subst)
        return term
    elif term.etiquette == "const":
        return term
    else:
        # C'est une fonction, appliquer aux enfants
        new_children = [apply_subst(child, subst) for child in term.enfants]
        return NoeudTerme(term.nom, term.etiquette, new_children)


def unify(t1: NoeudTerme, t2: NoeudTerme, store: TermStore, subst: Substitution) -> Optional[Substitution]:
    """
    Algorithme d'unification de Robinson. Unifie uniquement deux termes ensemble. (si possible)
    
    Args:
        t1: Premier terme à unifier.
        t2: Second terme à unifier.
        store: Structure de données pour stocker les équations
        subst: Ensemble de substitutions de départ
    
    Returns:
        Le MGU s'il existe, None sinon.
    """
    store.push(Equation(t1, t2))
    
    while not store.is_empty():
        eq = store.pop()
        left = apply_subst(eq.left, subst)
        right = apply_subst(eq.right, subst)
        
        # Cas 1: Les termes sont identiques (même nom et même tag)
        if left.nom == right.nom and left.etiquette == right.etiquette:
            if left.etiquette not in [ETIQUETTE_VAR, "const"]:
                # C'est une fonction, ajouter les équations pour les enfants
                for child_left, child_right in zip(left.enfants, right.enfants):
                    store.push(Equation(child_left, child_right))
            # Sinon (const ou var identiques), rien à faire
            continue
        
        # Cas 2: Le terme gauche est une variable
        if left.etiquette == ETIQUETTE_VAR:
            if occurs_check(left.nom, right, subst):
                return None  # Échec: cycle détecté
            subst[left.nom] = right
            continue
        
        # Cas 3: Le terme droit est une variable
        if right.etiquette == ETIQUETTE_VAR:
            if occurs_check(right.nom, left, subst):
                return None  # Échec: cycle détecté
            subst[right.nom] = left
            continue
        
        # Cas 4: Symboles différents ou arités différentes (a remplacer par une vérification de clash)
        return None
    
    return subst

def unifyAll(t1: NoeudTerme, tn: TermStore, store: TermStore) -> Optional[Substitution]:
    """
    Essaie d'unifier un terme avec un ensemble d'autres termes.
    
    Les substitutions sont accumulées
    Args:
        t1: Terme principal à unifier.
        tn: Groupe de termes qui doivent être unifiés avec t1.
        store: Structure de données à utiliser pour stocker les équations.
    
    Returns:
        Le MGU s'il existe, None sinon.
    """
    subst_final: Substitution = {}
    
    while not tn.is_empty():
        t = tn.pop()
        
        # Crée un nouveau store vide pour cette unification
        new_store = type(store)()
        
        # Passe les substitutions accumulées à unify
        subst = unify(t1, t, new_store, subst_final)
        
        if subst is None:
            return None  # Échec de l'unification
        
        subst_final = subst  # unify retourne déjà la substitution complète
    
    return subst_final


def unifyMax(t1: NoeudTerme, tn: TermStore, store: TermStore) -> Tuple[Substitution, List[NoeudTerme]]:
    """
    Essaie d'unifier un terme avec le maximum de termes possibles d'un ensemble.
    
    Contrairement à unifyAll, cette fonction ne s'arrête pas au premier échec.
    Elle retourne la substitution qui unifie t1 avec le plus grand nombre de termes,
    ainsi que la liste des termes compatibles (sans doublons).
    
    Optimisation: Un seul passage en O(n), puis un second passage pour récupérer
    les termes qui auraient échoué au premier tour mais qui sont compatibles
    avec la substitution finale.
    
    Args:
        t1: Terme principal à unifier.
        tn: Groupe de termes candidats à l'unification avec t1.
        store: Structure de données à utiliser pour stocker les équations.
    
    Returns:
        Un tuple (substitution, termes_compatibles) où :
        - substitution: Le MGU pour les termes compatibles
        - termes_compatibles: Liste des termes uniques qui ont pu être unifiés avec t1
    """
    # Extraire tous les termes de tn (en évitant les doublons)
    termes_vus: Dict[str, NoeudTerme] = {}
    while not tn.is_empty():
        t = tn.pop()
        key = repr(t)
        if key not in termes_vus:
            termes_vus[key] = t
    
    # Premier passage : accumulation gloutonne
    subst_courant: Substitution = {}
    termes_compatibles: Dict[str, NoeudTerme] = {}
    termes_echoues: Dict[str, NoeudTerme] = {}
    
    for key, t in termes_vus.items():
        new_store = type(store)()
        subst = unify(t1, t, new_store, subst_courant.copy())
        
        if subst is not None:
            subst_courant = subst
            termes_compatibles[key] = t
        else:
            termes_echoues[key] = t
    
    # Second passage : réessayer les termes échoués avec la substitution finale
    # (certains auraient pu échouer à cause de l'ordre)
    for key, t in termes_echoues.items():
        new_store = type(store)()
        subst = unify(t1, t, new_store, subst_courant.copy())
        
        if subst is not None:
            subst_courant = subst
            termes_compatibles[key] = t
    
    return subst_courant, list(termes_compatibles.values())

        

