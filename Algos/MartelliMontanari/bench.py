import time
from Util.Litteral.Litteral import Litteral
from Util.Litteral.traiterLitterauxDict import indexer, lit_dict
from Util.Litteral.traiterLitteraux import lit_liste, traiter_litteraux
from Util.Litteral.traiterLitterauxSet import lit_Set, traiterlitterauxSet
from Algos.MartelliMontanari.MartelliMontanari import MartelliMontanari, UnificationError
from Util.TermStore.TermList import TermSystem

def bench(candidat: Litteral, predList: list, structure: str, pretraitement: bool, touteUnif=True):
    
    tps_pretraitement = None
    collection = predList  

    if pretraitement:
        debut = time.perf_counter()

        if structure == "liste":
            # On filtre la liste pour avoir seulement les candidats éligibles pour l'unification
            collection = []
            for lit in predList:
                if (
                    lit.predicat == candidat.predicat
                    and lit.sign != candidat.sign
                    and lit.arity == candidat.arity
                ):
                    collection.append(lit)

        elif structure == "ensemble":
            # On transforme la liste en set avec filtrage
            collection = set()
            for lit in predList:
                if (
                    lit.predicat == candidat.predicat
                    and lit.sign != candidat.sign
                    and lit.arity == candidat.arity
                ):
                    collection.add(lit)

        elif structure == "dictionnaire":
            # On transforme la liste en index 
            index = indexer(predList)
            if candidat.predicat in index:
                if candidat.sign:
                    collection = index[candidat.predicat]["negatifs"]
                else:
                    collection = index[candidat.predicat]["positifs"]
            else:
                collection = []

        tps_pretraitement = time.perf_counter() - debut

    else:
        # Pas de prétraitement mais quand même on transforme en set ou dict 
        if structure == "ensemble":
            collection = set(predList)

        elif structure == "dictionnaire":
            index = indexer(predList)
            if candidat.predicat in index:
                if candidat.sign:
                    collection = index[candidat.predicat]["negatifs"]
                else:
                    collection = index[candidat.predicat]["positifs"]
            else:
                collection = []

    debut = time.perf_counter() #Ici on mesure le temps d'unification 
    resultat = {}

    for l2 in collection:
        # Si il y a pas de prétraitement, le filtre se fait ici pendant l'unification
        if not pretraitement:
            if l2.predicat != candidat.predicat or l2.sign == candidat.sign or l2.arity != candidat.arity:
                continue

        system = TermSystem()
        for t1, t2 in zip(candidat.enfants, l2.enfants):
            system.add(t1, t2)

        mm = MartelliMontanari(system)
        try:
            resultat[l2] = mm.solve()
            if not touteUnif:
                break  # on s'arrête après la première unification réussie
        except UnificationError:
            pass

    tps_unification = time.perf_counter() - debut

   
    print(f"Structure           : {structure}")
    print(f"Temps prétraitement : {tps_pretraitement} s")
    print(f"Temps unification   : {tps_unification} s")

    return (tps_pretraitement, tps_unification)