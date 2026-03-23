import sys
import os

racine_projet = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(os.path.abspath(racine_projet))

from Util.TermStore.terme import NoeudTerme, ETIQUETTE_CONS, ETIQUETTE_VAR
from Util.Litteral.Litteral import Litteral
from typing import List, Dict, Any, Optional, Tuple, NamedTuple


# Normalisation différente selon si var dans l'arbre ou dans le terme recherché 
NORM_VAR_ARBRE = "*"    # Exemple :  f(X, Y) -> ['f', '*1', '*2']
NORM_VAR_REQUETE = "?"  # Exemple :  f(X, Y) -> ['f', '?1', '?2']

# Préfixe pour signe prédicat
SYMBOLE_PREDICAT_POSITIF = "+"
SYMBOLE_PREDICAT_NEGATIF = "¬"

# Types ========================================================

class ResultatRecherche(NamedTuple):
    """
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║       Format de résultat proposé par IA (ClaudeCode).          ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    Résultat d'une recherche de termes unifiables dans l'arbre de discrimination.

    Attributes:
        substitution    (Dict[str, NoeudTerme])     :   Substitution associant les noms des varibales originaux
                                                            du terme de recherche à leur séquence de symboles en notation préfixe.
        pointeurs       (List[Any])                 :   Pointeurs associés au terme unifiable trouvé dans l'arbre    

    """
    substitution: Dict[str, NoeudTerme]
    pointeurs: List[Any]

class PointeurFeuille(NamedTuple):
    """
    Données stockées aux feuilles.
    Utile pour valider une substitution candidates, on garde le prédicat stocké.

    Attributes:
        predicat    (Litteral)      :   Prédicat original inséré
        pointeur    (Any)           :   Pointeur associé à ce terme
    """
    predicat: Litteral
    pointeur: Any

# Structure Arbre ========================================================

class NoeudArbreDeDiscrimination:
    """
    Classe d'un noeud dans l'arbre de discrimination.

    Attributes:
        symbole     (Optional[str])                             :   Symbole représentant le noeud (ex : X, f, a, etc.). 
                                                                    'None' pour le noeud racine.
        enfants     (Dict[str, 'NoeudArbreDeDiscrimination'])   :   Noeuds enfants, indexés par leur symbole.
        pointeurs   (List[PointeurFeuille])                     :   Pointeurs vers les termes associés à ce noeud.
    """
    def __init__(self, symbole: Optional[str] = None) -> None:
        self.symbole = symbole # Symbole du noeud (None pour la racine)
        self.enfants: Dict[str, NoeudArbreDeDiscrimination] = {}
        self.pointeurs: List[PointeurFeuille] = []
        self._pointeurs_ids: set = set()

# Arbre de Discrimination ========================================================

