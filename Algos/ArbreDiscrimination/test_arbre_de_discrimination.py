import sys
import os

racine_projet = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(os.path.abspath(racine_projet))

from Util.Litteral.Litteral import GenerateurLitteralAleatoire
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

generateur = GenerateurLitteralAleatoire(['P', 'Q', 'R'], 3, 3)
predicats = generateur.generer_litteraux(1000)

for predicat in predicats:
    dt.inserer(predicat, str(predicat))

dt.affichage_arbre()

#==================================================================
#
# Recherche unification
#
#==================================================================

predicats_recherche = generateur.generer_litteraux(5)

for predicat in predicats_recherche:
    resultats = dt.rechercher(predicat)
    afficher_resultats(str(predicat), resultats)