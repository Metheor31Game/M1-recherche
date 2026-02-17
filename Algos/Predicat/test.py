import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes
from Util.Litteral.Litteral import Litteral
from Util.Litteral.Litteral import GenerateurLitteralAleatoire
from Algos.Predicat.unifPredicat import unifPredicat

# Création des termes
X = FabriqueDeTermes.creer_var("X")
Y = FabriqueDeTermes.creer_var("Y")
Z = FabriqueDeTermes.creer_var("Z")
a = FabriqueDeTermes.creer_cons("a")
b = FabriqueDeTermes.creer_cons("b")

# Création de 3 prédicats à 2 arguments
# P(X, a) avec signe positif
p1 = Litteral("P", [X, a], True)
print(f"Prédicat 1 : {p1}")

# P(b, Y) avec signe négatif (opposé à p1)
p2 = Litteral("P", [b, Y], False)
print(f"Prédicat 2 : {p2}")

# Q(X, Y) avec signe négatif (nom différent de p1)
p3 = Litteral("Q", [X, Y], False)
print(f"Prédicat 3 : {p3}")

print("\n" + "="*50)
print("TEST 1 : Unification qui DEVRAIT RÉUSSIR")
print("="*50)
print(f"Unification de {p1} et {p2}")
print("Attendu : X -> b, Y -> a")
result1 = unifPredicat(p1, p2, "Robinson")
if result1:
    print("✓ Unification réussie !")
    print("Substitution :")
    for var, terme in result1.items():
        print(f"  {var} -> {terme}")
else:
    print("✗ Échec de l'unification")

print("\n" + "="*50)
print("TEST 2 : Unification qui DEVRAIT ÉCHOUER")
print("="*50)
print(f"Unification de {p1} et {p3}")
print("(noms de prédicats différents : P vs Q)")
result2 = unifPredicat(p1, p3, "Robinson")
if result2:
    print("Unification réussie !")
    print("Substitution :")
    for var, terme in result2.items():
        print(f"  {var} -> {terme}")
else:
    print("Échec de l'unification")

# Test supplémentaire avec 3 arguments
print("\n" + "="*50)
print("TEST 3 : Prédicats à 3 arguments")
print("="*50)
p4 = Litteral("R", [X, Y, a], True)
p5 = Litteral("R", [b, Z, a], False)
print(f"Unification de {p4} et {p5}")
print("Attendu : X -> b, Y -> Z")
result3 = unifPredicat(p4, p5, "Robinson")
if result3:
    print("Unification réussie !")
    print("Substitution :")
    for var, terme in result3.items():
        print(f"  {var} -> {terme}")
else:
    print("Échec de l'unification")


############## Test generation aléatoire #######################

generateur = GenerateurLitteralAleatoire(["P", "Q", "R", "estEnfant"], 2, 1)

predicats = generateur.generer_litteraux(10)

print("- - - - - - - - - - - - ")

for p in predicats:
   print(p)





