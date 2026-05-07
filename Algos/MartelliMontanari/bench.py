import time
from Util.Litteral.Litteral import Litteral
from Util.Litteral.traiterLitterauxDict import indexer, lit_dict
from Util.Litteral.traiterLitteraux import lit_liste, traiter_litteraux
from Util.Litteral.traiterLitterauxSet import lit_Set, traiterlitterauxSet
from Algos.MartelliMontanari.MartelliMontanari import MartelliMontanari, UnificationError
from Util.TermStore.TermList import TermSystem

def bench(candidats: list, predList: list, structure: str, pretraitement: bool, touteUnif=True):
    
    tps_pretraitement = 0.0
    collection = predList  
    resultats = []

    if pretraitement:
        debut = time.perf_counter()

        if structure == "liste":
            # On ne pourra pas filtrer la liste car on travaille sur plusieurs candidat
            collection = predList

        elif structure == "ensemble":
            # On transforme la liste en set 
            collection = set(predList)

        elif structure == "dictionnaire":
            # On transforme la liste en index
            collection = indexer(predList)
            

        tps_pretraitement = time.perf_counter() - debut

    else:
        # Pas de prétraitement mais quand même on transforme en set ou dict 
        if structure == "ensemble":
            collection = set(predList)

        elif structure == "dictionnaire":
            collection = indexer(predList)
        
    for candidat in candidats:
        debut = time.perf_counter() #Ici on mesure le temps d'unification pour chaque candidat
        resultat = {}

        sousCollection = collection
        if structure == "dictionnaire":
            dict = collection.get(candidat.predicat, {})
            
            if candidat.sign:
                sousCollection = dict.get("negatif", [])
            else:
                sousCollection = dict.get("positif", [])
        for l2 in sousCollection:
            # Si il y a pas de prétraitement, le filtre se fait ici pendant l'unification
            if structure != "dictionnaire":
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

        resultats.append(( tps_unification, len(resultat)))

   
    print(f"Structure           : {structure}")
    print(f"Temps prétraitement : {tps_pretraitement} s")
   

    return (tps_pretraitement, resultats)