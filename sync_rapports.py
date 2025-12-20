# -*- coding: utf-8 -*-
"""
Script de synchronisation des rapports vers le dossier web
Genere les fichiers files.json et files_issues.json et copie les rapports Word
"""

import os
import json
import shutil
from datetime import datetime
import sys

# Forcer l'encodage UTF-8 pour la console Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Chemin du dossier web (ce dossier)
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration des deux types de rapports
RAPPORTS_CONFIG = {
    'coherence': {
        'source_dir': r"d:\Cq\gtCq\Dataout\Rapport_de_coherence_men",
        'dest_dir': os.path.join(WEB_DIR, "rapports"),
        'json_file': "files.json",
        'label': "Rapports de Coherence"
    },
    'issues': {
        'source_dir': r"d:\Cq\gtCq\Dataout\Rapport_Issues",
        'dest_dir': os.path.join(WEB_DIR, "rapports_issues"),
        'json_file': "files_issues.json",
        'label': "Rapports Issues (Programme de Rejet)"
    }
}


# ============================================================================
# FONCTIONS
# ============================================================================

def scanner_rapports(source_dir):
    """Scanne le dossier source et retourne la structure des fichiers"""
    structure = {}

    if not os.path.exists(source_dir):
        print(f"[ERREUR] Le dossier source n'existe pas: {source_dir}")
        return structure

    # Parcourir les dossiers de date (format: dd_mm_yyyy)
    for date_folder in os.listdir(source_dir):
        date_path = os.path.join(source_dir, date_folder)

        # Verifier que c'est un dossier de date (format dd_mm_yyyy)
        if not os.path.isdir(date_path):
            continue

        # Verifier le format de date
        parts = date_folder.split('_')
        if len(parts) != 3:
            continue

        try:
            # Valider que c'est une date valide
            int(parts[0])  # jour
            int(parts[1])  # mois
            int(parts[2])  # annee
        except ValueError:
            continue

        structure[date_folder] = {}

        # Parcourir les dossiers de superviseurs
        for supervisor_folder in os.listdir(date_path):
            supervisor_path = os.path.join(date_path, supervisor_folder)

            if not os.path.isdir(supervisor_path):
                continue

            files_list = []

            # Parcourir les fichiers Word
            for filename in os.listdir(supervisor_path):
                if filename.endswith('.docx') and not filename.startswith('~'):
                    file_path = os.path.join(supervisor_path, filename)
                    file_size = os.path.getsize(file_path)

                    files_list.append({
                        "name": filename,
                        "path": f"{date_folder}/{supervisor_folder}/{filename}",
                        "size": file_size
                    })

            if files_list:
                structure[date_folder][supervisor_folder] = files_list

    return structure


def copier_rapports(source_dir, dest_dir, structure):
    """Copie les rapports vers le dossier de destination"""

    # Creer le dossier de destination s'il n'existe pas
    os.makedirs(dest_dir, exist_ok=True)

    total_copies = 0
    total_files = 0

    for date_folder, supervisors in structure.items():
        for supervisor, files in supervisors.items():
            total_files += len(files)

            # Creer le dossier de destination
            dest_path = os.path.join(dest_dir, date_folder, supervisor)
            os.makedirs(dest_path, exist_ok=True)

            for file_info in files:
                src_file = os.path.join(source_dir, file_info['path'])
                dst_file = os.path.join(dest_dir, file_info['path'])

                # Copier seulement si le fichier source est plus recent ou n'existe pas
                if not os.path.exists(dst_file) or \
                   os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                    shutil.copy2(src_file, dst_file)
                    total_copies += 1
                    print(f"    [COPIE] {file_info['path']}")

    return total_copies, total_files


def generer_files_json(structure, output_path, label):
    """Genere le fichier JSON d'index"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    nb_fichiers = sum(len(s) for d in structure.values() for s in d.values())
    print(f"[OK] {os.path.basename(output_path)} genere avec {nb_fichiers} fichiers")


def sync_rapport_type(report_type):
    """Synchronise un type de rapport specifique"""
    config = RAPPORTS_CONFIG[report_type]

    print()
    print("-" * 60)
    print(f"  {config['label']}")
    print("-" * 60)

    # Scanner les rapports
    print(f"[*] Scan du dossier: {config['source_dir']}")
    structure = scanner_rapports(config['source_dir'])

    if not structure:
        print("[!] Aucun rapport trouve")
        return 0

    # Afficher le resume
    total_dates = len(structure)
    total_supervisors = sum(len(s) for s in structure.values())
    total_files = sum(len(f) for d in structure.values() for f in d.values())

    print(f"    Dates trouvees: {total_dates}")
    print(f"    Superviseurs: {total_supervisors}")
    print(f"    Fichiers: {total_files}")
    print()

    # Copier les rapports
    print(f"[*] Copie des rapports vers: {config['dest_dir']}")
    copies, _ = copier_rapports(config['source_dir'], config['dest_dir'], structure)
    print(f"    {copies} fichier(s) copie(s)")
    print()

    # Generer le fichier JSON
    print(f"[*] Generation de {config['json_file']}")
    json_path = os.path.join(WEB_DIR, config['json_file'])
    generer_files_json(structure, json_path, config['label'])

    return total_files


def main():
    """Fonction principale"""
    print("=" * 60)
    print("SYNCHRONISATION DES RAPPORTS VERS LE WEB")
    print("=" * 60)

    total_all = 0

    # Synchroniser les deux types de rapports
    for report_type in RAPPORTS_CONFIG.keys():
        total_all += sync_rapport_type(report_type)

    print()
    print("=" * 60)
    print(f"[OK] Synchronisation terminee! ({total_all} fichiers au total)")
    print()
    print("    Prochaines etapes:")
    print("    1. cd Rapport_Web")
    print("    2. git add .")
    print("    3. git commit -m 'Mise a jour des rapports'")
    print("    4. git push")
    print("=" * 60)


if __name__ == "__main__":
    # Permettre de synchroniser un seul type si specifie en argument
    if len(sys.argv) > 1:
        report_type = sys.argv[1]
        if report_type in RAPPORTS_CONFIG:
            print("=" * 60)
            print(f"SYNCHRONISATION: {RAPPORTS_CONFIG[report_type]['label']}")
            print("=" * 60)
            sync_rapport_type(report_type)
        else:
            print(f"Type de rapport inconnu: {report_type}")
            print(f"Types valides: {', '.join(RAPPORTS_CONFIG.keys())}")
    else:
        main()
