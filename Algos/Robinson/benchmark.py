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
from Util.Serialisation.serialisation import serialiser, deserialiser

def benchmark_with_output():
    """
    Charge output1, place les prédicats dans un Store.
    Unifie le premier prédicat avec tous les autres 10 fois.
    Calcule le temps pour chaque unification.
    Renvoie la moyenne des 8 temps restants (après avoir retiré le premier et le dernier).
    """
    try:
        # Charger output1 depuis la sérialisation
        litteralList = deserialiser("output1")
        print(f"Chargé {len(litteralList)} littéraux depuis output1")
    except FileNotFoundError:
        print("Fichier output1 introuvable. Il faut générer output1 avec test_Serialise.")
        return None
    
    if len(litteralList) < 2:
        print("output1 contient trop peu de littéraux.")
        return None
    
    # Séparer le premier littéral des autres
    litteral1 = litteralList[0]
    autres_litteraux = litteralList[1:]
    
    print(f"Premier littéral à unifier: {litteral1}")
    print(f"Nombre d'autres littéraux: {len(autres_litteraux)}")
    
    # Créer un Store avec tous les autres littéraux
    store = SetStore()
    for lit in autres_litteraux:
        store.push(lit)

    print(f"Nombre d'elements : {len(store)}")
    
    # Répéter 10 fois et mesurer le temps de chaque unification
    nb_repetitions = 10
    temps_exec = []
    result = None
    
    print(f"\nExécution de l'unification {nb_repetitions} fois")
    for i in range(nb_repetitions):
        t0exec = time.perf_counter()
        result = rechercherUnifiablesSimple(litteral1, store, "Robinson")
        t1exec = time.perf_counter()
        temps_unif = t1exec - t0exec
        temps_exec.append(temps_unif)
        print(f"  Unification {i+1}: {temps_unif:.6f}s")
    
    # Enlever le premier et le dernier temps, puis calculer la moyenne des 8 autres
    temps_filtres = temps_exec[1:-1]  # Exclut le 1er et le dernier
    temps_moyen = sum(temps_filtres) / len(temps_filtres) if temps_filtres else 0
    
    print(f"\nRésultats:")
    print(f"  Temps 1ère unification: {temps_exec[0]:.6f}s")
    print(f"  Temps 10ème unification: {temps_exec[-1]:.6f}s")
    print(f"  Moyenne des 8 autres: {temps_moyen:.6f}s")
    
    return temps_moyen

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
    store = ListStore()
    for lit in litteralList:
        store.push(lit)

    print(f"store utilisé : {store}")

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

def test_Serialise(n, predList):
    t0gen = time.perf_counter()
    generateur = GenerateurLitteralAleatoire(predList, 3, 3)
    litteralList = generateur.generer_litteraux(n+1)
    t1gen = time.perf_counter()
    print("Temps de génération : ", t1gen - t0gen)

    t0ser = time.perf_counter()
    serialiser(litteralList, "output2")
    t1ser = time.perf_counter()
    print("Temps de serialisation : ", t1ser - t0ser)

    


if __name__ == "__main__":
    predList = ["P", "Q", "R"]
    test_Serialise(10000000, predList)
    # Puis lancer le benchmark_with_output1
    # moyenne = benchmark_with_output()
    # print(f"\n==> Temps moyen final: {moyenne:.6f}s")