class ArbreDeDiscrimination:
    """
    Arbre de discrimination pour stocker des termes. 
    Permet la recherche de termes unifiables.

    Les termes sont représentés en notation préfixe aplatie.
    
    Chaque chemin racine -> feuille encore un terme.
    
    Attributes:
        racine ('NoeudArbreDeDiscrimination')   :   Noeud racine de l'arbre. 'None' par défaut
        arites (Dict[str, int])                 :   Dictionnaire pour stocker l'arité de chaque symbole dans l'arbre
    """
    
    def __init__(self) -> None:
        self.racine = NoeudArbreDeDiscrimination()
        self.arites: Dict[str, int] = {} # Stocker les arités de tous les symboles

    # Insertion ----------------------------------------------------

    def inserer(self, predicat: Litteral, pointeur: Any) -> None:
        """
        Insère un prédicat dans l'arbre de discrimination avec un pointeur associé.

        Le prédicat est parcouru en ordre préfixe pour créer un seul chemin dans l'arbre.
        Par exemple, P(f(X, g(Y)), X) crée le chemin : P -> f -> *1 -> g -> *2 -> *1

        Args:
            prédicat    (Litteral)      :   Le prédicat à insérer dans l'arbre
            pointeur    (Any)           :   Un pointeur à associer avec ce prédicat.
        """

        # Mise à plat du terme en une séquence de symboles issue d'un parcours préfixe
        # On normalise aussi les variables  :
        var_map: Dict[str, str] = {}
        predicat_mis_a_plat = self._mise_a_plat_predicat(predicat, var_map, NORM_VAR_ARBRE)
        
        # Insertion dans l'arbre :
        noeud_courant = self.racine
        for symbole in predicat_mis_a_plat:
            if symbole not in noeud_courant.enfants:
                noeud_courant.enfants[symbole] = NoeudArbreDeDiscrimination(symbole)
            noeud_courant = noeud_courant.enfants[symbole]
        
        # Ajout du pointeur au noeud feuille :
        pointeur_id = id(pointeur) if not isinstance(pointeur, str) else pointeur
        if pointeur_id not in noeud_courant._pointeurs_ids:
            noeud_courant._pointeurs_ids.add(pointeur_id)
            noeud_courant.pointeurs.append(PointeurFeuille(predicat=predicat, pointeur=pointeur))

    # Recherche ----------------------------------------------------

    def rechercher(self, predicat: Litteral) -> List[ResultatRecherche]:
        """
        Recherche les prédicats unifiables avec le prédicat donné dans l'arbre de discrimination.
        
        Pour chaque prédicat unifiable, on retourne la substitution ainsi que le pointeur associé.
        Ainsi on sait comment instancier les variables afin de réaliser l'unification.

        Args:
            predicat    (Litteral)  :   Le prédicat que l'on souhaite unifier à notre arbre.
        Returns:
            List[ResultatRecherche] :   Liste des résultats (comprenant donc pointeur et substitution)
        """

        # Mise à plat du terme recherché :
        var_map: Dict[str, str] = {}
        predicat_mis_a_plat = self._mise_a_plat_predicat(predicat, var_map, NORM_VAR_REQUETE)
        
        # Cache local
        cache_profondeur: Dict[int, int] = {}
        def profondeur_cached(index: int) -> int:
            if index not in cache_profondeur:
                cache_profondeur[index] = self._calculer_profondeur_depuis_index(
                    index, predicat_mis_a_plat, profondeur_cached
                )
            return cache_profondeur[index]

        # Phase de filtrage :
        # On cherche juste les chemins valide par rapport au terme demandé
        candidats: List[PointeurFeuille] = []
        self._collecter_candidats(self.racine, predicat_mis_a_plat, 0, candidats, profondeur_cached)

        # Phase d'unification :
        # C'est ici qu'on valide les substitutions trouvées par la phase de filtrage
        resultats = []
        for pointeur in candidats:
            substitution = self._unifier_predicats(predicat, pointeur.predicat)
            if substitution is not None:
                resultats.append(ResultatRecherche(
                    substitution=substitution,
                    pointeurs=[pointeur.pointeur]
                ))
        
        return resultats
    
    # Filtrage ----------------------------------------------------
    
    def _collecter_candidats(self, noeud: NoeudArbreDeDiscrimination, sequence: List[str], index: int, candidats: List[PointeurFeuille], fn_profondeur) -> None:
        """
        Parcours de l'arbre pour collecter les candidats potentiellement unifiable.
        Filtre grossier en ignorant les contraintes d'unification qui seront vérifiées en phase d'unification.

        Args:
            noeud       (NoeudArbreDeDiscrimination): Noeud courant
            sequence    (List[str])                 : Séquence du terme mis à plat
            index       (int)                       : Index du parcours
            candidats   (List[PointeurFeuille])     : Listes des feuilles candidates à l'unification
        """
        # Si le parcours est fini :
        if index >= len(sequence):
            # On ajoute les feuilles aux candidats
            candidats.extend(noeud.pointeurs)
            return
        
        symbole_courant = sequence[index] # Récupération du symbole courant de la recherche

        # Cas prédicat : on cherche signe opposé au signe courant
        if symbole_courant in (SYMBOLE_PREDICAT_NEGATIF, SYMBOLE_PREDICAT_POSITIF):
            oppose = SYMBOLE_PREDICAT_NEGATIF if symbole_courant == SYMBOLE_PREDICAT_POSITIF else SYMBOLE_PREDICAT_POSITIF
            if oppose in noeud.enfants:
                self._collecter_candidats(noeud.enfants[oppose], sequence, index + 1, candidats, fn_profondeur)
            return
        
        # Cas 1 : les symboles sont identiques
        if symbole_courant in noeud.enfants and not symbole_courant.startswith(NORM_VAR_REQUETE):
            self._collecter_candidats(noeud.enfants[symbole_courant], sequence, index + 1, candidats, fn_profondeur)

        # Cas 2 : variable dans la requête
        if symbole_courant.startswith(NORM_VAR_REQUETE):
            for enfant in noeud.enfants.values():
                # On récupère les sous-terme :
                for dernier_noeud in self._collecter_sous_termes(enfant, 1):
                    # La variable peut s'unifier avec les sous-termes :
                    self._collecter_candidats(dernier_noeud, sequence, index + 1, candidats, fn_profondeur)
            return
        
        # Cas 3 : variable dans l'arbre
        profondeur = fn_profondeur(index)
        nouvel_index = index + profondeur
        for symbole, enfant in noeud.enfants.items():
            if symbole.startswith(NORM_VAR_ARBRE) and nouvel_index <= len(sequence):
                self._collecter_candidats(enfant, sequence, nouvel_index, candidats, fn_profondeur)

    # Unification ----------------------------------------------------

    def _unifier_predicats(self, predicat_recherche: Litteral, predicat_candidat: Litteral) -> Optional[Dict[str, NoeudTerme]]:
        """
        Surcouche de la fonction _unifier_termes pour les prédicats.
        On fait maintenant partager la substitution entre les termes du même prédicat.

        Args:
            predicat_recherche, predicat_candidat (Litteral)    :   Les prédicat à unifier.

        Returns:
            Optional[Dict[str, NoeudTerme]]                     :   La substitution si l'unification réussi, None sinon.
        """
        substitution: Dict[str, NoeudTerme] = {}
        
        for terme1, terme2 in zip(predicat_recherche.enfants, predicat_candidat.enfants):
            if not self._unifier_termes(terme1, terme2, substitution):
                return None
            
        return substitution
        

    def _unifier_termes(self, terme1: NoeudTerme, terme2: NoeudTerme, substitution: Dict[str, NoeudTerme]) -> bool:
        """
        Calcule le MGU de deux termes via Robinson (peut-etre qu'il faut directement utilisé l'algo de matheo, plus préférable ?)

        Args:
            terme1, terme2 (NoeudTerme)         :   Les termes à unifier.

        Returns:
            Optional[Dict[str, NoeudTerme]]     :   La substitution si l'unification réussi, None sinon.
        """
        pile: List[Tuple[NoeudTerme, NoeudTerme]] = [(terme1, terme2)]

        while pile:
            a, b = pile.pop()

            a = self._transitivite(a, substitution)
            b = self._transitivite(b, substitution)

            # Cas 1 : termes égaux 
            if self._termes_egaux(a, b):
                continue

            # Cas 2 : a est une variable
            if a.etiquette == ETIQUETTE_VAR:
                if self._apparait_dans(a.nom, b, substitution):
                    # Occur check
                    return False
                substitution[a.nom] = b

            # Cas 3 : b est une variable
            elif b.etiquette == ETIQUETTE_VAR:
                if self._apparait_dans(b.nom, a, substitution):
                    # Occur check
                    return False
                substitution[b.nom] = a

            # Cas 4 : même fonction ou constante et même arité
            elif a.nom == b.nom and len(a.enfants) == len(b.enfants):
                # On vérifie l'unification des arguments
                for ca, cb in zip(a.enfants, b.enfants):
                    pile.append((ca, cb))

            # Cas 5 : echec
            else:
                return False
            
        return True
    
    def _transitivite(self, terme: NoeudTerme, substitution: Dict[str, NoeudTerme]) -> NoeudTerme:
        """
        Récupère le dernier terme substitué d'une chaine de transitivité

        Args:
            terme           (NoeudTerme)            : Le premier terme de la chaine
            substitution    (Dict[str, NoeudTerme]) : La substitution parcourue

        Returns:
            NoeudTerme: Le dernier terme substitué de la chaine
        """
        chemin = []
        while terme.etiquette == ETIQUETTE_VAR and terme.nom in substitution:
            chemin.append(terme.nom)
            terme = substitution[terme.nom]
        for nom in chemin:
            substitution[nom] = terme
        return terme
    
    def _apparait_dans(self, nom_var: str, terme: NoeudTerme, substitution: Dict[str, NoeudTerme]) -> bool:
        """
        Occur check : vérifié si la variable 'nom_var' apparait dans 'terme'.

        Args:
            nom_var         (str)                   : La variable dont on vérifie la présence.
            terme           (NoeudTerme)            : Le terme pouvant contenir la variable.
            substitution    (Dict[str, NoeudTerme]) : La substitution.

        Returns:
            bool: True si occur check, False sinon.
        """
        terme = self._transitivite(terme, substitution)
        # Si variable :
        if terme.etiquette == ETIQUETTE_VAR: 
            # On vérifie le nom
            return terme.nom == nom_var
        
        # On regarde pour les enfants
        return any(self._apparait_dans(nom_var, enfant, substitution) for enfant in terme.enfants)
    
    def _termes_egaux(self, terme1: NoeudTerme, terme2: NoeudTerme) -> bool:
        """
        Vérifie l'égalité structurelle de deux termes

        Args:
            terme1, terme2 (NoeudTerme): Les termes à vérifier

        Returns:
            bool: True si égaux, False sinon.
        """
        # Si pas le meme nom ou meme type :
        if terme1.etiquette != terme2.etiquette or terme1.nom != terme2.nom:
            return False
        # Vérification dans les enfants :
        return all(self._termes_egaux(enfant1, enfant2) for enfant1, enfant2 in zip(terme1.enfants, terme2.enfants))

    # Autres fonctions internes ----------------------------------------------------
    
    def _mise_a_plat_predicat(self, predicat: Litteral, var_map: Dict[str, str], prefixe: str) -> List[str]:
        """
        Surcouche de la fonction _mise_a_plat_terme pour les prédicats.

        Args:
            predicat    (Litteral)      : Le prédicat à mettre à plat.
            var_map     (Dict[str, str]): Mapping de normalisation des variables.
            prefixe     (str)           : Préfixe pour les variables normalisées (* pour arbre, ? pour query).

        Returns:
            List[str]                   : La séquence correspondant au prédicat mis à plat.
        """
        
        # Initialisation de la séquence vide :
        resultat = []

        # Ajout du signe et du symbole du prédicat à la séquence :
        resultat.extend([SYMBOLE_PREDICAT_POSITIF if predicat.sign else SYMBOLE_PREDICAT_NEGATIF, predicat.predicat])

        self.arites[predicat.predicat] = predicat.arity

        # Mise à plat des termes du prédicat et ajout à la séquence :
        for terme in predicat.enfants:
            resultat.extend(self._mise_a_plat_terme(terme, var_map, prefixe))

        return resultat

    def _mise_a_plat_terme(self, terme: NoeudTerme, var_map: Dict[str, str], prefixe: str) -> List[str]:
        """
        Mise à plat d'un terme en une séquence de symboles en ordre préfixe.
        Les variables sont normalisées en *1, *2, etc.
        
        Pour f(X, g(Y)), retourne : ['f', '*1', 'g', '*2']
        
        Args:
            terme   (NoeudTerme)        :   Le terme à aplatir.
            var_map (Dict[str, str])    :   Mapping de normalisation des variables.
            prefixe (str)               :   Préfixe pour les variables normalisées.
        Returns:
            List[str]                   :   Séquence aplatie de symboles.
        """
        # Initialisation de la séquence résultat vide :
        resultat = []
        
        # Ajout du symbole du terme courant :
        if terme.etiquette == ETIQUETTE_VAR:
            # On map l'arité de la variable :
            if terme.nom not in self.arites:
                self.arites[terme.nom] = 0 # On met à 0
            # On normalise :
            if terme.nom not in var_map: # Nouvelle variable rencontrée
                var_map[terme.nom] = f"{prefixe}{len(var_map) + 1}"
            resultat.append(var_map[terme.nom])
        elif terme.etiquette == ETIQUETTE_CONS:
            # On map l'arité de la variable :
            if terme.nom not in self.arites:
                self.arites[terme.nom] = 0 # On met à 0
            # Constante, on ajoute le nom tel quel
            resultat.append(terme.nom)
        else:        
            # On map l'arité de la fonction
            if terme.nom not in self.arites:
                self.arites[terme.nom] = int(terme.etiquette) # L'arité est stockée dans l'étiquette
            # Fonction, on ajoute le nom tel quel :
            resultat.append(terme.nom)
            # Ajout des enfants :
            for enfant in terme.enfants:
                resultat.extend(self._mise_a_plat_terme(enfant, var_map, prefixe))
        
        return resultat
    
    
    def _collecter_sous_termes(self, noeud: NoeudArbreDeDiscrimination, obligations: int) -> List[NoeudArbreDeDiscrimination]:
        """
        Collecte les paires (séquence_sous_terme, noeud_de_continuation)
        correspondant aux sous-termes complets dont la racine est `noeud`

        Args:
            noeud       (NoeudArbreDeDiscrimination)            :   Noeud courant à explorer.
            obligations (int)                                   :   Sous-termes restants.
            
        Returns:
            List[NoeudArbreDeDiscrimination]                    :   Paire
        """
        arite = 0
        
        # Mise à jour du compteur :
        if noeud.symbole is not None:
            if noeud.symbole.startswith(NORM_VAR_ARBRE) or noeud.symbole.startswith(NORM_VAR_REQUETE):
                arite = 0
            else:
                arite = self.arites.get(noeud.symbole, 0)

            obligations = obligations - 1 + arite

        # Le sous-terme est complet :
        if obligations == 0:
            return [noeud]
        
        # Pas complet, on ajoute les enfants
        return [
            n 
            for enfant in noeud.enfants.values()
            for n in self._collecter_sous_termes(enfant, obligations)
        ]
        
    
    def _calculer_profondeur_depuis_index(self, index: int, sequence: List[str], fonction_profondeur=None) -> int:
        """
        Calcule la profondeur du sous-terme commençant à l'index donné.
        
        Args:
            index       (int)       : L'index de départ dans la séquence.
            sequence    (List[str]) : La séquence

        Returns:
            int : Le nombre de symboles formant le sous-terme.
        """
        if index >= len(sequence):
            return 0

        symbole = sequence[index]

        if symbole.startswith(NORM_VAR_ARBRE) or symbole.startswith(NORM_VAR_REQUETE):
            return 1
        
        arite = self.arites.get(symbole, 0)
        # Si arité = 0 (variable ou constante), la profondeur est 1
        if arite == 0:
            return 1
        
        fn = fonction_profondeur if fonction_profondeur is not None else \
            lambda i: self._calculer_profondeur_depuis_index(i, sequence)
        
        # Si arité > 0 (fonction), on compte 1 + profondeur de chaque argument
        profondeur = 1
        position_courante = index + 1
        
        for _ in range(arite):
            profondeur_arg = fn(position_courante)
            profondeur += profondeur_arg
            position_courante += profondeur_arg
        
        return profondeur
        

    
    def affichage_arbre(self, noeud: Optional[NoeudArbreDeDiscrimination] = None, niveau: int = 0, prefixe: str = "", est_dernier: bool = True, chemin: str = "") -> None:
        """
        ╔════════════════════════════════════════════════════════════════╗
        ║                                                                ║
        ║      Structure de la fonction générée par IA (ClaudeCode).     ║
        ║                                                                ║
        ╚════════════════════════════════════════════════════════════════╝

        Affiche l'arbre de discrimination de manière lisible dans la console.
        
        Args:
            noeud (Optional['NoeudArbreDeDiscrimination']) : Le noeud courant à afficher. 'None' pour commencer à la racine.
            niveau (int) : Niveau actuel dans l'arbre, utilisé pour l'indentation.
            prefixe (str) : Chaîne de préfixe pour formater la structure de l'arbre.
            est_dernier (bool) : Indique si le noeud courant est le dernier enfant de son parent.
            chemin (str) : Le chemin vers le noeud courant.
        """
        if noeud is None:
            # Commencer à la racine
            noeud = self.racine
            print("╔" + "═" * 61 + "╗")
            print("║" + " " * 19 + "ARBRE DE DISCRIMINATION" + " " * 19 + "║")
            print("╚" + "═" * 61 + "╝")
            print("\nRACINE")
            liste_enfants = list(noeud.enfants.values())
            for i, noeud_enfant in enumerate(liste_enfants):
                est_dernier_enfant = (i == len(liste_enfants) - 1)
                if noeud_enfant.symbole is not None:
                    self.affichage_arbre(noeud_enfant, niveau + 1, "", est_dernier_enfant, noeud_enfant.symbole)
            return
        
        # Déterminer les connecteurs pour l'affichage
        connecteur = "└── " if est_dernier else "├── "
        extension = "    " if est_dernier else "│   "

        # Afficher le noeud courant
        symbole_affiche = noeud.symbole
        
        if noeud.pointeurs:
            # Feuille avec pointeurs
            print(f"{prefixe}{connecteur}[{symbole_affiche}]")
            for i, pointeur in enumerate(noeud.pointeurs):
                est_dernier_pointeur = (i == len(noeud.pointeurs) - 1)
                connecteur_pointeur = "    └─→ " if est_dernier_pointeur else "    ├─→ "
                prefixe_pointeur = prefixe + extension if not est_dernier else prefixe + "    "
                print(f"{prefixe_pointeur}{connecteur_pointeur}{pointeur.pointeur}")
        else:
            # Noeud interne
            print(f"{prefixe}{connecteur}{symbole_affiche}")
        
        # Afficher les enfants
        liste_enfants = list(noeud.enfants.values())
        for i, noeud_enfant in enumerate(liste_enfants):
            est_dernier_enfant = (i == len(liste_enfants) - 1)
            chemin_enfant = f"{chemin}/{noeud_enfant.symbole}"
            self.affichage_arbre(noeud_enfant, niveau + 1, prefixe + extension, est_dernier_enfant, chemin_enfant)
 

