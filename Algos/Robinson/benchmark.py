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

def benchmark_with_output(fileName):
    """
    Charge output, place les prédicats dans un Store.
    Unifie le premier prédicat avec tous les autres 10 fois.
    Calcule le temps pour chaque unification.
    Renvoie la moyenne des 8 temps restants (après avoir retiré le premier et le dernier).
    """
    try:
        # Charger output1 depuis la sérialisation
        litteralList = deserialiser(fileName, False)
        print(f"Chargé {len(litteralList)} littéraux depuis output1")
    except FileNotFoundError:
        print("Fichier output introuvable. Il faut générer output1 avec test_Serialise.")
        return None
    
    if len(litteralList) < 2:
        print("output contient trop peu de littéraux.")
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

def test_Serialise(n, predList, fileName):
    t0gen = time.perf_counter()
    generateur = GenerateurLitteralAleatoire(predList, 8, 8)
    litteralList = generateur.generer_litteraux(n+1)
    t1gen = time.perf_counter()
    print("Temps de génération : ", t1gen - t0gen)

    t0ser = time.perf_counter()
    serialiser(litteralList, fileName)
    t1ser = time.perf_counter()
    print("Temps de serialisation : ", t1ser - t0ser)

    


if __name__ == "__main__":
    moyenne = benchmark_with_output("BD12")