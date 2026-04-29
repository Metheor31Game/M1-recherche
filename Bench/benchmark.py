import os
import sys
import time
import tracemalloc  # mesure fine de l'allocation mémoire côté Python
import psutil       # mesure système (RAM résidente, CPU du processus)
from typing import List, Tuple

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
      - le temps renvoyé par la fonction elle-même (prétraitement, unification par candidat)
      - la RAM consommée (delta RSS + pic tracemalloc)
      - le % CPU moyen utilisé par le processus pendant l'exécution

    Retourne un dict avec toutes les mesures + le résultat brut de l'algo.

    Le résultat brut a maintenant la forme :
        Tuple[float, List[Tuple[float, int]]]
        = (temps_prétraitement, [(tps_unif_candidat_i, nb_unif_candidat_i), ...])
    """
    # Handle vers le processus courant pour interroger l'OS
    process = psutil.Process(os.getpid())

    # --- Initialisation du compteur CPU ---
    # Le premier appel à cpu_percent() renvoie 0.0 et arme la mesure ;
    # les appels suivants renverront le % moyen depuis ce point.
    process.cpu_percent(interval=None)

    # --- Mesure RAM : point de départ ---
    ram_avant = process.memory_info().rss  # en octets
    tracemalloc.start()                    # démarre le suivi des allocations Python

    # --- Exécution de l'algo ---
    t_debut = time.perf_counter()
    resultat = fonction_algo(*args, **kwargs)
    t_fin = time.perf_counter()

    # --- Mesure RAM : point d'arrivée ---
    # On récupère la mémoire courante ET le pic atteint depuis tracemalloc.start().
    # Le pic capture aussi les allocations temporaires libérées avant la fin.
    mem_courante, mem_pic = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    ram_apres = process.memory_info().rss

    # --- Mesure CPU : lecture finale ---
    # % CPU moyen depuis l'init. Peut dépasser 100% sur une machine multi-cœurs.
    cpu_percent = process.cpu_percent(interval=None)

    # Construction du dictionnaire de résultats
    return {
        "resultat_algo": resultat,           # (tps_pre, [(tps_unif, nb_unif), ...])
        "temps_total_s": t_fin - t_debut,    # temps wall-clock global (sanity check)
        "ram_delta_rss_Mo": (ram_apres - ram_avant) / (1024 * 1024),
        "ram_pic_tracemalloc_Mo": mem_pic / (1024 * 1024),
        "ram_courante_tracemalloc_Mo": mem_courante / (1024 * 1024),
        "cpu_percent": cpu_percent,
    }


def _afficher_mesures(algo: str, structure: str, candidats: List[str], mesures: dict):
    """
    Joli affichage uniforme pour comparer les algos.
    Affiche :
      - le détail par candidat (temps unif + nb d'unifs trouvées)
      - les agrégats (somme et moyenne) sur l'ensemble des candidats
      - les ressources globales (RAM, CPU, temps wall total)
    """
    tps_pre, liste_resultats = mesures["resultat_algo"]
    nb_candidats = len(liste_resultats)

    # Agrégats : somme des temps d'unification + somme des nb d'unifs
    total_tps_unif = sum(t for t, _ in liste_resultats)
    total_nb_unif = sum(n for _, n in liste_resultats)
    moy_tps_unif = total_tps_unif / nb_candidats if nb_candidats else 0.0

    print("\n" + "=" * 70)
    print(f" Résultats  —  algo: {algo}   structure: {structure}")
    print(f" Nombre de candidats   : {nb_candidats}")
    print("=" * 70)
    print(f"  Temps prétraitement       : {tps_pre} s")
    print(f"  Temps unif. (somme)       : {total_tps_unif} s")
    print(f"  Temps unif. (moyen/cand.) : {moy_tps_unif} s")
    print(f"  Nb unifs (somme)          : {total_nb_unif}")
    print(f"  Temps total (wall)        : {mesures['temps_total_s']:.6f} s")
    print(f"  RAM delta (RSS)           : {mesures['ram_delta_rss_Mo']:.3f} Mo")
    print(f"  RAM pic (tracemalloc)     : {mesures['ram_pic_tracemalloc_Mo']:.3f} Mo")
    print(f"  CPU moyen                 : {mesures['cpu_percent']:.1f} %")
    print("-" * 70)

    # Détail par candidat (utile pour voir les disparités).
    # On limite l'affichage si la liste est très grande pour ne pas spammer la console.
    LIMITE_AFFICHAGE = 20
    print("  Détail par candidat (tps_unif s | nb_unifs) :")
    for i, (tps, nb) in enumerate(liste_resultats[:LIMITE_AFFICHAGE]):
        cand_str = candidats[i] if i < len(candidats) else f"<candidat {i}>"
        # On tronque l'affichage du candidat si trop long pour rester lisible
        cand_aff = (cand_str[:50] + "…") if len(cand_str) > 50 else cand_str
        print(f"    [{i:>3}] {tps:.6f} s | {nb:>6} unifs   ← {cand_aff}")
    if nb_candidats > LIMITE_AFFICHAGE:
        print(f"    … ({nb_candidats - LIMITE_AFFICHAGE} candidats supplémentaires non affichés)")
    print("=" * 70)


def benchmark(candidats: List[str], filename: str, algo: str, structure: str):
    """
    Mesure temps, RAM et CPU de manière uniforme pour permettre la comparaison.

    Paramètres :
      - candidats : liste de chaînes représentant les littéraux candidats à unifier
      - filename  : nom du fichier de jeu de données (dans Util/Serialisation/Output)
      - algo      : "arbre" | "robinson" | "mm"
      - structure : structure de données utilisée par l'algo (pour Robinson/MM)
    """
    touteUnif = True
    pretraitement = False

    # --- chargement des données ---
    print("Début déserialisation")
    predList = deserialiser(os.path.basename(filename), False)
    print(f"Chargé {len(predList)} littéraux")

    # Parsing de TOUS les candidats en objets Litteral.
    # On le fait HORS de la zone chronométrée pour ne mesurer que l'algo lui-même.
    print(f"Parsing de {len(candidats)} candidats")
    realCandidats = [Litteral.from_string(c) for c in candidats]

    # --- Phase algo : on dispatche vers la bonne fonction de bench ---
    print("Debut algo")
    if algo == "arbre":
        # L'arbre de discrimination n'a pas de paramètre "structure"
        mesures = _mesurer_ressources(
            benchmark_arbre_discrimination,
            predList, realCandidats, touteUnif
        )
    elif algo == "robinson":
        mesures = _mesurer_ressources(
            benchRobinson,
            realCandidats, predList, structure, pretraitement, touteUnif
        )
    elif algo == "mm":
        mesures = _mesurer_ressources(
            bench,
            realCandidats, predList, structure, pretraitement, touteUnif
        )
    else:
        raise ValueError(f"Algo inconnu : {algo}")

    _afficher_mesures(algo, structure, candidats, mesures)
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

    # Exemple : on passe maintenant une LISTE de candidats
    listeCandidats = [
        "S(X, b, V, a, Y, j(a), V, Z, b, W, c, d, i(b, X), U, X)",
        "S(a, b, c, a, Y, j(a), V, Z, b, W, c, d, i(b, X), U, X)",
        "P(X, Y, Z)",
    ]

    benchmark(listeCandidats, file, "arbre", "arbre")
