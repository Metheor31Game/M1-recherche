import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes
from Util.Litteral.Litteral import Litteral
from Util.Litteral.Litteral import GenerateurLitteralAleatoire
from Algos.Predicat.unifPredicat import unifPredicat, rechercherUnifiablesSimple, afficherResultat
from Util.TermStore.SetStore import SetStore


############## Test unifPredicat #######################

def testUnifPredicat():
    """
    Teste la fonction unifPredicat avec des cas précis et intéressants.
    Affichage créé par IA(les print etc), exemples et valeur des tests faits par moi
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

def testRechercherUnifiable():

    """
    Teste la fonction rechercherUnifiablesSimple.
    L'ia a fait l'affichage, les données sont les miennes
    """
    print("\n\n" + "="*60)
    print("TESTS DE LA FONCTION rechercherUnifiablesSimple")
    print("="*60)
    
    # Création de termes réutilisables
    X = FabriqueDeTermes.creer_var("X")
    Y = FabriqueDeTermes.creer_var("Y")
    Z = FabriqueDeTermes.creer_var("Z")
    a = FabriqueDeTermes.creer_cons("a")
    b = FabriqueDeTermes.creer_cons("b")
    c = FabriqueDeTermes.creer_cons("c")
    f_a = FabriqueDeTermes.creer_fonc("f", 1, [a])
    
    # TEST 1: Ensemble vide
    print("\n[TEST 1] Ensemble vide de candidats")
    p1 = Litteral("P", [X], True)
    preds = SetStore()
    result = rechercherUnifiablesSimple(p1, preds)
    print(f"  Référence : {p1}")
    print(f"  Candidats : (vide)")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : {{}} (dictionnaire vide)")
    
    # TEST 2: Aucun littéral ne s'unifie
    print("\n[TEST 2] Aucun littéral ne s'unifie")
    p1 = Litteral("P", [X], True)
    preds = SetStore()
    preds.push(Litteral("P", [a], True))      # Même signe
    preds.push(Litteral("Q", [a], False))     # Nom différent
    preds.push(Litteral("P", [a, b], False))  # Arité différente
    result = rechercherUnifiablesSimple(p1, preds)
    print(f"  Référence : {p1}")
    print(f"  Candidats : P(a), ¬Q(a), ¬P(a, b)")
    print(f"  → Résultat : {result}")
    print(f"  ✓ Attendu : {{}} (aucune unification possible)")
    
    # TEST 3: Un seul littéral s'unifie
    print("\n[TEST 3] Un seul littéral s'unifie")
    p1 = Litteral("P", [X], True)
    preds = SetStore()
    p_unifiable = Litteral("P", [a], False)
    preds.push(p_unifiable)
    preds.push(Litteral("Q", [a], False))     # Ne s'unifie pas
    preds.push(Litteral("P", [b], True))      # Même signe
    result = rechercherUnifiablesSimple(p1, preds)
    print(f"  Référence : {p1}")
    print(f"  Candidats : ¬P(a), ¬Q(a), P(b)")
    print(f"  → Résultat : {len(result)} unification(s)")
    print(f"     {result}")
    print(f"  ✓ Attendu : 1 unification avec ¬P(a) → {{X/a}}")
    
    # TEST 4: Plusieurs littéraux s'unifient (indépendance des substitutions)
    print("\n[TEST 4] Plusieurs littéraux s'unifient (indépendance)")
    p1 = Litteral("P", [X, Y], True)
    preds = SetStore()
    p_unifie1 = Litteral("P", [a, b], False)
    p_unifie2 = Litteral("P", [c, a], False)
    p_unifie3 = Litteral("P", [Z, Z], False)
    preds.push(p_unifie1)
    preds.push(p_unifie2)
    preds.push(p_unifie3)
    result = rechercherUnifiablesSimple(p1, preds)
    print(f"  Référence : {p1}")
    print(f"  Candidats : ¬P(a, b), ¬P(c, a), ¬P(Z, Z)")
    print(f"  → Résultat : {len(result)} unification(s)")
    for lit, subst in result.items():
        print(f"     {lit} → {subst}")
    print(f"  ✓ Attendu : 3 unifications avec substitutions indépendantes")
    print(f"     - X/a, Y/b")
    print(f"     - X/c, Y/a")
    print(f"     - X/Z, Y/Z")
    
    # TEST 5: Mélange avec différents prédicats
    print("\n[TEST 5] Mélange de prédicats différents")
    p1 = Litteral("P", [X], True)
    preds = SetStore()
    preds.push(Litteral("P", [a], False))     # S'unifie
    preds.push(Litteral("Q", [b], False))     # Non
    preds.push(Litteral("P", [b], False))     # S'unifie
    preds.push(Litteral("R", [c], False))     # Non
    preds.push(Litteral("P", [f_a], False))   # S'unifie
    result = rechercherUnifiablesSimple(p1, preds)
    print(f"  Référence : {p1}")
    print(f"  Candidats : ¬P(a), ¬Q(b), ¬P(b), ¬R(c), ¬P(f(a))")
    print(f"  → Résultat : {len(result)} unification(s)")
    for lit, subst in result.items():
        print(f"     {lit} → {subst}")
    print(f"  ✓ Attendu : 3 unifications (tous les P négatifs)")
    
    # TEST 6: Vérification que X peut prendre différentes valeurs
    print("\n[TEST 6] Vérification indépendance : X prend différentes valeurs")
    p1 = Litteral("Q", [X, X], True)
    preds = SetStore()
    preds.push(Litteral("Q", [a, a], False))  # X/a
    preds.push(Litteral("Q", [b, b], False))  # X/b
    preds.push(Litteral("Q", [a, b], False))  # Échec
    result = rechercherUnifiablesSimple(p1, preds)
    print(f"  Référence : {p1}")
    print(f"  Candidats : ¬Q(a, a), ¬Q(b, b), ¬Q(a, b)")
    print(f"  → Résultat : {len(result)} unification(s)")
    for lit, subst in result.items():
        print(f"     {lit} → {subst}")
    print(f"  ✓ Attendu : 2 unifications (X=a puis X=b séparément)")
    print(f"     - ¬Q(a, a) car X peut être a")
    print(f"     - ¬Q(b, b) car X peut être b")
    print(f"     - Pas ¬Q(a, b) car X ne peut pas être à la fois a et b")
    
    # TEST 7: Tous les candidats s'unifient
    print("\n[TEST 7] Tous les candidats s'unifient")
    p1 = Litteral("P", [X], True)
    preds = SetStore()
    preds.push(Litteral("P", [a], False))
    preds.push(Litteral("P", [b], False))
    preds.push(Litteral("P", [c], False))
    result = rechercherUnifiablesSimple(p1, preds)
    print(f"  Référence : {p1}")
    print(f"  Candidats : ¬P(a), ¬P(b), ¬P(c)")
    print(f"  → Résultat : ", result)
    print(f"  ✓ Attendu : 3 unifications (tous les candidats)")
    
    print("\n" + "="*60)
    print("FIN DES TESTS rechercherUnifiablesSimple")
    print("="*60)

# testUnifPredicat()

#testRechercherUnifiable()


############## Test generation aléatoire #######################

# generateur = GenerateurLitteralAleatoire(["P", "Q", "R", "estEnfant"], 2, 1)

# predicats = generateur.generer_litteraux(10)

# print("- - - - - - - - - - - - ")

# for p in predicats:
#    print(p)



################ Test pour vérifier que tout les algos ont les mêmes résultats ############

l1 = Litteral.from_string("¬P(f(Y), g(Z), X)")

set = SetStore()
set.push(Litteral.from_string("P(Y, g(X), X)"))
set.push(Litteral.from_string("P(X, a, Z)"))
set.push(Litteral.from_string("P(f(a), X, X)"))
set.push(Litteral.from_string("P(X, g(a), X)"))
set.push(Litteral.from_string("P(X, g(f(Y), X), X)"))
set.push(Litteral.from_string("P(f(Y), g(a), X)"))
set.push(Litteral.from_string("P(f(Z), g(Z), Z)"))
set.push(Litteral.from_string("P(f(a), g(Z), a)"))
set.push(Litteral.from_string("P(f(g(a)), g(Z), X)"))

res = rechercherUnifiablesSimple(l1, set, "Robinson")

afficherResultat(l1, res)

