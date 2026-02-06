import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes
from Util.Litteral.Litteral import Litteral

# Création des termes
X = FabriqueDeTermes.creer_var("X")
a = FabriqueDeTermes.creer_cons("a")
f_X_a = FabriqueDeTermes.creer_fonc("f", 2, [X, a])
Y = FabriqueDeTermes.creer_var("Y")

# Création du littéral +P(f(X, a), Y)
lit = Litteral("P", [f_X_a, Y], True)

print("Représentation compacte :")
print(lit)
print()

print("Représentation en arbre :")
print(lit.afficher_arbre(indent= "│  "))


f_X_f_X_a = FabriqueDeTermes.creer_fonc("f", 2, [X, f_X_a])

print("")

lit2 = Litteral("P", [f_X_f_X_a], False)

print("")

print(lit2.afficher_arbre())

print("")

print(lit2)

