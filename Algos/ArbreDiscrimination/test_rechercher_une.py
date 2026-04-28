import sys
import os

racine_projet = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(os.path.abspath(racine_projet))

from Util.Litteral.Litteral import Litteral
from Algos.ArbreDiscrimination.arbre_de_discrimination import SYMBOLE_PREDICAT_POSITIF, SYMBOLE_PREDICAT_NEGATIF
from Algos.ArbreDiscrimination.arbre_de_discrimination import ArbreDeDiscrimination

dt = ArbreDeDiscrimination()
 
predicat1 = Litteral.from_string("P(X,X)")
predicat2 = Litteral.from_string("P(X,Y)")
predicat3 = Litteral.from_string("P(g(a,X),Y)")
predicat4 = Litteral.from_string("P(g(X,b),X)")
predicat5 = Litteral.from_string("P(f(a),Z)")
predicat6 = Litteral.from_string("P(a,b)")
predicat7 = Litteral.from_string("P(b,b)")
predicat8 = Litteral.from_string("P(X,f(b))")
predicat9 = Litteral.from_string("P(Y,b)")
 
dt.inserer(predicat1, f"predicat1 : {SYMBOLE_PREDICAT_POSITIF}P(X, X)")
dt.inserer(predicat2, f"predicat2 : {SYMBOLE_PREDICAT_POSITIF}P(X, Y)")
dt.inserer(predicat3, f"predicat3 : {SYMBOLE_PREDICAT_POSITIF}P(g(a, X), Y)")
dt.inserer(predicat4, f"predicat4 : {SYMBOLE_PREDICAT_POSITIF}P(g(X, b), X)")
dt.inserer(predicat5, f"predicat5 : {SYMBOLE_PREDICAT_POSITIF}P(f(a), Z)")
dt.inserer(predicat6, f"predicat6 : {SYMBOLE_PREDICAT_POSITIF}P(a, b)")
dt.inserer(predicat7, f"predicat7 : {SYMBOLE_PREDICAT_POSITIF}P(b, b)")
dt.inserer(predicat8, f"predicat8 : {SYMBOLE_PREDICAT_POSITIF}P(X, f(b))")
dt.inserer(predicat9, f"predicat9 : {SYMBOLE_PREDICAT_POSITIF}P(Y, b)")

predicat_recherche = Litteral.from_string(f"{SYMBOLE_PREDICAT_NEGATIF}P(f(Y),Z)")
 
print(f"\nRecherche de termes unifiables avec : {SYMBOLE_PREDICAT_NEGATIF}P(f(Y), Z)")
resultat = dt.rechercher_une(predicat_recherche)
 
if not resultat:
    print("  Aucun prédicat unifiable trouvé.")
else:
    print(f"\n  Résultat :")
    print(f"    Pointeurs    : {resultat.pointeurs}")
    if resultat.substitution:
        print(f"    Substitution :")
        for var, terme_subst in resultat.substitution.items():
            print(f"      {var}  →  {terme_subst}")
    else:
        print(f"    Substitution : ∅  (termes identiques)")
    