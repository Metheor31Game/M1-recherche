import os
import sys
import time
import tracemalloc  # mesure fine de l'allocation mémoire côté Python
import psutil       # mesure système (RAM résidente, CPU du processus)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Algos.ArbreDiscrimination.arbre_de_discrimination import benchmark_arbre_discrimination
from Algos.Robinson.benchmark import benchRobinson
from Algos.MartelliMontanari.bench import bench

from Util.Serialisation.serialisation import deserialiser
from Util.Litteral.Litteral import Litteral

# ATTENTION : Aide de l'IA pour connaitre psutil et tracemalloc, et pour faire un affichage correct


def _mesurer_ressources(fonction_algo, *args, **kwargs):
    """
    Exécute `fonction_algo(*args, **kwargs)` en mesurant :
      - le temps renvoyé par la fonction elle-même (prétraitement, unification)
      - la RAM consommée (delta RSS + pic tracemalloc)
      - le % CPU moyen utilisé par le processus pendant l'exécution

    Retourne un dict avec toutes les mesures + le résultat brut de l'algo.

    """
    # Handle vers le processus courant pour interroger l'OS
    process = psutil.Process(os.getpid())

    # --- Initialisation du compteur CPU ---
    # Le premier appel à cpu_percent() renvoie 0.0
    # Les appels suivants renverront le % moyen depuis
    # ce point. C'est le fonctionnement documenté de psutil.
    process.cpu_percent(interval=None)

    # --- Mesure RAM : point de départ ---
    ram_avant = process.memory_info().rss  # en octets
    tracemalloc.start()                    # démarre le suivi des allocations Python

    # --- Exécution de l'algo ---
    t_debut = time.perf_counter()
    resultat = fonction_algo(*args, **kwargs)
    t_fin = time.perf_counter()

    # --- Mesure RAM : point d'arrivée ---
    # tracemalloc nous donne la mémoire courante ET le pic atteint
    # depuis le tracemalloc.start(). Le pic est plus intéressant car il
    # capture les allocations temporaires qui ont pu être libérées avant la fin.
    mem_courante, mem_pic = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ram_apres = process.memory_info().rss

    # --- Mesure CPU : lecture finale ---
    # % CPU moyen depuis l'appel d'init. Peut dépasser 100% sur une machine
    # multi-cœurs si l'algo est parallèle (ce n'est pas notre cas, mais bon).
    cpu_percent = process.cpu_percent(interval=None)

    # Construction du dictionnaire de résultats
    return {
        "resultat_algo": resultat,           # ce que l'algo a renvoyé (ex: (tps_pre, tps_unif))
        "temps_total_s": t_fin - t_debut,    # temps wall-clock global (sanity check)
        "ram_delta_rss_Mo": (ram_apres - ram_avant) / (1024 * 1024),
        "ram_pic_tracemalloc_Mo": mem_pic / (1024 * 1024),
        "ram_courante_tracemalloc_Mo": mem_courante / (1024 * 1024),
        "cpu_percent": cpu_percent,
    }


def _afficher_mesures(algo: str, structure: str, mesures: dict):
    """Joli affichage uniforme pour comparer les algos."""
    tps_pre, tps_unif = mesures["resultat_algo"]
    print("\n" + "=" * 60)
    print(f" Résultats  —  algo: {algo}   structure: {structure}")
    print("=" * 60)
    print(f"  Temps prétraitement   : {tps_pre} s")
    print(f"  Temps unification     : {tps_unif} s")
    print(f"  Temps total (wall)    : {mesures['temps_total_s']:.6f} s")
    print(f"  RAM delta (RSS)       : {mesures['ram_delta_rss_Mo']:.3f} Mo")
    print(f"  RAM pic (tracemalloc) : {mesures['ram_pic_tracemalloc_Mo']:.3f} Mo")
    print(f"  CPU moyen             : {mesures['cpu_percent']:.1f} %")
    print("=" * 60)


def benchmark(candidat: str, filename: str, algo: str, structure: str):
    """
    Mesure temps, RAM et CPU de manière uniforme pour permettre la comparaison.
    """
    touteUnif = True
    pretraitement = False

    # --- chargement des données ---
    print("Début déserialisation")
    predList = deserialiser(os.path.basename(filename), False)
    realCandidat = Litteral.from_string(candidat)
    print(f"Chargé {len(predList)} littéraux")

    # --- Phase algo : on dispatche vers la bonne fonction de bench ---
    print("Debut algo")
    if algo == "arbre":
        # L'arbre de discrimination n'a pas de paramètre "structure"
        mesures = _mesurer_ressources(
            benchmark_arbre_discrimination,
            predList, realCandidat, touteUnif
        )
    elif algo == "robinson":
        mesures = _mesurer_ressources(
            benchRobinson,
            realCandidat, predList, structure, pretraitement, touteUnif
        )
    elif algo == "mm":
        mesures = _mesurer_ressources(
            bench,
            realCandidat, predList, structure, pretraitement, touteUnif
        )
    else:
        raise ValueError(f"Algo inconnu : {algo}")

    _afficher_mesures(algo, structure, mesures)
    return mesures


if __name__ == "__main__":
    filename = "jeu23"
    file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "Util",
        "Serialisation",
        "Output",
        filename,
    )
    benchmark("S(X, b, V, a, Y, j(a), V, Z, b, W, c, d, i(b, X), U, X)", file, "arbre", "arbre")
