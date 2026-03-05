import sys
import os

racine_projet = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(os.path.abspath(racine_projet))

from Util.TermStore.terme import FabriqueDeTermes
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
        print("  → Aucun terme unifiable trouvé.")
        return
    for i, res in enumerate(resultats, 1):
        print(f"\n  Résultat {i} :")
        print(f"    Termes  : {res.pointeurs}")
        if res.substitution:
            print(f"    σ :")
            for var, seq in res.substitution.items():
                print(f"      {var}  →  {' '.join(seq)}")
        else:
            print(f"    σ : ∅  (termes identiques ou variables libres uniquement)")

#==================================================================
#
# Arbre de test (manuel)
#
#==================================================================

# ── Construction de l'arbre ──────────────────────────────────────────────────────

dt = ArbreDeDiscrimination()

# Abréviations :
var  = FabriqueDeTermes.creer_var
cons = FabriqueDeTermes.creer_cons
fonc = FabriqueDeTermes.creer_fonc

# Termes clos ==========================================================
# terme1 : f(a, b)
t01 = fonc("f", 2, [cons("a"), cons("b")])
dt.inserer(t01, "terme1 : f(a, b)")

# terme2 : f(a, a)
t02 = fonc("f", 2, [cons("a"), cons("a")])
dt.inserer(t02, "terme2 : f(a, a)")

# terme3 : f(g(a, b), c)
t03 = fonc("f", 2, [fonc("g", 2, [cons("a"), cons("b")]), cons("c")])
dt.inserer(t03, "terme3 : f(g(a, b), c)")

# terme4 : f(g(a, b), a)
t04 = fonc("f", 2, [fonc("g", 2, [cons("a"), cons("b")]), cons("a")])
dt.inserer(t04, "terme4 : f(g(a, b), a)")

# terme5 : h(a, g(b, c))
t05 = fonc("h", 2, [cons("a"), fonc("g", 2, [cons("b"), cons("c")])])
dt.inserer(t05, "terme5 : h(a, g(b, c))")


# Termes avec une seule variable ==========================================================
# terme6 : f(X, b) - variable en première position
t06 = fonc("f", 2, [var("X"), cons("b")])
dt.inserer(t06, "terme6 : f(X, b)")

# terme7 : f(a, X) - variable en deuxième position
t07 = fonc("f", 2, [cons("a"), var("X")])
dt.inserer(t07, "terme7 : f(a, X)")

# terme8 : f(g(X, b), c) — variable dans un sous-terme
t08 = fonc("f", 2, [fonc("g", 2, [var("X"), cons("b")]), cons("c")])
dt.inserer(t08, "terme8 : f(g(X, b), c)")

# terme9 : f(g(a, X), c) — symétrique de terme8
t09 = fonc("f", 2, [fonc("g", 2, [cons("a"), var("X")]), cons("c")])
dt.inserer(t09, "terme9 : f(g(a, X), c)")


# Termes avec plusieurs variables distinctes =====================================
# terme10 : f(X, Y) — deux variables libres (s'unifie avec tout f(_, _))
t10 = fonc("f", 2, [var("X"), var("Y")])
dt.inserer(t10, "terme10 : f(X, Y)")

# terme11 : f(g(X, Y), Z) — variable en tête d'argument et variable libre
t11 = fonc("f", 2, [fonc("g", 2, [var("X"), var("Y")]), var("Z")])
dt.inserer(t11, "terme11 : f(g(X, Y), Z)")

# terme12 : h(X, g(Y, Z)) — symétrique de terme11, tête h
t12 = fonc("h", 2, [var("X"), fonc("g", 2, [var("Y"), var("Z")])])
dt.inserer(t12, "terme12 : h(X, g(Y, Z))")


# Termes avec une variable répétée ===============================================
# Ces termes imposent une contrainte d'égalité : les deux occurrences de X
# doivent être liées au même terme lors de l'unification.
# terme13 : f(X, X) — les deux arguments doivent être identiques
t13 = fonc("f", 2, [var("X"), var("X")])
dt.inserer(t13, "terme13 : f(X, X)")

