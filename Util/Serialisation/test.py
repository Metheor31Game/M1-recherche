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




if __name__ == "__main__":
    testSerialisation()
    testSerialisationAleatoire()