# Exemple d'utilisation
if __name__ == "__main__":
    from Util.TermStore.terme import FabriqueDeTermes
    from Util.Litteral.Litteral import Litteral
 
    dt = ArbreDeDiscrimination()
 
    terme1 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("Y"),
        FabriqueDeTermes.creer_var("Z")
    ])
    terme2 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("Y"),
        FabriqueDeTermes.creer_cons("a")
    ])
    terme3 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_var("X"),
            FabriqueDeTermes.creer_cons("a")
        ]),
        FabriqueDeTermes.creer_var("Y")
    ])
    terme4 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_var("Z"),
            FabriqueDeTermes.creer_cons("a")
        ]),
        FabriqueDeTermes.creer_var("Y")
    ])

    predicat1 = Litteral(predicat="P", enfants=[terme1, terme3], sign = True)
    predicat2 = Litteral(predicat="P", enfants=[terme2, terme4], sign = False)
    predicat3 = Litteral(predicat="P", enfants=[terme1, terme4], sign = True)
 
    dt.inserer(predicat1, f"predicat1 : {SYMBOLE_PREDICAT_POSITIF}P(f(Y, Z), f(g(X, a), Y))")
    dt.inserer(predicat2, f"predicat2 : {SYMBOLE_PREDICAT_NEGATIF}P(f(Y, a), f(g(Z, a), Y))")
    dt.inserer(predicat3, f"predicat3 : {SYMBOLE_PREDICAT_POSITIF}P(f(Y, Z), f(g(Z, a), Y))")
   
    
    dt.affichage_arbre()

    terme5 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_var("X"),
        FabriqueDeTermes.creer_var("X")
    ])
    
    terme6 = FabriqueDeTermes.creer_fonc("f", 2, [
        FabriqueDeTermes.creer_fonc("g", 2, [
            FabriqueDeTermes.creer_cons("a"),
            FabriqueDeTermes.creer_var("X")
        ]),
        FabriqueDeTermes.creer_var("Y")
    ])

    predicat_recherche = Litteral(predicat="P", enfants=[terme5, terme6], sign = False)
 
    print(f"\nRecherche de termes unifiables avec : {SYMBOLE_PREDICAT_NEGATIF}P(f(X, X), f(g(a, X), Y))")
    resultats = dt.rechercher(predicat_recherche)
 
    if not resultats:
        print("  Aucun prédicat unifiable trouvé.")
    else:
        for i, res in enumerate(resultats, 1):
            print(f"\n  Résultat {i} :")
            print(f"    Pointeurs    : {res.pointeurs}")
            if res.substitution:
                print(f"    Substitution :")
                for var, terme_subst in res.substitution.items():
                    print(f"      {var}  →  {terme_subst}")
            else:
                print(f"    Substitution : ∅  (termes identiques)")