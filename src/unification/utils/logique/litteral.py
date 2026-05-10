from typing import Optional, List
import random

from .terme import NoeudTerme, GenerateurDeTermesAleatoires, FabriqueDeTermes


"""
le code a entierement été fait par moi, l'IA a aidé pour les docstrings, et comment parser

Proposition pour littéraux : 
Predicat (nom)
arité
[termes]
signe

Litteral("P", [t1, t2], True)

"""

class Litteral:
    """
    Représente un littéral comme un arbre.
    La racine est le prédicat (avec son signe), les enfants sont les termes.
    
    Structure :
        +P (arity = 2)
        ├── t1
        └── t2
    """
    def __init__(self, predicat: str, enfants: List[NoeudTerme], sign: bool = True):
        self.predicat = predicat
        self.enfants = enfants  # les termes sont les enfants du nœud
        self.sign = sign
        self.arity = len(enfants)

    @staticmethod
    def _split_args(args_str: str) -> List[str]:
        """Découpe les arguments d'un terme/littéral en tenant compte de l'imbrication."""
        args = []
        courant = []
        profondeur = 0

        for char in args_str:
            if char == ',' and profondeur == 0:
                arg = "".join(courant).strip()
                if arg:
                    args.append(arg)
                courant = []
                continue

            if char == '(':
                profondeur += 1
            elif char == ')':
                profondeur -= 1
                if profondeur < 0:
                    raise ValueError("Parentheses non equilibrees dans la chaine.")

            courant.append(char)

        if profondeur != 0:
            raise ValueError("Parentheses non equilibrees dans la chaine.")

        dernier = "".join(courant).strip()
        if dernier:
            args.append(dernier)

        return args

    @staticmethod
    def _parse_terme(terme_str: str) -> NoeudTerme:
        """Transforme une chaine en NoeudTerme (const, var ou fonction)."""
        terme_str = terme_str.strip()
        if not terme_str:
            raise ValueError("Terme vide.")

        if '(' not in terme_str:
            if terme_str[0].isupper():
                return FabriqueDeTermes.creer_var(terme_str)
            return FabriqueDeTermes.creer_cons(terme_str)

        if not terme_str.endswith(')'):
            raise ValueError(f"Terme mal forme: {terme_str}")

        idx = terme_str.find('(')
        nom_fonc = terme_str[:idx].strip()
        contenu = terme_str[idx + 1:-1].strip()
        if not nom_fonc:
            raise ValueError(f"Fonction sans nom: {terme_str}")

        enfants = []
        if contenu:
            enfants = [Litteral._parse_terme(arg) for arg in Litteral._split_args(contenu)]

        return FabriqueDeTermes.creer_fonc(nom_fonc, len(enfants), enfants)

    @staticmethod
    def from_string(litteral_str: str) -> 'Litteral':
        """
        Cree un objet Litteral a partir d'une chaine.

        Exemples:
            - P(f(x,y), g(a))
            - ¬Q(X)
            - R(a)
        """
        s = litteral_str.strip()
        if not s:
            raise ValueError("Litteral vide.")

        sign = True
        if s[0] == '¬':
            sign = False
            s = s[1:].strip()

        if '(' not in s:
            predicat = s
            enfants = []
            return Litteral(predicat, enfants, sign)

        if not s.endswith(')'):
            raise ValueError(f"Litteral mal forme: {litteral_str}")

        idx = s.find('(')
        predicat = s[:idx].strip()
        if not predicat:
            raise ValueError(f"Predicat invalide: {litteral_str}")

        contenu = s[idx + 1:-1].strip()
        enfants = []
        if contenu:
            enfants = [Litteral._parse_terme(arg) for arg in Litteral._split_args(contenu)]

        return Litteral(predicat, enfants, sign)

    def __repr__(self):
        """
        Représente un littéral sous la forme compacte : +P(t1, t2)
        """
        terms_str = ", ".join(repr(t) for t in self.enfants)
        signe = "" if self.sign else "¬"
        return f"{signe}{self.predicat}({terms_str})"

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Litteral):
            return False
        return (
            self.predicat == obj.predicat
            and self.sign == obj.sign
            and self.enfants == obj.enfants
        )

    def __hash__(self) -> int:
        return hash((self.predicat, self.sign, tuple(self.enfants)))
    
    def afficher_arbre(self, indent: str = "", est_dernier: bool = True) -> str:
        """
        (aidé par l'IA)
        Représente le littéral sous forme d'arbre avec ses termes comme enfants.
        Affiche récursivement la structure complète du littéral.
        
        Args:
            indent (str): Indentation courante pour l'affichage (utilisé en interne).
            est_dernier (bool): Indique si c'est le dernier enfant (utilisé en interne).
        
        Returns:
            str: Représentation arborescente du littéral.
        
        Example:
            >>> X = FabriqueDeTermes.creer_var("X")
            >>> a = FabriqueDeTermes.creer_cons("a")
            >>> f_X_a = FabriqueDeTermes.creer_fonc("f", 2, [X, a])
            >>> Y = FabriqueDeTermes.creer_var("Y")
            >>> lit = Litteral("P", [f_X_a, Y], True)
            >>> print(lit.afficher_arbre())
            +P (arity = 2)
            ├── f (arity = 2)
            │   ├── X (var)
            │   └── a (const)
            └── Y (var)
        """
        signe = " " if self.sign else "¬"
        lines = [f"{indent}{signe}{self.predicat} (arity = {self.arity})"]
        
        for i, enfant in enumerate(self.enfants):
            est_dernier_enfant = (i == len(self.enfants) - 1)
            branche = "└── " if est_dernier_enfant else "├── "
            sous_indent = "    " if est_dernier_enfant else "│   "
            
            # Afficher le terme (qui est lui-même un arbre)
            lines.append(self._afficher_terme(enfant, indent + branche, indent + sous_indent))
        
        return "\n".join(lines)
    
    def _afficher_terme(self, terme: NoeudTerme, prefixe: str, indent: str) -> str:
        """
        Affiche un terme récursivement sous forme d'arbre.
        """
        # Racine du terme
        if terme.etiquette in ["const", "var"]:
            return f"{prefixe}{terme.nom} ({terme.etiquette})"
        else:
            lines = [f"{prefixe}{terme.nom} (arity = {terme.etiquette})"]
            for i, enfant in enumerate(terme.enfants):
                est_dernier = (i == len(terme.enfants) - 1)
                branche = "└── " if est_dernier else "├── "
                sous_indent = "    " if est_dernier else "│   "
                lines.append(self._afficher_terme(enfant, indent + branche, indent + sous_indent))
            return "\n".join(lines)
        
