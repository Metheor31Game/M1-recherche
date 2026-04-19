import sys
import os
import time

racine_projet = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(os.path.abspath(racine_projet))

from Util.Litteral.Litteral import Litteral
from Algos.ArbreDiscrimination.arbre_de_discrimination import ArbreDeDiscrimination


#==================================================================
#
# Utilitaire d'affichage généré par IA (ClaudeCode)
#
#==================================================================
SEPARATEUR       = "─" * 68
SEPARATEUR_EPAIS = "═" * 68

def afficher_resultats(label: str, resultats) -> None:
    """Affiche les résultats d'une recherche de façon lisible."""
    print(f"\n{SEPARATEUR}")
    print(f"  Requête : {label}")
    print(SEPARATEUR)
    if not resultats:
        print("  Aucun terme unifiable trouvé.")
    else:
        for i, res in enumerate(resultats, 1):
            print(f"\n  Résultat {i} :")
            print(f"    Pointeurs    : {res.pointeurs}")
            if res.substitution:
                print(f"    Substitution :")
                for var, terme_subst in res.substitution.items():
                    print(f"      {var}  →  {terme_subst}")
            else:
                print(f"    Substitution : ∅  (termes identiques)")

#==================================================================
#
# Arbre de test 
#
#==================================================================

# ── Construction de l'arbre ──────────────────────────────────────────────────────

dt = ArbreDeDiscrimination()

predicat1 = Litteral.from_string("P(Y, g(X), X)")
predicat2 = Litteral.from_string("P(X, a, Z)")
predicat3 = Litteral.from_string("P(f(a), X, X)")
predicat4 = Litteral.from_string("P(X, g(a), X)")
predicat5 = Litteral.from_string("P(X, g(f(Y), X), X)")
predicat6 = Litteral.from_string("P(f(Y), g(a), X)")
predicat7 = Litteral.from_string("P(f(Z), g(Z), Z)")
predicat8 = Litteral.from_string("P(f(a), g(Z), a)")
predicat9 = Litteral.from_string("P(f(g(a)), g(Z), X)")

dt.inserer(predicat1, "predicat1: P(Y, g(X), X)")
dt.inserer(predicat2, "predicat2: P(X, a, Z)")
dt.inserer(predicat3, "predicat3: P(f(a), X, X)")
dt.inserer(predicat4, "predicat4: P(X, g(a), X)")
dt.inserer(predicat5, "predicat5: P(X, g(f(Y), X), X)")
dt.inserer(predicat6, "predicat6: P(f(Y), g(a), X)")
dt.inserer(predicat7, "predicat7: P(f(Z), g(Z), Z)")
dt.inserer(predicat8, "predicat8: P(f(a), g(Z), a)")
dt.inserer(predicat9, "predicat9: P(f(g(a)), g(Z), X)")



#==================================================================
#
# Recherche unification
#
#==================================================================

predicat_recherche = Litteral.from_string("¬P(f(Y), g(Z), X)")
resultats = dt.rechercher(predicat_recherche)
print(f"Unification de {predicat_recherche} :")
afficher_resultats("¬P(f(Y), g(Z), X)", resultats=resultats)
