from typing import List, Union
from unification.utils.logique.terme import NoeudTerme, FabriqueDeTermes, ETIQUETTE_VAR, ETIQUETTE_CONS
from unification.utils.stores import TermSystem
from unification.utils.logique.litteral import Litteral


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
        #print(f"--- Début de l'unification: {self.system}")

        while changed:
            changed = False
            for i in range(len(self.equations)):
                eq = self.equations[i]
                left, right = eq.left, eq.right

                # Règle 1 : DELETE (x = x)
                if left.etiquette == right.etiquette and left.nom == right.nom and left.etiquette in [ETIQUETTE_VAR, ETIQUETTE_CONS]:
                    #print(f"[DELETE] Suppression de {eq}")
                    self.equations.pop(i)
                    changed = True
                    break
                # Règle 2 : ORIENT (t = x devient x = t)
                elif left.etiquette != ETIQUETTE_VAR and right.etiquette == ETIQUETTE_VAR:
                    #print(f"[ORIENT] Inversion de {eq}")
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
                            #print(f"[SUBSTITUTION] {x_name} -> {right} dans {other}")
                            other.left = self.substitution(other.left, x_name, right)
                            other.right = self.substitution(other.right, x_name, right)
                            subst = True
                    
                    if subst:
                        changed = True
                        break

                # Règle 3 : DECOMPOSITION (f(s1..sn) = f(t1..tn))
                elif isinstance(left.etiquette, int) and isinstance(right.etiquette, int):
                    if left.nom == right.nom and left.etiquette == right.etiquette:
                        #print(f"[DECOMPOSITION] {eq}")
                        self.equations.pop(i)
                        for s, t in zip(left.enfants, right.enfants):
                            self.system.add(s, t)
                        changed = True
                        break
                    else:
                        raise UnificationError(f"CLASH : Fonctions différentes '{left.nom}' et '{right.nom}'")

                # Règle 4 : CLASH (Types incompatibles)
                elif left.etiquette == ETIQUETTE_CONS and right.etiquette == ETIQUETTE_CONS:
                    if left.nom != right.nom:
                     raise UnificationError(f"CLASH : Constantes différentes '{left.nom}' et '{right.nom}'")
                elif (left.etiquette == ETIQUETTE_CONS and right.etiquette != ETIQUETTE_CONS and right.etiquette != ETIQUETTE_VAR) or \
                     (isinstance(left.etiquette, int) and right.etiquette == ETIQUETTE_CONS):
                    raise UnificationError(f"CLASH : Impossible d'unifier {left} et {right} (types incompatibles)")

                
        #print("\n--- Unification réussie ---")
        return self.system
    
# Exemple d'utilisation
if __name__ == "__main__":
    from unification.utils.logique.litteral import Litteral
    litteraux = [
        Litteral.from_string("P(X,X)"),
        Litteral.from_string("P(X,Y)"),
        Litteral.from_string("P(g(a,X),Y)"),
        Litteral.from_string("P(g(X,b),X)"),
        Litteral.from_string("P(f(a),Z)"),
        Litteral.from_string("P(a,b)"),
        Litteral.from_string("P(b,b)"),
        Litteral.from_string("P(X,f(b))"),
        Litteral.from_string("P(Y,b)")
    ]

    litteral_recherche = Litteral.from_string("¬P(f(Y),Z)")

    for litteral in litteraux:
        if litteral.predicat == litteral_recherche.predicat and litteral.sign != litteral_recherche.sign and litteral.arity == litteral_recherche.arity:
            system = TermSystem()
            for t1, t2 in zip(litteral.enfants, litteral_recherche.enfants):
                system.add(t1, t2)
            mm = MartelliMontanari(system)
            try:
                unificateur = mm.solve()
                if unificateur.is_empty():
                    print("  → Succès (termes identiques, système vide)\n")
                else:
                    print("  → Succès, unificateur :")
                    for eq in unificateur.equations:
                        print(f"      {eq.left} = {eq.right}")
                    print()
            except UnificationError as e:
                print(f"  → Échec : {e}\n")

def traiterLitteraux(liste_litteraux):

    succes = 0
    echec = 0
    comparaisons = 0

    for i in range(len(liste_litteraux)):
        for j in range(i+1, len(liste_litteraux)):

            l1 = liste_litteraux[i]
            l2 = liste_litteraux[j]

            comparaisons += 1

            if l1.predicat == l2.predicat and l1.sign != l2.sign:
                if l1.arity != l2.arity:
                    #print(f"Échec : Arités différentes pour {l1} et {l2}")
                    echec += 1
                    continue

                system = TermSystem()

                for t1, t2 in zip(l1.enfants, l2.enfants):
                    system.add(t1, t2)

                mm = MartelliMontanari(system)

                try:
                    unificateur=mm.solve()
                    #print("Unification réussie")
                    succes += 1

                    if unificateur.is_empty():
                     #print("   (Système vide : les termes étaient identiques)")
                     pass
                    else:
                        for eq in unificateur.equations:
                            #print(f"   {eq.left} --> {eq.right}")
                            pass
                except UnificationError:
                    #print("Échec") 
                    echec += 1
    print("Fin du traitement.")
    return comparaisons, succes, echec


