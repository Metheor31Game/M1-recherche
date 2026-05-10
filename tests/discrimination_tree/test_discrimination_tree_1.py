import time

from unification.utils.logique.litteral import GenerateurLitteralAleatoire
from unification import ArbreDeDiscrimination


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
N = 1000000
print(f"Génération de {N} prédicats . . .")
predicats = generateur.generer_litteraux(N)
print(f"Génération terminée.")

print(f"Insertion des prédicats dans l'arbre . . .")
debut_creation = time.time()
for predicat in predicats:
    dt.inserer(predicat, str(predicat))
fin_creation = time.time()

print(f"Création de l'arbre des {N} prédicats terminée en {(fin_creation - debut_creation):3f} secondes.")


#==================================================================
#
# Recherche unification
#
#==================================================================

n = 5
print(f"Génération des {n} prédicats à unifier . . .")
predicats_recherche = generateur.generer_litteraux(n)
print(f"Génération terminée.")

debut_total = time.time()
cpt = 0

for predicat in predicats_recherche:
    cpt += 1
    debut_pred = time.time()
    resultats = dt.rechercher(predicat)
    fin_pred = time.time()
    print(f"Unification de {predicat} :")
    print(f"\t* {len(resultats)} unifications trouvées en {(fin_pred - debut_pred):3f} secondes")
    print(f"\t* {(len(resultats) /  (fin_pred - debut_pred)):3f} unifications par seconde")

fin_total = time.time()
print(f"Résultats des {n} unifications trouvés en {(fin_total - debut_total):3f} secondes")