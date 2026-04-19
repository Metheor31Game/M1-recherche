import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Algos.ArbreDiscrimination.arbre_de_discrimination import benchmark_arbre_discrimination
from Algos.Robinson.benchmark import benchRobinson

from Util.Serialisation.serialisation import deserialiser
from Util.Litteral.Litteral import Litteral

def benchmark(candidat: str, filename: str, algo: str, structure: str):
    touteUnif = True
    pretraitement = True
    if algo == "arbre":
        print("Début déserialisation")
        predList = deserialiser(os.path.basename(filename), False)
        realCandidat = Litteral.from_string(candidat)
        print("Debut algo")
        tps_pretraitement, tps_unif = benchmark_arbre_discrimination(predList, realCandidat, touteUnif)
        print(tps_pretraitement, tps_unif)
    if algo == "robinson":
        print("Début déserialisation")
        predList = deserialiser(os.path.basename(filename), False)
        realCandidat = Litteral.from_string(candidat)
        print("Debut algo")
        tps_pretraitement, tps_unif = benchRobinson(realCandidat, predList, structure, pretraitement, touteUnif)
        print(tps_pretraitement, tps_unif)


if __name__ == "__main__":
    filename = "BD12"
    file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "Util",
        "Serialisation",
        "Output",
        filename,
    )
    benchmark("Q(X, f(Y), Z, g(X))", file, "robinson", "ensemble")