# terme14 : f(g(X, a), X) — X apparaît à deux niveaux différents
t14 = fonc("f", 2, [fonc("g", 2, [var("X"), cons("a")]), var("X")])
dt.inserer(t14, "terme14 : f(g(X, a), X)")

# terme15 : h(X, X) — même contrainte, tête h
t15 = fonc("h", 2, [var("X"), var("X")])
dt.inserer(t15, "terme15 : h(X, X)")


# ── Affichage de l'arbre ──────────────────────────────────────────────────────
print(f"\n{SEPARATEUR_EPAIS}")
print("  ARBRE CONSTRUIT (15 termes)")
print(SEPARATEUR_EPAIS)
dt.affichage_arbre()

# Création de l'arbre : validée


#==================================================================
#
# Requêtes de tests
#
#==================================================================

print(f"\n\n{SEPARATEUR_EPAIS}")
print("  REQUÊTES")
print(SEPARATEUR_EPAIS)

# ── Requête 1 : terme clos exact ──────────────────────────────────────────────
# f(a, b) est dans l'arbre.
# Résultats attendus (validé) :
#   terme1 f(a, b)      avec σ = ∅
#   terme6 f(X, b)      avec σ = {X → a}
#   terme7 f(a, X)      avec σ = {X → b}
#   terme10 f(X, Y)     avec σ = {X → a, Y → b}
q1 = fonc("f", 2, [cons("a"), cons("b")])
afficher_resultats("f(a, b)", dt.rechercher_terme(q1))

# ── Requête 2 : terme clos, arguments identiques ──────────────────────────────
# f(a, a)
# Résultats attendus (validé) :
#   terme2 f(a, a)      avec σ = ∅
#   terme7 f(a, X)      avec σ = {X → a}
#   terme10 f(X, Y)     avec σ = {X → a, Y → a}
#   terme13 f(X, X)     avec σ = {X → a}   
q2 = fonc("f", 2, [cons("a"), cons("a")])
afficher_resultats("f(a, a)", dt.rechercher_terme(q2))

# ── Requête 3 : terme clos imbriqué ───────────────────────────────────────────
# f(g(a, b), c)
# Résultats attendus (validé) :
#   terme3 f(g(a,b), c)     avec σ = ∅
#   terme8 f(g(X,b), c)     avec σ = {X → a}
#   terme9 f(g(a,X), c)     avec σ = {X → b}
#.  terme10 f(X, Y)         avec σ = {X → g a b, Y → c}
#   terme11 f(g(X,Y), Z)    avec σ = {X → a, Y → b, Z → c}
q3 = fonc("f", 2, [fonc("g", 2, [cons("a"), cons("b")]), cons("c")])
afficher_resultats("f(g(a, b), c)", dt.rechercher_terme(q3))

# ── Requête 4 : variable en première position ─────────────────────────────────
# f(X, c) : X peut matcher n'importe quel premier argument.
# Résultats attendus (validé) :
#   terme3 f(g(a,b), c)     avec σ = {X → g a b}
#   terme7 f(a, X)          avec σ = {X → a, *1 → c}
#   terme8 f(g(X,b), c)     avec σ = {X → g *1 b}  
#   terme9 f(g(a,X), c)     avec σ = {X → g a *1}
#   terme10 f(X, Y)         avec σ = {X → *1, *2 → c}
#   terme11 f(g(X,Y), Z)    avec σ = {X → g *1 *2, *3 → c}
#   terme13 f(X, X)         avec σ = {X → *1, *1 → c}
#   terme14 f(g(X,a), X)    avec σ = {X → g *1 a, *1 → c}
q4 = fonc("f", 2, [var("X"), cons("c")])
afficher_resultats("f(X, c)", dt.rechercher_terme(q4))

