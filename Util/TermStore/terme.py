import random
from typing import Union, List, Optional

PROFONDEUR_MAX_PAR_DEFAUT = 3
ARITE_MAX_PAR_DEFAUT = 3
ETIQUETTE_CONS = "cons"
ETIQUETTE_VAR = "var"
DOMAINE_CONS = ['a', 'b', 'c', 'd', 'e']
DOMAINE_VAR = ['U', 'V', 'W','X', 'Y', 'Z']
DOMAINE_FONC = ['f', 'g', 'h', 'i', 'j', 'k', 'l']
ARITES = {
    'f': random.randint(1, ARITE_MAX_PAR_DEFAUT),
    'g': random.randint(1, ARITE_MAX_PAR_DEFAUT),
    'h': random.randint(1, ARITE_MAX_PAR_DEFAUT),
    'i': random.randint(1, ARITE_MAX_PAR_DEFAUT),
    'j': random.randint(1, ARITE_MAX_PAR_DEFAUT),
    'k': random.randint(1, ARITE_MAX_PAR_DEFAUT),
    'l': random.randint(1, ARITE_MAX_PAR_DEFAUT),
}

class NoeudTerme:
    """
    Classe représentant un noeud de terme.
    Peut représenter une constante, une variable ou une fonction.

    Attributes:
        nom (str): Le nom du terme (ex : "a", "X" ou "f").
        etiquette (Union[str, int]): Etiquette pour identifier le type du terme, ou l'arité dans le cas d'une fonction ("cons", "var", ou 3 pour une fonction à 3 arguments).
        enfants (Optional[List['NoeudTerme']]): Liste des NoeudTerme enfants pour les fonctions.
    """
    def __init__(self, nom: str, etiquette: Union[str, int], enfants: Optional[List['NoeudTerme']] = None):
        self.nom = nom # Nom du terme (du symbole)
        self.etiquette = etiquette # Etiquette du noeud ('cons', 'var' ou arité pour fonction)
        self.enfants = enfants if enfants is not None else [] # Enfants du noeud (vide pour constantes et variables)

    def __repr__(self) -> str:
        if self.etiquette in [ETIQUETTE_CONS, ETIQUETTE_VAR]:
            # Pour les constantes et variables on affiche juste le nom du symbole
            return f"{self.nom}"
        else:
            # Pour les fonctions on affiche le symbole puis les enfants entre parenthèses 
            # pour recréer la représentation d'une fonction
            representation_enfants = ", ".join(repr(enfant) for enfant in self.enfants)
            return f"{self.nom}({representation_enfants})"
        
        
class FabriqueDeTermes:
    """
    Classe utilitaire pour créer des termes.
    """
    @staticmethod
    def creer_cons(nom: str) -> NoeudTerme:
        return NoeudTerme(nom=nom, etiquette=ETIQUETTE_CONS)
     
    @staticmethod
    def creer_var(nom: str) -> NoeudTerme:
        return NoeudTerme(nom=nom, etiquette=ETIQUETTE_VAR)
    
    @staticmethod
    def creer_fonc(nom: str, arite: int, enfants: list) -> NoeudTerme:
        return NoeudTerme(nom=nom, etiquette=arite, enfants=enfants)
    
class GenerateurDeTermesAleatoires:
    """
    Classe générant des termes aléatoires.

    Attributes:
        profondeur_max (int): Profondeur maximale du terme généré (par défaut 3).
        arite_max (int): Arité maximale des fonctions générées (par défaut 3).
    """
    def __init__(self, profondeur_max: int = PROFONDEUR_MAX_PAR_DEFAUT, arite_max: int = ARITE_MAX_PAR_DEFAUT):
        self.profondeur_max = profondeur_max
        self.arite_max = arite_max
        self.consts = DOMAINE_CONS
        self.vars = DOMAINE_VAR
        self.foncs = DOMAINE_FONC

    def generer_terme_aleatoire(self, profondeur_courante: int = 0) -> NoeudTerme:
        """
        Génère un terme aléatoire selon la profondeur courante du terme en train d'être généré.

        Args:
            profondeur_courante (int, optional): Profondeur courante du terme. 0 par défaut.

        Returns:
            NoeudTerme: Le terme généré.
        """
        if profondeur_courante >= self.profondeur_max:
            # Si on est à la profondeur max, on ne peut générer qu'une constante ou une variable
            return random.choice([
                self._generer_cons(profondeur_courante),
                self._generer_var(profondeur_courante)
            ])
        else:
            # Sinon, on peut aussi générer une fonction
            choices = [
                self._generer_cons,
                self._generer_var,
                self._generer_fonc
            ]
            poids = [0.3, 0.3, 0.4] # Poids pour favoriser légérement la génération de fonction   
            generateur_choisi = random.choices(choices, weights=poids)[0]
            return generateur_choisi(profondeur_courante)
        
    def _generer_cons(self, _:int) -> NoeudTerme:
        return FabriqueDeTermes.creer_cons(random.choice(self.consts))

    def _generer_var(self, _:int) -> NoeudTerme:
        return FabriqueDeTermes.creer_var(random.choice(self.vars))

    def _generer_fonc(self, profondeur_courante: int) -> NoeudTerme:
        nom = random.choice(self.foncs)
        arite = ARITES.get(nom)
        if arite is None:
            arite = 1
        enfants = [self.generer_terme_aleatoire(profondeur_courante + 1) for _ in range(arite)]
        return FabriqueDeTermes.creer_fonc(nom, arite, enfants)
    
    def generer_termes(self, n: int) -> List[NoeudTerme]:
        """
        Génère 'n' termes de façon aléatoire et les renvoie dans une liste.

        Args:
            n (int): Nombre de termes à générer.

        Returns:
            List[NoeudTerme]: Liste des termes générés.
        """
        return [self.generer_terme_aleatoire() for _ in range(n)]

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le générateur de termes aléatoires
    generateur = GenerateurDeTermesAleatoires(profondeur_max=3, arite_max=3)

    # Générer autant de termes aléatoires que souhaité
    termes_aleatoires = generateur.generer_termes(10)

    # Afficher les termes générés
    print("Termes générés :")
    for terme in termes_aleatoires:
        print(terme)