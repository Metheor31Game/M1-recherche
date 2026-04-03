from Util.TermStore.TermList import TermSystem
from Util.TermStore.StructureMM.TermeArbre import TermeArbre
from Util.TermStore.StructureMM.TermeDict import TermeDict
from Algos.MM.MartelliMontanari import MartelliMontanari, UnificationError


def _construire_system(l1, l2, structure: str) -> TermSystem:
    """
    Construit un TermSystem à partir de deux littéraux en choisissant
    la structure de données utilisée pour représenter les termes.

    Chaque littéral est converti en un seul terme dont la racine est
    le prédicat — ex : P(f(X), a) devient un terme avec P comme racine.

    Args:
        l1        (Litteral) : premier littéral
        l2        (Litteral) : second littéral
        structure (str)      : "arbre", "dict" ou "liste"
    Returns:
        TermSystem : système prêt pour MM
    """
    system = TermSystem()

    if structure == "arbre":
        system.add(
            TermeArbre.depuis_litteral(l1),
            TermeArbre.depuis_litteral(l2)
        )
    elif structure == "dict":
        system.add(
            TermeDict.depuis_litteral(l1),
            TermeDict.depuis_litteral(l2)
        )
    else:
        raise ValueError(f"Structure inconnue : {structure}. Choisir 'arbre', 'dict'.")

    return system


def traiter_litteraux(liste_litteraux, structure: str = "arbre"):
    """
    Traitement naïf O(n²) : compare toutes les paires de littéraux.

    Pour chaque paire (l1, l2) :
        - même prédicat
        - signes opposés (l1 positif, l2 négatif ou inversement)
        - même arité
    On tente l'unification via MM sur la structure choisie.


    Args:
        liste_litteraux (List[Litteral]) : liste des littéraux à traiter
        structure       (str)            : structure de données pour MM
                                          "arbre" | "dict" | "liste"
    Returns:
        tuple : (comparaisons, succes, echec)
    """
    succes      = 0
    echec       = 0
    comparaisons = 0

    for i in range(len(liste_litteraux)):
        for j in range(i + 1, len(liste_litteraux)):

            l1 = liste_litteraux[i]
            l2 = liste_litteraux[j]

            #  même prédicat
            if l1.predicat != l2.predicat:
                continue

            # signes opposés (P et ¬P)
            if l1.sign == l2.sign:
                continue

            comparaisons += 1

            # même arité
            if l1.arity != l2.arity:
                echec += 1
                continue

            # Construction du système avec la structure choisie
            system = _construire_system(l1, l2, structure)
            mm     = MartelliMontanari(system)

            try:
                mm.solve()
                succes += 1
            except UnificationError:
                echec += 1

    print(f"[traiter_litteraux | {structure}] "
          f"comparaisons={comparaisons}, succes={succes}, echec={echec}")
    return comparaisons, succes, echec
