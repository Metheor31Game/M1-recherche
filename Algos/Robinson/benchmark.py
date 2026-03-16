import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes, GenerateurDeTermesAleatoires
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from Algos.Predicat.unifPredicat import rechercherUnifiablesSimple
from Util.Litteral.Litteral import Litteral
from Util.Litteral.Litteral import GenerateurLitteralAleatoire

def benchmark(n, predList):
    #TODO : améliorer pour que je puisse directement commencer avec le store que je veux, pour optimiser

    # on veut essayer d'unifier un prédicat aléatoire avec n candidats
    t0gen = time.perf_counter()
    generateur = GenerateurLitteralAleatoire(predList, 1, 1)
    litteralList = generateur.generer_litteraux(n+1)
    litteral1 = litteralList.pop()
    t1gen = time.perf_counter()
    print("Temps de génération : ", t1gen - t0gen)

    # Créer un TermStore
    store = SetStore()
    for lit in litteralList:
        store.push(lit)

    # Répéter l'opération pour prendre la moyenne

    nb_repetitions = 100
    temps_exec = []
    result = None

    for _ in range(nb_repetitions):
        t0exec = time.perf_counter()
        result = rechercherUnifiablesSimple(litteral1, store, "Robinson")
        t1exec = time.perf_counter()
        temps_exec.append(t1exec - t0exec)

    temps_moyen = sum(temps_exec) / nb_repetitions
    print(f"Algo avec Set exécuté {nb_repetitions}x, temps moyen : {temps_moyen}")

    # Créer un ListStore
    store = ListStore()
    for lit in litteralList:
        store.push(lit)

    # Répéter l'opération pour prendre la moyenne

    nb_repetitions = 100
    temps_exec = []
    result = None

    for _ in range(nb_repetitions):
        t0exec = time.perf_counter()
        result = rechercherUnifiablesSimple(litteral1, store, "Robinson")
        t1exec = time.perf_counter()
        temps_exec.append(t1exec - t0exec)

    temps_moyen = sum(temps_exec) / nb_repetitions
    print(f"Algo avec List exécuté {nb_repetitions}x, temps moyen : {temps_moyen}")

    return result
    


if __name__ == "__main__":
    predList = ["P", "Q", "R"]
    benchmark(1000000, predList)