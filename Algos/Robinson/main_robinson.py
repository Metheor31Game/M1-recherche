import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from Util.TermStore.terme import FabriqueDeTermes, GenerateurDeTermesAleatoires
from Util.TermStore.ListStore import ListStore
from Util.TermStore.SetStore import SetStore
from robinson import unify, afficher, afficherAll, afficherMax

generateur: GenerateurDeTermesAleatoires = GenerateurDeTermesAleatoires(4,4)


def benchmark(n):
    print(f"\n{'='*50}")
    print(f"Benchmark avec {n} termes")
    print(f"{'='*50}")
    
    # Génération des termes dans un set d'abord (pour absolument éviter les doublons)
    start_gen = time.time()
    termes_generes = set()
    while len(termes_generes) < n + 1:
        new_term = generateur.generer_terme_aleatoire()
        termes_generes.add(new_term)
    end_gen = time.time()
    print(f"Temps de génération : {end_gen - start_gen:.4f}s")
    
    # Récupération de t1 (j'aimerai que ce soit une fonction pour que l'unification soit plus interessante)
    t1 = next((t for t in termes_generes if isinstance(t.etiquette, int)), None)
    if t1:
        termes_generes.remove(t1) 

    # On doit refaire les store car sinon t1 serait différent
    temps = []
    stores = [ListStore, SetStore]
    # stores = [SetStore, ListStore]
    for StoreClass in stores:
        print(f"\n{'='*50}")
        # Recréer le store avec les mêmes termes pour chaque test
        store = StoreClass()
        for t in termes_generes:
            store.push(t)
        
        # Unification
        start_unif = time.time()
        afficherMax(t1, store, StoreClass())
        end_unif = time.time()
        print(f"Temps d'unification avec {StoreClass.__name__}: {end_unif - start_unif:.4f}s")
        temps.append(end_unif - start_unif)
    
    #Affichage de la différence : 
    if temps[0] > temps[1]:
        print(f"le store {stores[0].__name__} est plus lent que {stores[1].__name__} de {temps[0] - temps[1]:.4f}s")
    else:
        print(f"le store {stores[1].__name__} est plus lent que {stores[0].__name__} de {temps[1] - temps[0]:.4f}s")


if __name__ == "__main__":
    benchmark(5000000)
    

