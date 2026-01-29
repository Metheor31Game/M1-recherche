import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from robinson import unify

# Créer des termes simples
# t1 = f(X, a)
# t2 = f(b, Y)
X = FabriqueDeTermes.creer_var("X")
Y = FabriqueDeTermes.creer_var("Y")
a = FabriqueDeTermes.creer_cons("a")
b = FabriqueDeTermes.creer_cons("b")

t1 = FabriqueDeTermes.creer_fonc("f", 2, [X, a])
t2 = FabriqueDeTermes.creer_fonc("f", 2, [b, Y])

print(f"Terme 1 : {t1}")
print(f"Terme 2 : {t2}")
print()

# Unifier avec un ListStore
result = unify(t1, t2, SetStore())

if result is None:
    print("Échec de l'unification")
else:
    print("Unification réussie !")
    print("Substitution susbt :")
    for var, terme in result.items():
        print(f"  {var} -> {terme}")
