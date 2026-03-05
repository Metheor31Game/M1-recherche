import time
from Util.Litteral.Litteral import GenerateurLitteralAleatoire
from Util.Litteral.traiterLitteraux import traiter_litteraux


def bench_traitement():
    
    # paramètres du générateur
    predicats = ["P", "Q", "R", "S"]
    ariteMax = 5
    profondeurMax = 5

    gen = GenerateurLitteralAleatoire(predicats, ariteMax, profondeurMax)

    tailles = [10000, 20000, 50000] 

    print("====== BENCH UNIFICATION ======")

    for n in tailles:

        litteraux = gen.generer_litteraux(n)

        #print("\n--- Littéraux générés aléatoirement ---")
       # for lit in litteraux:
         #   print(lit)

        debut = time.perf_counter()

        comparaisons, succes, echec = traiter_litteraux(litteraux)

        fin = time.perf_counter()

        temps = fin - debut

        print("\n--- Statistiques ---")
        print(f"Comparaisons : {comparaisons}")
        print(f"Unifications réussies : {succes}")
        print(f"Échecs : {echec}")
        print(f"Taille = {n} littéraux | Temps = {temps:.6f} sec")

    print("====== FIN BENCH ======")


if __name__ == "__main__":
    bench_traitement()