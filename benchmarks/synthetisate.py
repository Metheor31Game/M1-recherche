import csv
import os
from collections import defaultdict

# Aidé de l'IA

def synthetiser_csv(fichier_entree, fichier_sortie):
    if not os.path.exists(fichier_entree):
        print(f"Le fichier {fichier_entree} n'existe pas. Ignoré.")
        return

    # Dictionnaire pour regrouper les lignes par configuration
    groupes = defaultdict(list)

    # 1. LECTURE ET REGROUPEMENT DES DONNÉES BRUTES
    with open(fichier_entree, mode='r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            # Notre clé unique pour grouper les 10 itérations
            cle = (row['Jeu'], row['Algo'], row['Structure'], row['TouteUnif'])
            
            # Extraction des données numériques
            tps_pre = float(row['Temps_Pretraitement'])
            tps_tot = float(row['Temps_Total'])
            tps_unif = tps_tot - tps_pre
            ram = float(row['RAM_Pic_Mo'])
            cpu = float(row['CPU_Percent'])

            # Ajout aux mesures du groupe
            groupes[cle].append({
                'tps_pre': tps_pre,
                'tps_unif': tps_unif,
                'tps_tot': tps_tot,
                'ram': ram,
                'cpu': cpu,
            })

    # 2. CALCUL DES MOYENNES ET ÉCRITURE
    with open(fichier_sortie, mode='w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        
        # Nouvel en-tête avec les colonnes demandées (+ les unifications)
        writer.writerow([
            "Jeu", "Algo", "Structure", "TouteUnif",
            "Temps_Pretraitement_Moyen(s)", "Temps_Unification_Moyen(s)", 
            "Temps_Total_Moyen(s)", "RAM_Pic_Moyen(Mo)", "CPU_Moyen(%)"
        ])

        for cle, mesures in groupes.items():
            nb_mesures = len(mesures)
            
            # Calcul des moyennes simples
            moy_tps_pre = sum(m['tps_pre'] for m in mesures) / nb_mesures
            moy_tps_unif = sum(m['tps_unif'] for m in mesures) / nb_mesures
            moy_tps_tot = sum(m['tps_tot'] for m in mesures) / nb_mesures
            moy_ram = sum(m['ram'] for m in mesures) / nb_mesures
            moy_cpu = sum(m['cpu'] for m in mesures) / nb_mesures
            # Écriture de la ligne consolidée
            writer.writerow([
                cle[0], cle[1], cle[2], cle[3], # Jeu, Algo, Structure, TouteUnif
                round(moy_tps_pre, 6),
                round(moy_tps_unif, 6),
                round(moy_tps_tot, 6),
                round(moy_ram, 2),
                round(moy_cpu, 1),
            ])
            
    print(f"Fichier synthétisé généré : {fichier_sortie} (à partir de {len(groupes)} configurations)")


if __name__ == "__main__":
    fichiers_a_traiter = ["brut_arbre.csv", "brut_robinson.csv", "brut_mm.csv"]
    
    for brut in fichiers_a_traiter:
        synthese = brut.replace("brut_", "synthese_")
        synthetiser_csv(brut, synthese)
