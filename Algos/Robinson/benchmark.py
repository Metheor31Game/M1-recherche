import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from typing import List, Dict, Any, Optional, Tuple, NamedTuple
from Util.TermStore.TermStore import TermStore
from Util.TermStore.terme import FabriqueDeTermes, GenerateurDeTermesAleatoires
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from Algos.Predicat.unifPredicat import rechercherUnifiablesSimple
from Algos.Predicat.unifPredicat import afficherResultat
from Util.Litteral.Litteral import Litteral
from Util.Litteral.Litteral import GenerateurLitteralAleatoire
from Util.Serialisation.serialisation import serialiser, deserialiser
from Util.TermStore.DictStore import DictStore
from Algos.Predicat.unifPredicat import rechercherUnifiablesOptimise

def benchRobinson(candidats: List[Litteral], predList: list, structure: str,
                  pretraitement: bool, touteUnif: bool = True) -> Tuple[float, List[Tuple[float, int]]]:
    """
    Fonction utilitaire pour bench de l'algo de Robinson sur une LISTE de candidats.
    Calcule :
      - le temps de prétraitement (une seule fois, indépendant du candidat
        si `pretraitement` est True ; 0 sinon),
      - pour chaque candidat : le temps d'unification + le nombre d'unifications trouvées.

    L'unification est paramétrée par `touteUnif` qui recherche soit la première
    unification trouvée, soit toutes.

    Args:
        candidats (List[Litteral]): Liste des littéraux que l'on cherche à unifier.
        predList (list): Les littéraux du jeu de données (la "base").
        structure (str): Structure de données utilisée. ("liste", "ensemble", "dictionnaire")
        pretraitement (bool): Active ou non la phase de prétraitement.
        touteUnif (bool, optional): True = toutes les unifications, False = la première. Defaults to True.

    Returns:
        Tuple[float, List[Tuple[float, int]]]:
            (temps_pretraitement,
             [(tps_unif_candidat_0, nb_unif_candidat_0),
              (tps_unif_candidat_1, nb_unif_candidat_1),
              ...])
    """
    # --- Choix de la structure de données utilisée pour stocker les littéraux ---
    store = TermStore
    if structure == "liste":
        store = ListStore()
    elif structure == "ensemble":
        store = SetStore()
    elif structure == "dictionnaire":
        store = DictStore()
    else:
        raise ValueError(f"Structure non supportée : {structure}")

    # --- Remplissage initial de la structure ---
    # On ne mesure pas ce temps : ce n'est pas du prétraitement algorithmique,
    # juste du chargement de la structure.
    print("Creation de la structure")
    for e in predList:
        store.push(e)

    # --- Phase de prétraitement (Construction / Indexation) ---
    tps_pretraitement = 0.0
    
    if pretraitement:
        print(f"Debut pretraitement (Indexation dans {structure})")
        debut_pretraitement = time.perf_counter()
        
        # Le prétraitement EST l'insertion dans la structure intelligente
        for e in predList:
            store.push(e)
            
        # (Optionnel) Ici tu pourrais ajouter un store.optimiser_globalement() 
        # pour la ListStore si tu veux la trier une fois pour toutes.
            
        tps_pretraitement = time.perf_counter() - debut_pretraitement
    else:
        # Si on ne veut pas compter le prétraitement dans le bench, 
        # on fait le remplissage hors du chrono
        print(f"Creation de la structure sans chrono ({structure})")
        for e in predList:
            store.push(e)

    # --- Phase d'unification : on boucle sur tous les candidats ---
    resultats: List[Tuple[float, int]] = []
    print(f"Debut unification ({len(candidats)} candidats)")

    for i, candidat in enumerate(candidats):
        debut_unif = time.perf_counter()
        
        result = rechercherUnifiablesOptimise(candidat, store, "Robinson", touteUnif)
            
        tps_unif = time.perf_counter() - debut_unif

        nb_unif = len(result) if result is not None else 0
        resultats.append((tps_unif, nb_unif))

    return (tps_pretraitement, resultats)

    

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