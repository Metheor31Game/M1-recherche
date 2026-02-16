import time  
from Util.TermStore.terme import FabriqueDeTermes
from Util.Litteral.Litteral import Litteral
from Util.Litteral.traiterLitteraux import traiter_litteraux

def var(name):
    return FabriqueDeTermes.creer_var(name)

def cons(name):
    return FabriqueDeTermes.creer_cons(name)

def func(name, arity, enfants):
    return FabriqueDeTermes.creer_fonc(name, arity, enfants)

def executer_test(nom, liste_litteraux):
    print(f"\n==============================")
    print(f"{nom}")
    print("==============================")
    
    start_time = time.perf_counter() 
    traiter_litteraux(liste_litteraux)
    end_time = time.perf_counter()  
    
    duree = (end_time - start_time) * 1000
    print(f"\n Temps d'exécution : {duree:.4f} ms")

# Initialisation des variables et constantes
X = var("X")
Y = var("Y")
Z = var("Z")
a = cons("a")
b = cons("b")

# ======================================================
# CAS 1 : Unification réussie
# ======================================================
fX = func("f", 1, [X])
fa = func("f", 1, [a])
g_b = func("g", 1, [b])
fY = func("f", 1, [Y])
gX = func("g", 1, [X])

L1 = [
    Litteral("P", [fX, b], True),
    Litteral("Q", [g_b], False),
    Litteral("P", [fa, b], False),
    Litteral("Q", [gX], True),
    Litteral("P", [fY, b], False)
]
executer_test("TEST 1 : Unification réussie", L1)

# ======================================================
# CAS 2: Clash (fonctions différentes)
# ======================================================
L2 = [
    Litteral("P", [fa], True),
    Litteral("P", [g_b], False)
]
executer_test("TEST 2 : Clash", L2)

# ======================================================
# CAS 3 : Occur Check
# ======================================================
L3 = [
    Litteral("P", [X], True),
    Litteral("P", [fX], False)
]
executer_test("TEST 3 : Occur Check", L3)

# ======================================================
# CAS 4 : Aucun complémentaire
# ======================================================
L4 = [
    Litteral("P", [a], True),
    Litteral("Q", [b], True)
]
executer_test("TEST 4 : Aucun complémentaire", L4)

# ======================================================
# CAS 5 : Même signe
# ======================================================
L5 = [
    Litteral("P", [a], True),
    Litteral("P", [a], True)
]
executer_test("TEST 5 : Même signe", L5)

# ======================================================
# CAS 6 : Variables identiques contradictoires
# ======================================================
executer_test("TEST 6 : Variables identiques", [
    Litteral("P", [X, X], True),
    Litteral("P", [a, b], False)
])

# ======================================================
# CAS 7 : Arité différente
# ======================================================
L7 = [
    Litteral("P", [a, b], True),
    Litteral("Q", [a, b], False),
    Litteral("P", [a], False)
]
executer_test("TEST 7 : Arité différente", L7)

# ======================================================
# CAS 8 : Clash 
# ======================================================
g_a = func("g", 1, [a])
gZ = func("g", 1, [Z])
fgZ = func("f", 1, [gZ])

L8 = [
    Litteral("P", [X, fY, g_a], True), 
    Litteral("P", [fY, fgZ, gX], False)
]
executer_test("TEST 8 : Clash", L8)

# ======================================================
#  CAS 9 : Chaîne profonde
# ======================================================
X1, X2, X3, X4 = var("X1"), var("X2"), var("X3"), var("X4")

L9 = [
    Litteral("P", [X1, X2, X3, X4], True),
    Litteral("P", [func("f", 1, [X2]), func("f", 1, [X3]), func("f", 1, [X4]), a], False)
]

executer_test("TEST 9 :Chaîne profonde", L9)