class GenerateurLitteralAleatoire:
    """
    Génère des littéraux aléatoires avec des arités cohérentes.
    
    IMPORTANT: Utiliser la même instance du générateur pour conserver les arités
    des prédicats. Chaque instance génère ses propres arités aléatoires à
    l'initialisation. Si vous créez plusieurs instances, les prédicats auront
    des arités différentes entre les instances.
    
    Attributes:
        nom_predicats (list[str]): Liste des noms de prédicats disponibles (ex: ['P', 'Q', 'R']).
        ariteMax (int): Arité maximale autorisée pour les prédicats.
        profondeurMax (int): Profondeur maximale des termes générés.
        dict_arites (dict[str, int]): Dictionnaire associant chaque prédicat à son arité fixe.
        generateur_termes (GenerateurDeTermesAleatoires): Générateur de termes aléatoires avec profondeur fixe.
    """
    
    def __init__(self, nom_predicats: list[str], ariteMax: int, profondeurMax: int):
        """
        Initialise le générateur de littéraux avec des arités fixes pour chaque prédicat.
        
        Args:
            nom_predicats (list[str]): Liste des noms de prédicats (ex: ['P', 'Q', 'R']).
            ariteMax (int): Arité maximale pour les prédicats (arité choisie entre 1 et ariteMax).
            profondeurMax (int): Profondeur maximale des termes dans les littéraux.
        
        Example:
            >>> gen = GenerateurLitteral(['P', 'Q', 'R'], ariteMax=3, profondeurMax=2)
            >>> # Tous les littéraux P générés par 'gen' auront la même arité
        """
        self.nom_predicats = nom_predicats
        self.ariteMax = ariteMax
        self.profondeurMax = profondeurMax
        self.dict_arites = self._creer_dict_arites()
        self.generateur_termes = GenerateurDeTermesAleatoires(profondeur_max=self.profondeurMax)
        
    def _creer_dict_arites(self) -> dict[str, int]:
        """
        Crée un dictionnaire associant chaque prédicat à une arité aléatoire.
        L'arité est choisie aléatoirement entre 1 et ariteMax.
        Cela garantit que chaque prédicat aura toujours la même arité.
        
        Returns:
            dict[str, int]: Dictionnaire {nom_predicat: arite}
        """
        return {predicat: random.randint(1, self.ariteMax) for predicat in self.nom_predicats}

    def _generer_litteral_aleatoire(self, predicat: str) -> Litteral:
        """
        Génère un littéral aléatoire pour un prédicat donné (fonction interne).
        
        L'arité du prédicat est déterminée par le dictionnaire d'arités.
        Les termes sont générés aléatoirement avec la profondeur maximale spécifiée.
        Le signe du littéral (positif/négatif) est choisi aléatoirement.
        
        Args:
            predicat (str): Le nom du prédicat (doit être dans nom_predicats).
        
        Returns:
            Litteral: Un littéral avec le prédicat, des termes aléatoires et un signe aléatoire.
        """
        termes = []
        arite = self.dict_arites[predicat]
        for i in range(arite):
            termes.append(self.generateur_termes.generer_terme_aleatoire())
        sign = random.choice([True, False])
        return Litteral(predicat, termes, sign)
    
    def generer_litteraux(self, n: int) -> List[Litteral]:
        """
        Génère n littéraux aléatoires.
        
        Pour chaque littéral généré, un prédicat est choisi aléatoirement parmi
        les prédicats disponibles, puis un littéral est créé avec des termes aléatoires
        et un signe aléatoire.
        
        Args:
            n (int): Nombre de littéraux à générer.
        
        Returns:
            List[Litteral]: Liste de n littéraux générés aléatoirement.
        
        Example:
            >>> gen = GenerateurLitteralAleatoire(['P', 'Q', 'R'], ariteMax=3, profondeurMax=2)
            >>> litteraux = gen.generer_litteraux(5)
            >>> for lit in litteraux:
            ...     print(lit)
            # Exemple: P(X, f(a)), ¬Q(b), R(Y, Z, a), ...
        """
        litteraux = []
        for i in range(n):
            predicat = random.choice(self.nom_predicats)
            litteral = self._generer_litteral_aleatoire(predicat)
            litteraux.append(litteral)
        return litteraux
    
# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le générateur de litteraux aléatoires
    generateur = GenerateurLitteralAleatoire(['P', 'Q', 'R'], profondeurMax=3, ariteMax=3)

    # Générer autant de prédicats aléatoires que souhaité
    litteraux_aleatoires = generateur.generer_litteraux(10)

    # Afficher les littéraux générés
    print("Littéraux générés :")
    for litteral in litteraux_aleatoires:
        print(litteral)