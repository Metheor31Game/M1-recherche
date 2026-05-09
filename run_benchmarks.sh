#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================${NC}"
echo -e "${BLUE}   LANCEMENT DE LA CAMPAGNE DE BENCHMARK AUTOMATISEE   ${NC}"
echo -e "${BLUE}========================================================${NC}"

# Boucle sur les 24 jeux de tests
for j in {1..24}
do
    jeu="jeu$j"
    
    # Liste des algorithmes à tester
    for algo in "robinson" "mm" "arbre"
    do
        # Configuration des structures
        if [ "$algo" == "arbre" ]; then
            structures=("unique")
        else
            structures=("liste" "dictionnaire" "ensemble")
        fi 

        for struct in "${structures[@]}"
        do
            # Test avec touteUnif = True puis False
            for unif in "true" "false"
            do
                echo -e "${GREEN}>>> Test en cours : $jeu | $algo | $struct | TouteUnif=$unif${NC}"
                
                # Répétition 10 fois
                for i in {1..10}
                do
                    # Nettoyage du cache
                    ./clean_pycache.sh > /dev/null
                    
                    # Lancement du script python (on ajoute $i pour l'itération)
                    python3 Bench/benchmark.py "$jeu" "$algo" "$struct" "$unif" "$i"
                done
            done
        done
    done
done

echo -e "${BLUE}========================================================${NC}"
echo -e "${BLUE}             TOUS LES TESTS SONT TERMINES              ${NC}"
echo -e "${BLUE}========================================================${NC}"
