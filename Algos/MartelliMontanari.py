from typing import List, Union
from Util.TermStore.term import NodeTerm, TermFactory, VAR_TAG, CONST_TAG
from Util.TermStore.TermList import TermSystem


class UnificationError(Exception):
    """Exception levée quand l'unification échoue (Clash ou Occur Check)."""
    pass

class MartelliMontanari:
    def __init__(self, system: TermSystem):
        self.system = system
        self.equations = system.equations 

    def get_variables(self, term: NodeTerm) -> set:
        """Récupère toutes les variables d'un terme."""
        if term.tag == VAR_TAG:
            return {term.name}
        if term.tag == CONST_TAG:
            return set()
        variables = set()
        for child in term.children:
            variables.update(self.get_variables(child))
        return variables

    def substitution(self, term: NodeTerm, var_name: str, replacement: NodeTerm) -> NodeTerm:
        if term.tag == VAR_TAG:
            return replacement if term.name == var_name else term
        if term.tag == CONST_TAG:
            return term
        new_children = [self.substitution(c, var_name, replacement) for c in term.children]
        return TermFactory.create_func(term.name, term.tag, new_children)

    def solve(self) -> TermSystem:   
        changed = True
        print(f"--- Début de l'unification: {self.system}")

        while changed:
            changed = False
            for i in range(len(self.equations)):
                eq = self.equations[i]
                left, right = eq.left, eq.right

                # Règle 1 : DELETE (x = x)
                if left.tag == right.tag and left.name == right.name and left.tag in [VAR_TAG, CONST_TAG]:
                    print(f"[DELETE] Suppression de {eq}")
                    self.equations.pop(i)
                    changed = True
                    break

                # Règle 2 : DECOMPOSITION (f(s1..sn) = f(t1..tn))
                elif isinstance(left.tag, int) and isinstance(right.tag, int):
                    if left.name == right.name and left.tag == right.tag:
                        print(f"[DECOMPOSITION] {eq}")
                        self.equations.pop(i)
                        for s, t in zip(left.children, right.children):
                            self.system.add(s, t)
                        changed = True
                        break
                    else:
                        raise UnificationError(f"CLASH : Fonctions différentes '{left.name}' et '{right.name}'")

                # Règle 3 : CLASH (Types incompatibles)
                elif left.tag == CONST_TAG and right.tag == CONST_TAG:
                    if left.name != right.name:
                     raise UnificationError(f"CLASH : Constantes différentes '{left.name}' et '{right.name}'")
                elif (left.tag == CONST_TAG and right.tag != CONST_TAG and right.tag != VAR_TAG) or \
                     (isinstance(left.tag, int) and right.tag == CONST_TAG):
                    raise UnificationError(f"CLASH : Impossible d'unifier {left} (type {left.tag}) et {right} (type {right.tag})")

                # Règle 4 : ORIENT (t = x devient x = t)
                elif left.tag != VAR_TAG and right.tag == VAR_TAG:
                    print(f"[ORIENT] Inversion de {eq}")
                    self.equations[i].left, self.equations[i].right = right, left
                    changed = True
                    break

                elif left.tag == VAR_TAG:
                    x_name = left.name
                    vars_right = self.get_variables(right)

                    # Occur Check 
                    if x_name in vars_right and right.tag != VAR_TAG:
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