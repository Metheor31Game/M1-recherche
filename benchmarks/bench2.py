import psutil
import os
import time


from unification.utils.logique.litteral import GenerateurLitteralAleatoire
from unification.martelli_montanari import traiterLitterauxDict


def bench_traitement():
    
    # paramètres du générateur
    predicats = ["P", "Q", "R", "S"]
    ariteMax = 5
    profondeurMax = 5

    gen = GenerateurLitteralAleatoire(predicats, ariteMax, profondeurMax)

    tailles = [1000, 5000, 10000, 50000]  # différentes tailles de listes de littéraux à tester

    #print("====== BENCH UNIFICATION ======")

    for n in tailles:

        litteraux = gen.generer_litteraux(n)

        #print("\n--- Littéraux générés aléatoirement ---")
        #for lit in litteraux:
         #  print(lit)
        
        process = psutil.Process(os.getpid())
        ram_avant = process.memory_info().rss

        debut = time.perf_counter()

        comparaisons, succes, echec = traiterLitterauxDict(litteraux)

        fin = time.perf_counter()

        ram_apres = process.memory_info().rss
        ram_utilisee = (ram_apres - ram_avant) / (1024*1024)

        temps = fin - debut

        print("\n--- Statistiques ---")
        print(f"Comparaisons : {comparaisons}")
        print(f"Unifications réussies : {succes}")
        print(f"Échecs : {echec}")
        print(f"Taille = {n} littéraux | Temps = {temps:.6f} sec")
        print(f"RAM utilisée : {ram_utilisee:.2f} MB")

    print("====== FIN BENCH ======")


if __name__ == "__main__":
    bench_traitement()