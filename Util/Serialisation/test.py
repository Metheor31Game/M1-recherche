import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if path not in sys.path:
    sys.path.insert(0, path)

from Util.Litteral.Litteral import Litteral, GenerateurLitteralAleatoire
from Util.Serialisation.serialisation import serialiser, deserialiser


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
    pass