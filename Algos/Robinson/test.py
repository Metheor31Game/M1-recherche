import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from robinson import unify


def afficher(t1, t2, store):
    print(f"Terme 1 : {t1}")
    print(f"Terme 2 : {t2}")
    print()
    result = unify(t1, t2, SetStore())
    print(result)

    if result is None:
        print("Échec de l'unification")
    else:
        print("Unification réussie")
        print("Substitution susbt :")
        for var, terme in result.items():
            print(f"  {var} -> {terme}")

# Créer des termes simples
# t1 = f(X, a)
# t2 = f(b, Y)
X = FabriqueDeTermes.creer_var("X")
Y = FabriqueDeTermes.creer_var("Y")
a = FabriqueDeTermes.creer_cons("a")
b = FabriqueDeTermes.creer_cons("b")

t1 = FabriqueDeTermes.creer_fonc("f", 2, [X, a])
t2 = FabriqueDeTermes.creer_fonc("f", 2, [b, Y])

# Créer des termes un peu plus complexes
# t3 = f(g(X,b), Y)
# t4 = f(Z, a)
Z = FabriqueDeTermes.creer_var("Z")
g_X_b = FabriqueDeTermes.creer_fonc("g", 2, [X, b])
t3 = FabriqueDeTermes.creer_fonc("f", 2, [g_X_b, Y])
t4 = FabriqueDeTermes.creer_fonc("f", 2, [Z, a])

# Créer des termes plus grands (Généré par IA)
# t5 = f(g(h(X, a), Y), k(Z, b))
# t6 = f(g(h(c, W), d), k(V, U))
# Substitution attendue : {X → c, W → a, Y → d, Z → V, U → b}

W = FabriqueDeTermes.creer_var("W")
V = FabriqueDeTermes.creer_var("V")
U = FabriqueDeTermes.creer_var("U")
c = FabriqueDeTermes.creer_cons("c")
d = FabriqueDeTermes.creer_cons("d")

h_X_a = FabriqueDeTermes.creer_fonc("h", 2, [X, a])
g_h_Y = FabriqueDeTermes.creer_fonc("g", 2, [h_X_a, Y])
k_Z_b = FabriqueDeTermes.creer_fonc("k", 2, [Z, b])
t5 = FabriqueDeTermes.creer_fonc("f", 2, [g_h_Y, k_Z_b])

h_c_W = FabriqueDeTermes.creer_fonc("h", 2, [c, W])
g_h_d = FabriqueDeTermes.creer_fonc("g", 2, [h_c_W, d])
k_V_U = FabriqueDeTermes.creer_fonc("k", 2, [V, U])
t6 = FabriqueDeTermes.creer_fonc("f", 2, [g_h_d, k_V_U])

# t7 = f(g(X), g(Y))   - cas d'ÉCHEC
# t8 = f(g(a), h(b))  - g != h donc pas unifiable
t7 = FabriqueDeTermes.creer_fonc("f", 2, [
    FabriqueDeTermes.creer_fonc("g", 1, [X]),
    FabriqueDeTermes.creer_fonc("g", 1, [Y])
])
t8 = FabriqueDeTermes.creer_fonc("f", 2, [
    FabriqueDeTermes.creer_fonc("g", 1, [a]),
    FabriqueDeTermes.creer_fonc("h", 1, [b])
])

# t9 = f(X, X)        - cas d'ÉCHEC (occurs check)
# t10 = f(Y, g(Y))     - X devrait être Y ET g(Y) : cycle
t9 = FabriqueDeTermes.creer_fonc("f", 2, [X, X])
t10 = FabriqueDeTermes.creer_fonc("f", 2, [Y, FabriqueDeTermes.creer_fonc("g", 1, [Y])])


# Unifier avec un SetStore

#afficher(t1, t2, SetStore)
#afficher(t3, t4, SetStore)
afficher(t5, t6, SetStore)
#afficher(t7, t8, SetStore)
# afficher(t9, t10, SetStore)
