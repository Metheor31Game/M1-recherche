import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes
from Util.Litteral.Litteral import Litteral
from Util.Litteral.Litteral import GenerateurLitteralAleatoire
from Algos.Predicat.unifPredicat import unifPredicat


############## Test unifPredicat #######################

def testUnifPredicat():
    """
    Teste la fonction unifPredicat avec des cas précis et intéressants.
    Affichage créé par IA
    """
    print("="*60)
    print("TESTS DE LA FONCTION unifPredicat")
    print("="*60)
    
    # Création de termes réutilisables
    X = FabriqueDeTermes.creer_var("X")
    Y = FabriqueDeTermes.creer_var("Y")
    Z = FabriqueDeTermes.creer_var("Z")
    a = FabriqueDeTermes.creer_cons("a")
    b = FabriqueDeTermes.creer_cons("b")
    c = FabriqueDeTermes.creer_cons("c")
    f_a = FabriqueDeTermes.creer_fonc("f", 1, [a])
    f_X = FabriqueDeTermes.creer_fonc("f", 1, [X])
    g_a_b = FabriqueDeTermes.creer_fonc("g", 2, [a, b])
    
    # TEST 1: Unification réussie simple (variables et constantes)
    print("\n[TEST 1] Unification réussie : P(X, Y) avec ¬P(a, b)")
    p1 = Litteral("P", [X, Y], True)
    p2 = Litteral("P", [a, b], False)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : {{X/a, Y/b}}")
    
    # TEST 2: Échec - même signe (deux positifs)
    print("\n[TEST 2] Échec : même signe (les deux positifs)")
    p1 = Litteral("P", [X], True)
    p2 = Litteral("P", [a], True)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : None (signes identiques)")
    
    # TEST 3: Échec - noms de prédicats différents
    print("\n[TEST 3] Échec : noms de prédicats différents")
    p1 = Litteral("P", [X], True)
    p2 = Litteral("Q", [a], False)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : None (P ≠ Q)")
    
    # TEST 4: Échec - arités différentes
    print("\n[TEST 4] Échec : arités différentes")
    p1 = Litteral("P", [X, Y], True)
    p2 = Litteral("P", [a], False)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : None (arité 2 ≠ arité 1)")
    
    # TEST 5: Unification avec fonctions
    print("\n[TEST 5] Unification avec fonctions : P(f(X), Y) avec ¬P(f(a), b)")
    p1 = Litteral("P", [f_X, Y], True)
    p2 = Litteral("P", [f_a, b], False)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : {{X/a, Y/b}}")
    
    # TEST 6: Unification entre variables
    print("\n[TEST 6] Unification entre variables : P(X, Y) avec ¬P(Z, a)")
    p1 = Litteral("P", [X, Y], True)
    p2 = Litteral("P", [Z, a], False)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : {{X/Z, Y/a}} ou équivalent")
    
    # TEST 7: Échec - termes non unifiables (constantes différentes)
    print("\n[TEST 7] Échec : termes non unifiables (a ≠ b)")
    p1 = Litteral("P", [a, X], True)
    p2 = Litteral("P", [b, Y], False)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : None (a ne s'unifie pas avec b)")
    
    # TEST 8: Unification complexe avec plusieurs termes
    print("\n[TEST 8] Unification complexe : Q(X, g(a, b), Y) avec ¬Q(c, g(a, b), Z)")
    p1 = Litteral("Q", [X, g_a_b, Y], True)
    p2 = Litteral("Q", [c, g_a_b, Z], False)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : {{X/c, Y/Z}}")
    
    # TEST 9: Unification avec accumulation (X unifié deux fois)
    print("\n[TEST 9] Test cohérence : P(X, X) avec ¬P(a, a)")
    p1 = Litteral("P", [X, X], True)
    p2 = Litteral("P", [a, a], False)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : {{X/a}}")
    
    # TEST 10: Échec - incohérence (X ne peut pas être à la fois a et b)
    print("\n[TEST 10] Échec : incohérence (X = a et X = b simultanément)")
    p1 = Litteral("P", [X, X], True)
    p2 = Litteral("P", [a, b], False)
    result = unifPredicat(p1, p2, "Robinson")
    print(f"  {p1} ⊔ {p2}")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : None (X ne peut pas être a et b)")
    
    print("\n" + "="*60)
    print("FIN DES TESTS")
    print("="*60)


# testUnifPredicat()


############## Test generation aléatoire #######################

generateur = GenerateurLitteralAleatoire(["P", "Q", "R", "estEnfant"], 2, 1)

predicats = generateur.generer_litteraux(10)

print("- - - - - - - - - - - - ")

for p in predicats:
   print(p)

