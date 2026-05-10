from unification.utils.logique.litteral import Litteral, GenerateurLitteralAleatoire
from unification.utils.serialisation import serialiser, deserialiser

def testSerialisation():
    predicats_str = [
        "P(f(X,a),Y)",
        "Q(g(a))",
        "R(X,f(a),b)",
        "P(g(Y),h(a,b))",
        "Q(Z)",
        "R(f(X),g(Y),h(a))",
        "P(a,b)",
        "Q(f(g(a)))",
        "R(U,V,W)",
        "P(f(a,b),g(X))",
    ]
    predList = [Litteral.from_string(pred) for pred in predicats_str]
    serialiser(predList, "predicats_test.txt")
    predicasRelus = deserialiser("predicats_test.txt")

    assert len(predicasRelus) == len(predList)

    for i in range(len(predList)):
        assert predList[i] == predicasRelus[i]

    return

def testSerialisationAleatoire():
    generateur = GenerateurLitteralAleatoire(["P", "Q", "R"], 3, 3)
    predList = generateur.generer_litteraux(50)
    serialiser(predList, "TestAleatoire.txt")
    predicasRelus = deserialiser("TestAleatoire.txt")
    assert len(predicasRelus) == len(predList)

    for i in range(len(predList)):
        assert predList[i] == predicasRelus[i]

    return


def serialisation(predList, arite, profondeur, n, filename):
    """
    Génère un fichier de donnée aléatoire avec un certaine quantité et signature
    """
    generateur = GenerateurLitteralAleatoire(predList, arite, profondeur)
    preds = generateur.generer_litteraux(n)
    serialiser(preds, filename, False)




if __name__ == "__main__":
    # testSerialisation()
    # testSerialisationAleatoire()

    # Génération bd1
    # serialisation(["P", "Q", "R"], 3, 3, 10000, "BD1")
    # Génération bd2
    # serialisation(["P", "Q", "R"], 3, 3, 100000, "BD2")
    # Génération bd3
    # serialisation(["P", "Q", "R"], 3, 3, 1000000, "BD3")
    # Génération bd4
    # serialisation(["P", "Q", "R"], 6, 6, 10000, "BD4")
    # Génération bd5
    # serialisation(["P", "Q", "R"], 6, 6, 100000, "BD5")
    # Génération bd6
    # serialisation(["P", "Q", "R"], 6, 6, 1000000, "BD6")
    # Génération bd7
    # serialisation(["P", "Q", "R", "S", "T", "U"], 3, 3, 10000, "BD7")
    # Génération bd8
    # serialisation(["P", "Q", "R", "S", "T", "U"], 3, 3, 100000, "BD8")
    # Génération bd9
    # serialisation(["P", "Q", "R", "S", "T", "U"], 3, 3, 1000000, "BD9")
    # Génération bd10
    # serialisation(["P", "Q", "R", "S", "T", "U"], 6, 6, 10000, "BD10")
    # Génération bd11
    # serialisation(["P", "Q", "R", "S", "T", "U"], 6, 6, 100000, "BD11")
    # Génération bd12
    # serialisation(["P", "Q", "R", "S", "T", "U"], 6, 6, 1000000, "BD12zip")


    # Seconde génération

   # Signature : P, Q, R
    # Profondeur = 1
    serialisation(["P", "Q", "R"], 10, 1,    10_000, "jeu1")
    serialisation(["P", "Q", "R"], 10, 1,   100_000, "jeu2")
    serialisation(["P", "Q", "R"], 10, 1, 1_000_000, "jeu3")

    # Profondeur = 5
    serialisation(["P", "Q", "R"], 10, 5,    10_000, "jeu4")
    serialisation(["P", "Q", "R"], 10, 5,   100_000, "jeu5")
    serialisation(["P", "Q", "R"], 10, 5, 1_000_000, "jeu6")

    # Profondeur = 10
    serialisation(["P", "Q", "R"], 10, 10,    10_000, "jeu7")
    serialisation(["P", "Q", "R"], 10, 10,   100_000, "jeu8")
    serialisation(["P", "Q", "R"], 10, 10, 1_000_000, "jeu9")

    # Profondeur = 20
    serialisation(["P", "Q", "R"], 10, 20,    10_000, "jeu10")
    serialisation(["P", "Q", "R"], 10, 20,   100_000, "jeu11")
    serialisation(["P", "Q", "R"], 10, 20, 1_000_000, "jeu12")

    # Signature : P, Q, R, S, T, U
    # Profondeur = 1
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 1,    10_000, "jeu13")
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 1,   100_000, "jeu14")
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 1, 1_000_000, "jeu15")

    # Profondeur = 5
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 5,    10_000, "jeu16")
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 5,   100_000, "jeu17")
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 5, 1_000_000, "jeu18")

    # Profondeur = 10
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 10,    10_000, "jeu19")
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 10,   100_000, "jeu20")
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 10, 1_000_000, "jeu21")

    # Profondeur = 20
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 20,    10_000, "jeu22")
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 20,   100_000, "jeu23")
    serialisation(["P", "Q", "R", "S", "T", "U"], 10, 20, 1_000_000, "jeu24")


    pass