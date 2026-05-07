import os
import sys
import time
import tracemalloc  # mesure fine de l'allocation mémoire côté Python
import psutil       # mesure système (RAM résidente, CPU du processus)
import gzip
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from Util.Litteral.Litteral import Litteral
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

    Le résultat brut a la forme :
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
    pretraitement = True

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
    filename = "jeu5"
    file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "Util",
        "Serialisation",
        "Output",
        filename,
    )

    listeCandidats1 = [
        "¬P(U, V, W)",
        "P(a, X, Y)",
        "¬P(h(Z), U, V)",
        "Q(U, V, W, X, Y, Z)",
        "¬Q(a, b, U, V, W, X)",
        "Q(f(U, V), g(W, X, Y), c, Z, U, V)",
        "¬R(U, V, W, X, Y, Z, U)",
        "R(a, b, U, V, W, X, Y)",
        "¬R(k(U, V), i(W), l(X, Y), d, Z, U, V)"
    ]

    listeCandidats2 = [
        "¬P(X, Y)",
        "P(a, b)",
        "¬P(f(X, Y), g(a))",
        "Q(X, Y, Z, W)",
        "¬Q(a, b, c, d)",
        "Q(f(X, Y), g(Z, W, Y), h(a), b)",
        "¬R(U, V)",
        "R(e, f)",
        "¬R(i(U), j(V, a))"
    ]

    listeCandidats3 = [
        "¬P(U, V)",
        "P(a, W)",
        "¬P(h(X), Y)",
        "Q(U, V, W, X, Y, Z)",
        "¬Q(a, b, U, V, W, X)",
        "Q(f(U, V), i(W), c, X, Y, Z)",
        "¬R(U, V, W, X, Y, Z, U, V, W)",
        "R(a, b, c, U, V, W, X, Y, Z)",
        "¬R(f(U, V), g(W, X, Y), h(Z), i(U), d, V, W, X, Y)"
    ]

    listeCandidats4 = [
        "¬P(U, V, W, X, Y, Z, U, V)",
        "P(a, b, U, V, W, X, Y, Z)",
        "¬P(f(U, V), g(W, X, Y), h(Z), a, U, V, W, X)",
        "Q(U, V)",
        "¬Q(a, U)",
        "Q(f(U, V), W)",
        "¬R(U, V, W, X, Y, Z, U, V, W, X)",
        "R(a, b, c, U, V, W, X, Y, Z, U)",
        "¬R(f(U, V), g(W, X, Y), h(Z), i(U), a, V, W, X, Y, Z)"
    ]

    listeCandidats5 = [
        "P(U, V, W, X, Y, Z, U, V)",
        "¬P(a, b, U, V, W, X, Y, Z)",
        "P(f(U, V), g(W, X, Y), h(Z), a, U, V, W, X)",
        "¬Q(U, V, W)",
        "Q(a, U, V)",
        "¬Q(f(U, V), a, W)",
        "R(U, V, W, X, Y, Z, U)",
        "¬R(a, b, U, V, W, X, Y)",
        "R(f(U, V), g(W, X, Y), h(Z), a, U, V, W)"
    ]

    listeCandidats6 = [
        "Q(X)",
        "¬Q(a)",
        "Q(f(X, Y))",
        "P(X, Z)",
        "¬P(a, f(X, e))",
        "P(i(X), g(X, W, a))",
        "¬R(X, f(X, W), Y, X, Z)",
        "R(Y, g(a, X, W), V, k(h(Z),X), U)",
        "¬R(i(h(f(X,Y))), W, e, U, V)"

    ]

    listeCandidats7 = [
        "¬P(X, Y, Z)",
        "P(g(X, e, Y), h(e), j(Z, W, Z))",
        "P(h(h(h(h(j(X, Y, e))))), k(f(X, b), Y), Z)",
        "¬Q(X, Y, Z, W, U, V)",
        "Q(i(a), U, g(h(U), V, e), f(X, d), k(i(Z), W), Z)",
        "¬Q(X, e, Y, b, Z, W)",
        "R(X, Z, W, Y, V, U, e)",
        "¬R(e, Y, a, Y, h(X), V, W)",
        "R(X, d, W, Y, V, U, e)",

    ]

    listeCandidats8 = [
        "¬P(X,V)",
        "P(Y,i(g(X, e, h(W))))",
        "¬P(k(i(V),  Z), l(h(U), d))",
        "¬Q(X, V, U, W, Y, Z, V)",
        "Q(Y, c, W, d, X, h(U), c)",
        "¬Q(W, c, Y, h(i(V)), X, l(Z, e), U)",
        "R(X, Y, Z, W, U, V, W, Y)",
        "R(X, a, Z, d, U, V, W, e)",
        "R(h(Y), Y, i(Z), W, e, V, W, a)",
    ]

    listeCandidats9 = [
        "¬P(U, V, W, X, Y)",
        "P(X, a, Y, Z, b)",
        "¬P(f(X, a), Y, h(V), c, Z)",
        "Q(V, W, X, Y)",
        "¬Q(U, c, Z, d)",
        "Q(g(X, b, Y), i(Z), a, V)",                 
        "¬R(U, V, W, X, Y, Z)",
        "R(X, a, Y, b, Z, e)",
        "¬R(j(U, k(V, a), W), l(X, Y), Z, d, h(b), i(V))"
    ]
    
    listeCandidats10 = [
        "P(U, V, W, X, Y, Z, U)",
        "¬P(U, V, W, X, Y, a, b)",
        "P(Z, W, h(W), c, Y, b, X)",
        "¬Q(X, Y, Z)",
        "Q(U, a, V)",
        "¬Q(j(X, b, Y), k(Z, c), l(U, V))",
        "R(Z, Y, X, W, V, U, Z)",
        "¬R(Z, Y, X, W, c, d, e)",
        "R(j(X, Y, Z), k(U, V), l(W, a), f(b, c), h(i(X)), Y, Z)"
    ]

    listeCandidats11 = [
        "¬P(U, V, W, X, Y, Z, U, V, W)",
        "P(U, V, W, X, Y, Z, a, b, c)",
        "¬P(f(U, V), g(W, X, Y), Z, U, j(V, a, W), k(X, b), l(Y, c), Z, X)",
        "Q(X, Y, Z)",
        "¬Q(U, V, a)",
        "Q(f(X, Y), g(Z, a, b), h(U))",
        "¬R(W, Y)",
        "R(Z, b)",
        "¬R(k(V, W), i(j(Z, a, b)))"
    ]

    listeCandidats12 = [
        "P(U, V, W, X)",
        "¬P(U, V, a, b)",
        "P(f(U, a), g(V, b, c), W, X)",
        "¬Q(U, V)",
        "Q(W, c)",
        "¬Q(h(X), Y)",
        "R(U, V, W, X, Y, Z, Y)",
        "¬R(U, V, W, a, b, c, Y)",
        "R(j(U, d, V), k(W, e), i(X), f(Y, a), Z, U, Y)"
    ]

    listeCandidats13 = [
        "¬P(U, V, W, X, Y, Z, U)",
        "P(U, V, W, X, a, b, c)",
        "¬P(f(U, V), g(W, a, b), h(c), i(d), X, Y, Z)",
        "Q(U, V, W, X)",
        "¬Q(U, V, a, b)",
        "Q(j(U, V, a), k(W, b), X, Y)",
        "¬R(Z, Y, X, W)",
        "R(Z, Y, c, d)",
        "¬R(l(Z, a), f(Y, b), X, W)",
        "S(U, V, W, X, Y, Z)",
        "¬S(U, V, W, a, b, c)",
        "S(g(U, a, b), h(c), i(d), V, W, X)",
        "¬T(U, V, W, X, Y, Z, U, V, W)",
        "T(U, V, W, X, Y, Z, a, b, c)",
        "¬T(j(U, V, a), k(W, b), l(X, c), f(Y, d), g(Z, a, b), U, V, W, X)",
        "U(Z, Y, X, W, V, U, Z)",
        "¬U(Z, Y, X, W, a, b, c)",
        "U(i(Z), h(Y), k(X, a), l(W, b), V, U, Z)"

    ]

    listeCandidats14 = [
        "P(U, V, W, X, Y, Z, U)",
        "¬P(V, W, X, Y, a, b, c)",
        "P(f(U, V), g(W, a, b), h(c), i(d), X, Y, Z)",
        "¬Q(U, V, W, X, Y, Z, U, V, W)",
        "Q(X, Y, Z, U, V, a, b, c, d)",
        "¬Q(j(W, a, b), k(X, c), l(Y, d), h(e), i(Z), U, V, W, X)",
        "R(U, V, W, X, Y, Z, U, V)",
        "¬R(W, X, Y, Z, a, b, c, d)",
        "R(f(U, a), g(V, b, c), h(d), i(e), j(W, a, b), X, Y, Z)",
        "¬S(U, V, W)",
        "S(X, Y, a)",
        "¬S(k(Z, U), l(V, b), W)",
        "T(U, V, W, X, Y, Z, U, V, W, X)",
        "¬T(Y, Z, U, V, W, X, a, b, c, d)",
        "T(f(U, V), g(W, a, b), h(c), i(d), j(X, e, a), k(Y, b), Z, U, V, W)",
        "¬U(Z, Y, X, W, V, U, Z, Y)",
        "U(X, W, V, U, a, b, c, d)",
        "¬U(l(Z, a), k(Y, b), j(X, c, d), i(e), h(W), V, U, Z)"
    ]

    listeCandidats15 = [
        "¬P(U, V, W, X, Y, Z, U, V)",
        "P(W, X, Y, Z, a, b, c, d)",
        "¬P(f(U, a), g(V, b, c), h(d), i(e), k(W, d), X, Y, Z)",
        "Q(U, V, W, X, Y, Z, U)",
        "¬Q(V, W, X, Y, a, b, c)",
        "Q(j(U, V, a), l(W, b), f(X, c), d, Y, Z, U)",
        "¬R(U)",
        "R(a)",
        "¬R(h(V))",
        "S(U, V, W, X, Y, Z)",
        "¬S(U, V, W, a, b, c)",
        "S(g(U, V, a), k(W, b), i(c), d, X, Y)",
        "¬T(U, V, W, X, Y)",
        "T(Z, U, V, a, b)",
        "¬T(f(W, a), j(X, b, c), d, Y, Z)",
        "U(Z)",
        "¬U(e)",
        "U(l(X, Y))"
    ]

    listeCandidats16 = [
        "P(U, V, W, X, Y, Z, U, V, W)",
        "¬P(X, Y, Z, U, a, b, c, d, e)",
        "P(f(U, a), g(V, b, c), h(d), i(e), j(W, a, b), X, Y, Z, U)",
        "¬Q(V, W)",
        "Q(X, a)",
        "¬Q(k(Y, b), Z)",
        "R(U, V, W)",
        "¬R(X, a, b)",
        "R(l(Y, c), f(Z, d), U)",
        "¬S(U, V, W, X, Y, Z, U, V)",
        "S(W, X, Y, Z, a, b, c, d)",
        "¬S(g(U, V, a), k(W, b), i(c), h(d), l(X, e), Y, Z, U)",
        "T(U, V, W, X, Y, Z)",
        "¬T(a, b, c, d, e, U)",
        "T(f(V, a), g(W, b, c), h(d), i(e), X, Y)",
        "¬U(Z, Y, X, W, V, U, Z, Y)",
        "U(a, b, c, d, e, X, Y, Z)",
        "¬U(j(U, V, a), k(W, b), l(X, c), f(Y, d), g(Z, a, b), U, V, W)"
    ]

    listeCandidats17 = [
        "¬P(U, V)",
        "P(W, a)",
        "¬P(f(X, Y), Z)",
        "Q(U, V, W, X, Y, Z)",
        "¬Q(U, V, a, b, c, d)",
        "Q(g(W, a, b), h(X), i(Y), Z, U, V)",
        "¬R(U, V, W, X, Y, Z, U, V)",
        "R(W, X, Y, Z, a, b, c, d)",
        "¬R(j(U, V, a), k(W, b), l(X, c), d, Y, Z, U, V)",
        "S(Z, Y, X, W, V, U)",
        "¬S(a, b, c, d, e, Z)",
        "S(f(Y, a), g(X, b, c), h(W), i(V), U, Z)",
        "¬T(U, V, W, X)",
        "T(Y, Z, a, b)",
        "¬T(j(U, V, a), k(W, b), X, Y)",
        "U(Z)",
        "¬U(c)",
        "U(l(X, Y))"
    ]

    listeCandidats18 = [
        "P(U, V, W, X, Y, Z, U, V, W)",
        "¬P(X, Y, Z, a, b, c, d, e, U)",
        "P(f(U, a), g(V, b, c), h(W), i(X), j(Y, Z, a), U, V, W, X)",
        "¬Q(Z, Y, X, W, V, U, Z, Y)",
        "Q(X, W, V, U, a, b, c, d)",
        "¬Q(k(U, a), l(V, b), f(W, c), g(X, d, e), Y, Z, U, V)",
        "R(U, V)",
        "¬R(a, W)",
        "R(h(X), Y)",
        "¬S(Z, Y)",
        "S(X, b)",
        "¬S(i(W), V)",
        "T(U, V)",
        "¬T(c, W)",
        "T(k(X, d), Y)",
        "¬U(Z, Y, X)",
        "U(a, b, W)",
        "¬U(j(V, U, e), l(Z, a), Y)"
    ]

    listeCandidats19 = [
        "¬P(U, V, W, X, Y, Z)",
        "P(a, b, c, U, V, W)",
        "¬P(f(X, a), g(Y, Z, b), h(U), V, W, X)",
        "Q(U, V, W, X, Y, Z, U, V, W)",
        "¬Q(a, b, c, d, e, X, Y, Z, U)",
        "Q(j(V, W, a), k(X, b), l(Y, c), h(Z), i(U), V, W, X, Y)",
        "¬R(U, V, W, X, Y)",
        "R(a, b, Z, U, V)",
        "¬R(f(W, X), g(Y, Z, a), b, c, d)",
        "S(U, V, W, X)",
        "¬S(a, b, Y, Z)",
        "S(k(U, V), l(W, X), a, b)",
        "¬T(U, V, W, X, Y, Z, U, V, W)",
        "T(a, b, c, d, e, X, Y, Z, U)",
        "¬T(j(V, W, a), k(X, b), l(Y, c), h(Z), i(U), V, W, X, Y)",
        "U(U, V, W, X, Y, Z, U)",
        "¬U(a, b, c, d, V, W, X)",
        "U(f(Y, Z), g(U, V, a), h(W), i(X), Y, Z, U)"
    ]

    listeCandidats20 = [
        "P(U, V, W, X)",
        "¬P(a, b, Y, Z)",
        "P(f(U, V), g(W, X, a), b, c)",
        "¬Q(U, V, W, X, Y, Z, U)",
        "Q(a, b, c, d, V, W, X)",
        "¬Q(h(Y), i(Z), j(U, V, a), k(W, X), b, c, d)",
        "R(U)",
        "¬R(a)",
        "R(h(V))",
        "¬S(U, V, W, X, Y, Z, U, V, W)",
        "S(a, b, c, d, e, X, Y, Z, U)",
        "¬S(f(V, W), g(X, Y, a), h(Z), i(U), V, W, X, Y, Z)",
        "T(U, V, W, X, Y, Z, U, V, W)",
        "¬T(e, d, c, b, a, Z, Y, X, W)",
        "T(j(U, V, a), k(W, X), l(Y, Z), h(U), i(V), W, X, Y, Z)",
        "¬U(U, V, W, X, Y, Z, U, V, W)",
        "U(a, b, c, d, e, X, Y, Z, U)",
        "¬U(f(V, W), g(X, Y, a), h(Z), i(U), V, W, X, Y, Z)"
    ]

    listeCandidats21 = [
        "P(U, V, W, X, Y, Z, U, V, W)",
        "¬P(a, b, c, d, e, X, Y, Z, U)",
        "P(f(V, W), g(X, Y, Z), h(U), i(V), j(W, X, a), Y, Z, U, V)",
        "¬Q(U, V, W, X, Y, Z, U, V)",
        "Q(a, b, c, d, e, X, Y, Z)",
        "¬Q(k(U, V), l(W, X), f(Y, a), g(Z, U, b), V, W, X, Y)",
        "R(Z, Y, X, W, V, U, Z, Y, X)",
        "¬R(e, d, c, b, a, U, V, W, X)",
        "R(j(Y, Z, a), k(U, V), l(W, X), h(Y), i(Z), U, V, W, X)",
        "¬S(U, V, W, X, Y, Z)",
        "S(a, b, c, U, V, W)",
        "¬S(f(X, Y), g(Z, U, a), h(V), W, X, Y)",
        "T(U, V, W, X)",
        "¬T(a, b, Y, Z)",
        "T(k(U, V), l(W, X), Y, Z)",
        "¬U(U, V, W, X, Y, Z, U, V, W)",
        "U(a, b, c, d, e, X, Y, Z, U)",
        "¬U(f(V, W), g(X, Y, Z), h(U), i(V), j(W, X, a), Y, Z, U, V)"
    ]

    listeCandidats22 = [
        "¬P(U, V, W, X, Y, Z, U, V, W)",
        "P(a, b, c, d, e, f, X, Y, Z)",
        "¬P(f(U, V), g(W, X, a), h(Y), i(Z), j(U, V, b), W, X, Y, Z)",
        "Q(Z, Y, X, W, V, U, Z, Y, X)",
        "¬Q(a, b, c, d, e, f, g, X, Y)",
        "Q(j(U, V, a), k(W, X), l(Y, Z), h(U), i(V), W, X, Y, Z)",
        "¬R(U, V, W, X, Y, Z, U, V)",
        "R(X, Z, W, Y, U, f, X, Y)",
        "¬R(f(V, W), g(X, Y, a), h(Z), i(U), j(V, b, c), X, Y, Z)",
        "S(U, V, W, X, Y, Z, U, V, W, X)",
        "¬S(a, b, c, d, e, f, g, h, X, Y)",
        "S(f(U, V), g(W, X, a), h(Y), i(Z), j(U, b, c), k(V, d, e), W, X, Y, Z)",
        "¬T(U, V, W, X, Y)",
        "T(a, b, c, X, Y)",
        "¬T(f(U, V), g(W, X, a), h(Y), Z, U)",
        "U(Z, Y, X, W, V, U)",
        "¬U(a, b, c, d, X, Y)",
        "U(i(U), j(V, W, a), k(X, b), l(Y, c), Z, U)"
    ]

    listeCandidats23 = [
        "¬P(U, V, W)",
        "P(a, b, X)",
        "¬P(f(U, V), g(W, X, Y), h(Z))",
        "Q(X, Y, Z)",
        "¬Q(c, d, e)",
        "Q(i(U), j(V, W, a), k(X, Y))",
        "¬R(Z, Y, X)",
        "R(b, c, U)",
        "¬R(l(V, W), f(X, Y), g(Z, a, b))",
        "S(U, V, W, X)",
        "¬S(a, b, c, d)",
        "S(h(U), i(V), j(W, X, a), Y)",
        "¬T(U, V, W, X, Y, Z)",
        "T(a, b, c, d, e, X)",
        "¬T(f(U, V), g(W, X, Y), h(Z), i(U), j(V, W, a), b)",
        "U(U, V, W, X, Y, Z, U, V, W)",
        "¬U(a, b, c, d, e, X, Y, Z, U)",
        "U(k(U, V), l(W, X), f(Y, Z), g(U, V, a), h(W), i(X), j(Y, Z, b), c, d)"
    ]

    listeCandidats24 = [
        "¬P(U, V, W, X)",
        "P(a, b, c, Y)",
        "¬P(f(U, V), g(W, X), h(Y), a)",
        "Q(U, V, W, X, Y, Z, U, V, W)",
        "¬Q(a, b, c, d, e, f, g, h, X)",
        "Q(f(U, V), g(W, X, a), h(Y), i(Z), j(U), k(V), l(W), X, Y)",
        "¬R(U, V, W, X, Y, Z, U)",
        "R(a, b, c, d, e, f, X)",
        "¬R(f(U, V), g(W, X, a), h(Y, Z), i(U), V, W, X)",
        "S(U, V, W, X, Y, Z, U, V, W, X)",
        "¬S(a, b, c, d, e, f, g, h, i, X)",
        "S(f(U, V), g(W, X, a), h(Y, Z), i(U, b), j(V, c), k(W, d), l(X, e), Y, Z, a)",
        "¬T(U, V, W, X, Y)",
        "T(a, b, c, d, Z)",
        "¬T(f(U, V), g(W, X), h(Y, a, b), c, d)",
        "U(Z, Y, X, W, V, U, Z, Y, X, W)",
        "¬U(a, b, c, d, e, f, g, h, i, j)",
        "U(k(U, V), l(W, X), m(Y, Z, a), n(U, b), o(V, c), p(W, d), q(X, e), r(Y, f), Z, a)"
    ]

    benchmark(listeCandidats5, file, "robinson", "dictionnaire")
    # benchmark(listeCandidats5, file, "mm", "dictionnaire")
    # benchmark(listeCandidats5, file, "arbre", "liste")
