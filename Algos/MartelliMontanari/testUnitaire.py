from Util.TermStore.terme import FabriqueDeTermes
from Util.TermStore.TermList import TermSystem
from Algos.MartelliMontanari.MartelliMontanari import UnificationError, MartelliMontanari


def testDelete():
    """X = X, le résultat doit donner un système vide """
    X = FabriqueDeTermes.creer_var("X")
    system = TermSystem()
    system.add(X, X)

    mm = MartelliMontanari(system)
    result = mm.solve()

    assert result.is_empty(), f"On attend un système vide, obtenu : {result}"
    print("testDelete OK")

def testOrient():
    """a = X, X doit être à gauche et a à droite (X = a)"""
    X = FabriqueDeTermes.creer_var("X")
    a = FabriqueDeTermes.creer_cons("a")

    system = TermSystem()
    system.add(a, X)

    mm = MartelliMontanari(system)
    result = mm.solve()
    eq = result.equations[0]

    assert eq.left == X, f"On attend X à gauche, obtenu : {eq.left}"
    assert eq.right == a, f"On attend a à droite, obtenu : {eq.right}"
    print("testOrient OK")

def testSubstitution():
    """X = a, Y = X doit donner X = a, Y = a après substitution"""
    X = FabriqueDeTermes.creer_var("X")
    Y = FabriqueDeTermes.creer_var("Y")
    a = FabriqueDeTermes.creer_cons("a")

    system = TermSystem()
    system.add(X, a)
    system.add(Y, X)

    mm = MartelliMontanari(system)
    result = mm.solve()

    assert len(result.equations) == 2, f"On attend 2 équations, obtenu : {result}"
    
    # Ici on cherche les équations X = a et Y = a, peu importe l'ordre
    lefts = [eq.left for eq in result.equations]
    rights = [eq.right for eq in result.equations]

    assert X in lefts, f"On attend X dans les gauches, obtenu : {lefts}"
    assert Y in lefts, f"On attend Y dans les gauches, obtenu : {lefts}"
    assert rights[lefts.index(X)] == a, f"On attend X = a"
    assert rights[lefts.index(Y)] == a, f"On attend Y = a"
    print("testSubstitution OK")

def testDecomposition():
    """f(X, g(Y)) = f(a, g(b)) doit donner X = a et Y = b"""
    X = FabriqueDeTermes.creer_var("X")
    Y = FabriqueDeTermes.creer_var("Y")
    a = FabriqueDeTermes.creer_cons("a")
    b = FabriqueDeTermes.creer_cons("b")
    
    gY = FabriqueDeTermes.creer_fonc("g", 1, [Y])
    gb = FabriqueDeTermes.creer_fonc("g", 1, [b])
    
    fXgY = FabriqueDeTermes.creer_fonc("f", 2, [X, gY])
    fagb = FabriqueDeTermes.creer_fonc("f", 2, [a, gb])

    system = TermSystem()
    system.add(fXgY, fagb)

    mm = MartelliMontanari(system)
    result = mm.solve()

    lefts = [eq.left for eq in result.equations]
    rights = [eq.right for eq in result.equations]

    assert X in lefts, f"On attend X dans les gauches, obtenu : {lefts}"
    assert Y in lefts, f"On attend Y dans les gauches, obtenu : {lefts}"
    assert rights[lefts.index(X)] == a, f"On attend X = a"
    assert rights[lefts.index(Y)] == b, f"On attend Y = b"
    print("testDecomposition OK")

def testClashConstantes():
    """a = b doit lever une UnificationError"""
    a = FabriqueDeTermes.creer_cons("a")
    b = FabriqueDeTermes.creer_cons("b")

    system = TermSystem()
    system.add(a, b)

    mm = MartelliMontanari(system)
    
    try:
        mm.solve()
        assert False, "On attend une UnificationError, aucune exception levée"
    except UnificationError:
        print("testClashConstantes OK")


def testClashFonctions():
    """f(X) = g(X) doit lever une UnificationError"""
    X = FabriqueDeTermes.creer_var("X")
    
    fX = FabriqueDeTermes.creer_fonc("f", 1, [X])
    gX = FabriqueDeTermes.creer_fonc("g", 1, [X])

    system = TermSystem()
    system.add(fX, gX)

    mm = MartelliMontanari(system)
    
    try:
        mm.solve()
        assert False, "On attend une UnificationError, aucune exception levée"
    except UnificationError:
        print("testClashFonctions OK")


def testOccurCheck():
    """X = f(X) doit lever une UnificationError """
    X = FabriqueDeTermes.creer_var("X")
    fX = FabriqueDeTermes.creer_fonc("f", 1, [X])

    system = TermSystem()
    system.add(X, fX)

    mm = MartelliMontanari(system)

    try:
        mm.solve()
        assert False, "On attend une UnificationError, aucune exception levée"
    except UnificationError:
        print("testOccurCheck OK")
    
if __name__ == "__main__":
    testDelete()
    testOrient()
    testSubstitution()
    testDecomposition()
    testClashConstantes()
    testClashFonctions()
    testOccurCheck()