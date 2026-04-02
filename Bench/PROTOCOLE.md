# Protocole de benchmark

## Remarques Générales
 
1. Les **algorithmes** à tester sont : Robinson, Martelli-Montanari et le Discrimination Tree.
 
2. Les **structures de données** à tester sont : Listes, Ensembles, Dictionnaires et le Discrimination Tree.
 
3. D'après les points 1 et 2, le Discrimination Tree est un cas **à part**.
 
4. D'après les points précédents, il faudra donc tester :
   - **Robinson** sur des **listes** ;
   - **Robinson** sur des **ensembles** ;
   - **Robinson** sur des **dictionnaires** ;
   - **Martelli-Montanari** sur des **listes** ;
   - **Martelli-Montanari** sur des **ensembles** ;
   - **Martelli-Montanari** sur des **dictionnaires** ;
   - **Discrimination Tree**.
 
5. Ces tests doivent être effectués sur la/les même(s) **banque(s) de données**.
 
6. La **génération de ces données** représente un enjeu important pour ce protocole.
 
7. Ces données devront être : **conséquentes** (en nombre), **représentatives** (en cas) et **variées**.
 
8. Les **résultats** de ces différents tests doivent être **identiques**.
 
9. Pour vérifier facilement que ces différents résultats soient les mêmes, ils doivent avoir le **même format**.
 
10. L'utilisation de Python ne doit **pas** être un facteur dans ces tests — en d'autres termes, ce protocole devra être perméable à ce que l'on appellera les pythoneries™©®.
   > *"pythoneries"* est une marque déposée de notre équipe de recherche. Toute reproduction, même partielle, même en Python, est — ironiquement — strictement interdite. Les contrevenants seront contraints de réécrire leur code en PROLOG.

11. Voici des mesures intéréssantes à envisager :
   - Le **temps** d'exécution ;
   - Le **nombre d'opérations** effectuées ;
   - L'**espace mémoire** utilisé ;
   - La **taille** des termes (en nombre de caractères) ;
   - La **profondeur** des termes ;
   - La **taille** des query termes (en nombre de caractères) ;
   - La **profondeur** des query termes.

12. Il serait intéressant de tester plusieurs unifications (donc plusieurs query termes)

13. Il faudra préciser pour chaque tests les **paramètres** utilisés (signature de notre banque de données)

14. On pourra pour chaque couple (algo, structure) tester :
   - La **première** unification trouvée ;
   - **Toutes** les unifications possibles ;
   - **Echec** d'unification.

15. Faire **échouer** une unification avec des termes aléatoires et nombreux est très compliqué.

16. Les différents tests devront être lancés depuis **la même machine**, dans **les mêmes conditions**.

## Format d'entrée

- Plusieurs échelles (10 000, 100 000 puis 1 000 000) ;

- Les différentes échelles testeront les mêmes signatures ;

- Au sein de chaque échelle, plusieurs banques avec paramètres différents (profondeur max différente) ;

- Une signature par banque de données ;
   * Symboles de variables ;
   * Symboles de fonctions et arités ;
   * Symboles de prédicats et arités ;
   * Symboles de constantes

- Littéraux aléatoires ;
   * Vérifier la "qualité" de l'aléa.

- Générées dans des fichiers à part ;
   * Format à réfléchir (.json, .txt compressé ou non, .py séparé).

## Format de sortie

- Doit être le même pour chaque test (comparaison plus rapide) ;
   * donc suivre le même format.

- 
