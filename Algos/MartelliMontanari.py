from typing import List, Union
from Util.TermStore.terme import NoeudTerme, FabriqueDeTermes, ETIQUETTE_VAR, ETIQUETTE_CONS
from Util.TermStore.TermList import TermSystem


class UnificationError(Exception):
    """Exception levée quand l'unification échoue (Clash ou Occur Check)."""
    pass

class MartelliMontanari:
    def __init__(self, system: TermSystem):
        self.system = system
        self.equations = system.equations 

    def get_variables(self, term: NoeudTerme) -> set:
        """Récupère toutes les variables d'un terme."""
        if term.etiquette == ETIQUETTE_VAR:
            return {term.nom}
        if term.etiquette == ETIQUETTE_CONS:
            return set()
        variables = set()
        for child in term.enfants:
            variables.update(self.get_variables(child))
        return variables

    def substitution(self, term: NoeudTerme, var_name: str, replacement: NoeudTerme) -> NoeudTerme:
        if term.etiquette == ETIQUETTE_VAR:
            return replacement if term.nom == var_name else term
        if term.etiquette == ETIQUETTE_CONS:
            return term
        new_children = [self.substitution(c, var_name, replacement) for c in term.enfants]
        return FabriqueDeTermes.creer_fonc(term.nom, int(term.etiquette), new_children)

    def solve(self) -> TermSystem:   
        changed = True
        print(f"--- Début de l'unification: {self.system}")

        while changed:
            changed = False
            for i in range(len(self.equations)):
                eq = self.equations[i]
                left, right = eq.left, eq.right

                # Règle 1 : DELETE (x = x)
                if left.etiquette == right.etiquette and left.nom == right.nom and left.etiquette in [ETIQUETTE_VAR, ETIQUETTE_CONS]:
                    print(f"[DELETE] Suppression de {eq}")
                    self.equations.pop(i)
                    changed = True
                    break

                # Règle 2 : DECOMPOSITION (f(s1..sn) = f(t1..tn))
                elif isinstance(left.etiquette, int) and isinstance(right.etiquette, int):
                    if left.nom == right.nom and left.etiquette == right.etiquette:
                        print(f"[DECOMPOSITION] {eq}")
                        self.equations.pop(i)
                        for s, t in zip(left.enfants, right.enfants):
                            self.system.add(s, t)
                        changed = True
                        break
                    else:
                        raise UnificationError(f"CLASH : Fonctions différentes '{left.nom}' et '{right.nom}'")

                # Règle 3 : CLASH (Types incompatibles)
                elif left.etiquette == ETIQUETTE_CONS and right.etiquette == ETIQUETTE_CONS:
                    if left.nom != right.nom:
                     raise UnificationError(f"CLASH : Constantes différentes '{left.nom}' et '{right.nom}'")
                elif (left.etiquette == ETIQUETTE_CONS and right.etiquette != ETIQUETTE_CONS and right.etiquette != ETIQUETTE_VAR) or \
                     (isinstance(left.etiquette, int) and right.etiquette == ETIQUETTE_CONS):
                    raise UnificationError(f"CLASH : Impossible d'unifier {left} (type {left.etiquette}) et {right} (type {right.etiquette})")

                # Règle 4 : ORIENT (t = x devient x = t)
                elif left.etiquette != ETIQUETTE_VAR and right.etiquette == ETIQUETTE_VAR:
                    print(f"[ORIENT] Inversion de {eq}")
                    self.equations[i].left, self.equations[i].right = right, left
                    changed = True
                    break

                elif left.etiquette == ETIQUETTE_VAR:
                    x_name = left.nom
                    vars_right = self.get_variables(right)

                    # Occur Check 
                    if x_name in vars_right and right.etiquette != ETIQUETTE_VAR:
                        raise UnificationError(f"OCCUR CHECK : La variable {x_name} apparaît dans {right}")

                    # Substitution
                    subst = False
                    for j in range(len(self.equations)):
                        if i == j: continue
                        other = self.equations[j]
                        
                        if x_name in self.get_variables(other.left) or x_name in self.get_variables(other.right):
                            print(f"[SUBSTITUTION] {x_name} -> {right} dans {other}")
                            other.left = self.substitution(other.left, x_name, right)
                            other.right = self.substitution(other.right, x_name, right)
                            subst = True
                    
                    if subst:
                        changed = True
                        break

        print("\n--- Unification réussie ---")
        return self.system