# ── Requête 5 : deux variables libres ─────────────────────────────────────────
# f(X, Y) : s'unifie avec tout terme de tête f/2.
# Résultats attendus : 
#   terme1 f(a, b)          avec σ = {X → a, Y → b}
#   terme2 f(a, a)          avec σ = {X → a, Y → a}
#   terme3 f(g(a,b), c)     avec σ = {X → g a b, Y → c}
#   terme4 f(g(a,b), a)     avec σ = {X → g a b, Y → a}
#   terme6 f(X,b)           avec σ = {X → *1, Y → b}
#   terme7 f(a,X)           avec σ = {X → a, Y → *1}
#   terme8 f(g(X,b), c)     avec σ = {X → g *1 b, Y → c}  
#   terme9 f(g(a,X), c)     avec σ = {X → g a *1, Y → c}
#   terme10 f(X, Y)         avec σ = {X → *1, Y → *2}
#   terme11 f(g(X,Y), Z)    avec σ = {X → g *1 *2, Y → *3}
#   terme13 f(X,X)          avec σ = {X → *1, Y → X}
#   terme14 f(g(X,a), X)    avec σ = {X → g *1 a, Y → X}
q5 = fonc("f", 2, [var("X"), var("Y")])
afficher_resultats("f(X, Y)", dt.rechercher_terme(q5))

# ── Requête 6 : variable répétée dans la requête ──────────────────────────────
# f(X, X) : les deux arguments doivent être liés au même terme.
# Résultats attendus (validé) :
#   terme2 f(a, a)          avec σ = {X → a}
#   terme13 f(X, X)         avec σ = {X → *1}
q6 = fonc("f", 2, [var("X"), var("X")])
afficher_resultats("f(X, X)", dt.rechercher_terme(q6))

# ── Requête 7 : tête inconnue de l'arbre ──────────────────────────────────────
# p(a, b)
# Résultat attendu (validé) : aucun résultat.
q7 = fonc("p", 2, [cons("a"), cons("b")])
afficher_resultats("p(a, b)  [tête absente de l'arbre]", dt.rechercher_terme(q7))

# ── Requête 8 : tête h, terme clos ────────────────────────────────────────────
# h(a, g(b, c))
# Résultats attendus (validé) :
#   terme5 h(a, g(b,c))     avec σ = ∅
#   terme12 h(X, g(Y,Z))    avec σ = {*1 → a, *2 → b, *3 → c}
q8 = fonc("h", 2, [cons("a"), fonc("g", 2, [cons("b"), cons("c")])])
afficher_resultats("h(a, g(b, c))", dt.rechercher_terme(q8))

# ── Requête 9 : terme imbriqué, contrainte de cohérence forte ─────────────────
# f(g(a, a), a)
# Résultats attendus (validé) :
#   terme10 f(X,Y)          avec σ = {*1 → g a a, *2 → a}
#   terme11 f(g(X,Y), Z)    avec σ = {*1 → a, *2 → a, *3 → a}
#   terme14 f(g(X,a), X)    avec σ = {*1 → a}
q9 = fonc("f", 2, [fonc("g", 2, [cons("a"), cons("a")]), cons("a")])
afficher_resultats("f(g(a, a), a)", dt.rechercher_terme(q9))

# ── Requête 10 : imbrication profonde, variable libre ─────────────────────────
# f(g(X, b), Y) : X libre sur le 1er arg de g, Y libre sur le 2e arg de f.
# Résultats attendus (validé) :
#   terme3 f(g(a,b), c)     avec σ = {X → a, Y → c}
#   terme4 f(g(a,b), a)     avec σ = {X → g a b, Y → a}
#   terme6 f(X,b)           avec σ = {*1 → g X b, Y → b}
#   terme8 f(g(X,b), c)     avec σ = {X → *1, Y → c}  
#   terme9 f(g(a,X), c)     avec σ = {X → a, *1 → b, Y → c}
#   terme10 f(X,Y)          avec σ = {*1 → g X b, Y → *2}
#   terme11 f(g(X,Y), Z)    avec σ = {X → *1, *2 → b, Y → *3}
#   terme13 f(X, X)         avec σ = {*1 → g X b, Y → *1}
q10 = fonc("f", 2, [fonc("g", 2, [var("X"), cons("b")]), var("Y")])
afficher_resultats("f(g(X, b), Y)", dt.rechercher_terme(q10))