def lit_liste(l1: Litteral, list_litteraux: list[Litteral], touteUnif=True):
    resultat = {}
    for l2 in list_litteraux: # Etape 1 : On compare le littéral l1 avec tous les autres littéraux de la liste
        if l1.predicat == l2.predicat and l1.sign != l2.sign and l1.arity == l2.arity: #Etape 2 : On vérifie si les deux prédicats ont les mêmes symboles, les signes opposés et les arités égales
            system = TermSystem() 

            for t1, t2 in zip(l1.enfants, l2.enfants):
                system.add(t1, t2) # Etape 3 : Si les conditions sont remplies, on crée un système d'équations à partir des enfants des deux littéraux

            mm = MartelliMontanari(system) # Etape 4 : On utilise l'algorithme de Martelli-Montanari pour tenter de résoudre le système d'équations
            try:
                unificateur=mm.solve()                  
                resultat[l2] = unificateur
                if not touteUnif:
                    return resultat # Ici on retourne dès la première unification réussie
            except UnificationError:
                pass
    return resultat

def traiterLitterauxSet(liste_litteraux):

    ensemble = set(liste_litteraux)

    succes = 0
    echec = 0
    comparaisons = 0

    for l1 in ensemble:
        for l2 in ensemble:
            if l1.predicat == l2.predicat and l1.sign and not l2.sign:
                comparaisons += 1

                if l1.arity != l2.arity:
                    echec += 1
                    continue

                system = TermSystem()

                for t1, t2 in zip(l1.enfants, l2.enfants):
                    system.add(t1, t2)

                mm = MartelliMontanari(system)

                try:
                    unificateur=mm.solve()
                    #print("Unification réussie")
                    succes += 1

                    if unificateur.is_empty():
                     #print("   (Système vide : les termes étaient identiques)")
                     pass
                    else:
                        for eq in unificateur.equations:
                            pass
                except UnificationError:
                    echec += 1
    print("Fin du traitement.")
    return comparaisons, succes, echec


def lit_Set(l1,list_litteraux, touteUnif=True):
    resultat = {}
    ensemble = set(list_litteraux)
    for l2 in ensemble:
        if l1.predicat == l2.predicat and l1.sign != l2.sign and l1.arity == l2.arity:
            system = TermSystem()

            for t1, t2 in zip(l1.enfants, l2.enfants):
                system.add(t1, t2)

            mm = MartelliMontanari(system)
            try:
                unificateur=mm.solve()
                resultat[l2] = unificateur
                if not touteUnif:
                    return resultat # Ici on retourne dès la première unification réussie
            except UnificationError:
                pass
    return resultat

def indexer(liste_litteraux):

    index = {}

    for lit in liste_litteraux:
        if lit.predicat not in index:
            index[lit.predicat] = {"positif": [], "negatif": []}

        if lit.sign:
            index[lit.predicat]["positif"].append(lit)
        else:
            index[lit.predicat]["negatif"].append(lit)

    return index

def traiterLitterauxDict(liste_litteraux):

    succes = 0
    echec = 0
    comparaisons = 0

    index = indexer(liste_litteraux)

    for predicat, groupe in index.items():
        positifs = groupe["positif"]
        negatifs = groupe["negatif"]

        for i in range(len(positifs)):
            for j in range(len(negatifs)):

                l1 = positifs[i]
                l2 = negatifs[j]

                comparaisons += 1

                if l1.arity != l2.arity:
                    echec += 1
                    continue

                system = TermSystem()

                for t1, t2 in zip(l1.enfants, l2.enfants):
                    system.add(t1, t2)

                mm = MartelliMontanari(system)

                try:
                    unificateur = mm.solve()
                    succes += 1
                except UnificationError:
                        echec += 1

    print("Fin du traitement.")
    return comparaisons, succes, echec


def lit_dict(l1, index: dict, touteUnif: bool = True):

    resultat = {}
 
    if l1.predicat not in index:
        return resultat # Ici on retourne un ensmble vide
 
   
    if l1.sign:
        candidats = index[l1.predicat]["negatifs"]
    else:
        candidats = index[l1.predicat]["positifs"]
 
    for l2 in candidats:
        if l1.arity == l2.arity:
 
            system = TermSystem()
            for t1, t2 in zip(l1.enfants, l2.enfants):
                system.add(t1, t2)
    
            mm = MartelliMontanari(system)
            try:
                unificateur = mm.solve()
                resultat[l2] = unificateur
                if not touteUnif:
                    return resultat  # Ici on retourne dès la première unification réussie
            except UnificationError:
                pass
 
    return resultat