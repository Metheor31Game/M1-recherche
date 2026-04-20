from Util.TermStore.TermList import TermSystem
from Algos.MartelliMontanari.MartelliMontanari import MartelliMontanari, UnificationError

def traiterlitterauxSet(liste_litteraux):

    ensemble = set(liste_litteraux)

    succes = 0
    echec = 0
    comparaisons = 0

    for l1 in ensemble:
        for l2 in ensemble:
            if l1.predicat == l2.predicat and l1.sign and not l2.sign:
                comparaisons += 1

                if l1.arity != l2.arity:
                    echec += 1
                    continue

                system = TermSystem()

                for t1, t2 in zip(l1.enfants, l2.enfants):
                    system.add(t1, t2)

                mm = MartelliMontanari(system)

                try:
                    unificateur=mm.solve()
                    #print("Unification réussie")
                    succes += 1

                    if unificateur.is_empty():
                     #print("   (Système vide : les termes étaient identiques)")
                     pass
                    else:
                        for eq in unificateur.equations:
                            pass
                except UnificationError:
                    echec += 1
    print("Fin du traitement.")
    return comparaisons, succes, echec


def lit_Set(l1,list_litteraux, touteUnif=True):
    resultat = {}
    ensemble = set(list_litteraux)
    for l2 in ensemble:
        if l1.predicat == l2.predicat and l1.sign != l2.sign and l1.arity == l2.arity:
            system = TermSystem()

            for t1, t2 in zip(l1.enfants, l2.enfants):
                system.add(t1, t2)

            mm = MartelliMontanari(system)
            try:
                unificateur=mm.solve()
                resultat[l2] = unificateur
                if not touteUnif:
                    return resultat # Ici on retourne dès la première unification réussie
            except UnificationError:
                pass
    return resultat