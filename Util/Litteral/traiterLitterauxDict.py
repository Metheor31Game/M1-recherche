from Util.TermStore.TermList import TermSystem
from Algos.MartelliMontanari import MartelliMontanari, UnificationError

def indexer_par_predicat(liste_litteraux):

    index = {}

    for lit in liste_litteraux:
        if lit.predicat not in index:
            index[lit.predicat] = []

        index[lit.predicat].append(lit)

    return index

def traiter_litteraux_dict(liste_litteraux):

    succes = 0
    echec = 0
    comparaisons = 0

    index = indexer_par_predicat(liste_litteraux)

    for predicat, groupe in index.items():

        for i in range(len(groupe)):
            for j in range(i+1, len(groupe)):

                l1 = groupe[i]
                l2 = groupe[j]

                comparaisons += 1

                if l1.sign != l2.sign:

                    if l1.arity != l2.arity:
                        echec += 1
                        continue

                    system = TermSystem()

                    for t1, t2 in zip(l1.enfants, l2.enfants):
                        system.add(t1, t2)

                    mm = MartelliMontanari(system)

                    try:
                        unificateur = mm.solve()
                        succes += 1

                    except UnificationError:
                        echec += 1

    print("Fin du traitement.")
    return comparaisons, succes, echec