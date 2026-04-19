import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.TermStore import TermStore
from Util.TermStore.terme import FabriqueDeTermes, GenerateurDeTermesAleatoires
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from Algos.Predicat.unifPredicat import rechercherUnifiablesSimple
from Algos.Predicat.unifPredicat import afficherResultat
from Util.Litteral.Litteral import Litteral
from Util.Litteral.Litteral import GenerateurLitteralAleatoire
from Util.Serialisation.serialisation import serialiser, deserialiser

def benchRobinson(candidat: Litteral, predList: list, structure: str, pretraitement: bool, touteUnif = True):
    """
    Fonction utilitaire pour bench des algos.
    Calcul le temps de pré-traitement et le temps d'unification.
    L'unification est paramétrée par `toutes_unifs` qui recherche soit la première unification trouvée, soit toutes.

    Args:
        litteraux (List[Litteral]): Les littéraux.
        query_litteral (Litteral): Le littéral que l'on cherche à unifier.
        structure (str): Permet de dire quelle structure on veut bench. (liste, ensemble, dictionnaire)
        pretraitement (bool): dit si oui ou non on veut prétraiter.
        toutes_unifs (bool, optional): Choix de trouver toutes les unifications ou seulement la première. Defaults to True.
    Returns:
        Tuple[float, float]: (temps_pretraitement, temps_unification) en secondes.
    """
    # Choix de la structure de données utilisée pour stocker les littéraux
    store = TermStore
    if structure == "liste":
        store = ListStore()
    elif structure == "ensemble":
        store = SetStore()
    elif structure == "dictionnaire":
        # a faire plus tard
        pass

    # Remplir le store avec la predList
    # Remarque : on ne mesure pas ce temps car ce n'est pas du prétraitement
    # au sens algorithmique (c'est juste du remplissage initial de la structure).
    print("Creation de la structure")
    for e in predList:
        store.push(e)

    # --- Calcul du temps de prétraitement ---
    # 0 par défaut si on ne prétraite pas
    tps_pretraitement = 0.0
    if pretraitement:
        print("debut pretraitement")
        # On mémorise l'instant avant le prétraitement
        debut_pretraitement = time.perf_counter()
        store.pretraitement(candidat)
        # Différence entre maintenant et le début = durée du prétraitement
        tps_pretraitement = time.perf_counter() - debut_pretraitement

    # --- Calcul du temps d'unification ---
    # On mémorise l'instant avant de lancer la recherche d'unifications
    debut_unif = time.perf_counter()
    if touteUnif:
        print("Debut unification")
        # Cas où on cherche toutes les unifications possibles
        result = rechercherUnifiablesSimple(candidat, store)
    else:
        # A faire plus tard : recherche de la première unification seulement
        result = None
    # Différence = durée réelle de l'unification
    tps_unif = time.perf_counter() - debut_unif

    # Affichage pour debug (attention : ça peut fausser le temps du bench
    #afficherResultat(candidat, result)

    return (tps_pretraitement, tps_unif)

    

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