from Util.TermStore.TermList import TermSystem
from Algos.MartelliMontanari.MartelliMontanari import MartelliMontanari, UnificationError

def indexer(liste_litteraux):

    index = {}

    for lit in liste_litteraux:
        if lit.predicat not in index:
            index[lit.predicat] = {"positifs": [], "negatifs": []}

        if lit.sign:
            index[lit.predicat]["positifs"].append(lit)
        else:
            index[lit.predicat]["negatifs"].append(lit)

    return index

def traiter_litteraux_dict(liste_litteraux):

    succes = 0
    echec = 0
    comparaisons = 0

    index = indexer(liste_litteraux)

    for predicat, groupe in index.items():
        positifs = groupe["positifs"]
        negatifs = groupe["negatifs"]

        for i in range(len(positifs)):
            for j in range(len(negatifs)):

                l1 = positifs[i]
                l2 = negatifs[j]

                comparaisons += 1

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