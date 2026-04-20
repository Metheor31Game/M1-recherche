import time
from Util.Litteral.Litteral import Litteral
from Util.Litteral.traiterLitterauxDict import indexer, lit_dict
from Util.Litteral.traiterLitteraux import lit_liste, traiter_litteraux
from Util.Litteral.traiterLitterauxSet import lit_Set, traiterlitterauxSet

def bench(candidat: Litteral, predList: list, structure: str, pretraitement: bool, touteUnif=True):
    
    tps_pretraitement = None
    collection = predList  

    if pretraitement:
        debut = time.perf_counter()
        if structure == "liste":
            collection = predList  
        elif structure == "ensemble":
            collection = set(predList)
        elif structure == "dictionnaire":
           collection = indexer(predList)
        tps_pretraitement = time.perf_counter() - debut

    else:
        if structure == "dictionnaire":
            collection = indexer(predList)
        if structure == "ensemble":
            collection = set(predList)

    debut = time.perf_counter()
    if structure == "liste":
        resultat = lit_liste(candidat, collection, touteUnif)
    elif structure == "ensemble":
        resultat = lit_Set(candidat, collection, touteUnif)
    elif structure == "dictionnaire":
        resultat = lit_dict(candidat, collection, touteUnif)
    tps_unification = time.perf_counter() - debut

   
    print(f"Structure           : {structure}")
    print(f"Temps prétraitement : {tps_pretraitement} s")
    print(f"Temps unification   : {tps_unification} s")

    return (tps_pretraitement, tps_unification)