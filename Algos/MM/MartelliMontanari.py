from Util.TermStore.terme import ETIQUETTE_VAR, ETIQUETTE_CONS
from Util.TermStore.StructureMM.TermeAbstrait import TermeAbstrait
from Util.TermStore.TermList import TermSystem, Equation

TYPE_FONC = "fonc"
TYPE_PRED = "pred"


class UnificationError(Exception):
    """Exception levée quand l'unification échoue (Clash ou Occur Check)."""
    pass


class MartelliMontanari:
   
    def __init__(self, system: TermSystem):
        self.system    = system
        self.equations = list(system.equations)

    def solve(self) -> TermSystem:
        """
        Résout le système d'équations par l'algorithme de Martelli-Montanari.

        Returns:
            TermSystem : système résolu
        Raises:
            UnificationError : si l'unification échoue (Clash ou Occur Check)
        """
        changed = True

        while changed:
            changed = False

            for i in range(len(self.equations)):
                eq          = self.equations[i]
                left, right = eq.left, eq.right

                # Règle 1 : DELETE (t = t)
                if (left.nom == right.nom
                        and left.typeNoeud == right.typeNoeud
                        and left.typeNoeud in [ETIQUETTE_VAR, ETIQUETTE_CONS]):
                    self.equations.pop(i)
                    changed = True
                    break

                # Règle 2 : DECOMPOSE f(s1..sn) = f(t1..tn)
                elif (left.typeNoeud in [TYPE_FONC, TYPE_PRED]
                      and right.typeNoeud in [TYPE_FONC, TYPE_PRED]):
                    if left.nom != right.nom or left.arite != right.arite:
                        raise UnificationError(
                            f"CLASH : symboles différents '{left.nom}' et '{right.nom}'"
                        )
                    self.equations.pop(i)
                    for s, t in zip(left.enfants, right.enfants):
                        self.equations.append(Equation(s, t))
                    changed = True
                    break

                # Règle 3 : CLASH (types incompatibles)
                elif (left.typeNoeud == ETIQUETTE_CONS
                      and right.typeNoeud == ETIQUETTE_CONS):
                    if left.nom != right.nom:
                        raise UnificationError(
                            f"CLASH : constantes différentes '{left.nom}' et '{right.nom}'"
                        )

                elif ((left.typeNoeud == ETIQUETTE_CONS
                       and right.typeNoeud not in [ETIQUETTE_CONS, ETIQUETTE_VAR])
                      or (left.typeNoeud in [TYPE_FONC, TYPE_PRED]
                          and right.typeNoeud == ETIQUETTE_CONS)):
                    raise UnificationError(
                        f"CLASH : impossible d'unifier '{left}' et '{right}'"
                    )

                # Règle 4 : ORIENT (t = x devient x = t)
                elif (left.typeNoeud != ETIQUETTE_VAR
                      and right.typeNoeud == ETIQUETTE_VAR):
                    self.equations[i].left  = right
                    self.equations[i].right = left
                    changed = True
                    break

                # SUBSTITUTE (x = t)
                elif left.typeNoeud == ETIQUETTE_VAR:
                    x_name = left.nom

                    # Règle 5 : Occur Check 
                    vars_right = right.getVariables()
                    if x_name in vars_right and right.typeNoeud != ETIQUETTE_VAR:
                        raise UnificationError(
                            f"OCCUR CHECK : '{x_name}' apparaît dans '{right}'"
                        )

                    # Substitution dans toutes les autres équations
               
                    subst = False
                    for j in range(len(self.equations)):
                        if i == j:
                            continue
                        other = self.equations[j]
                        if (x_name in other.left.getVariables()
                                or x_name in other.right.getVariables()):
                            other.left  = other.left.substituer(x_name, right)
                            other.right = other.right.substituer(x_name, right)
                            subst = True

                    if subst:
                        changed = True
                        break

        self.system.equations = list(self.equations)
        return self.system