# -*- coding: utf-8 -*-
"""
Script de synchronisation des rapports vers le dossier web
Genere le fichier files.json et copie les rapports Word
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

# Chemin source des rapports
SOURCE_DIR = r"d:\Cq\gtCq\Dataout\Rapport_de_coherence_men"

# Chemin du dossier web (ce dossier)
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

# Dossier destination pour les rapports dans le projet web
RAPPORTS_DIR = os.path.join(WEB_DIR, "rapports")


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


def generer_files_json(structure, output_path):
    """Genere le fichier files.json"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)
    print(f"[OK] files.json genere avec {sum(len(s) for d in structure.values() for s in d.values())} fichiers")


def main():
    """Fonction principale"""
    print("=" * 60)
    print("SYNCHRONISATION DES RAPPORTS VERS LE WEB")
    print("=" * 60)
    print()

    # Scanner les rapports
    print(f"[*] Scan du dossier: {SOURCE_DIR}")
    structure = scanner_rapports(SOURCE_DIR)

    if not structure:
        print("[!] Aucun rapport trouve")
        return

    # Afficher le resume
    total_dates = len(structure)
    total_supervisors = sum(len(s) for s in structure.values())
    total_files = sum(len(f) for d in structure.values() for f in d.values())

    print(f"    Dates trouvees: {total_dates}")
    print(f"    Superviseurs: {total_supervisors}")
    print(f"    Fichiers: {total_files}")
    print()

    # Copier les rapports
    print(f"[*] Copie des rapports vers: {RAPPORTS_DIR}")
    copies, _ = copier_rapports(SOURCE_DIR, RAPPORTS_DIR, structure)
    print(f"    {copies} fichier(s) copie(s)")
    print()

    # Generer files.json
    print(f"[*] Generation de files.json")
    json_path = os.path.join(WEB_DIR, "files.json")
    generer_files_json(structure, json_path)

    print()
    print("=" * 60)
    print("[OK] Synchronisation terminee!")
    print()
    print("    Prochaines etapes:")
    print("    1. cd Rapport_Web")
    print("    2. git add .")
    print("    3. git commit -m 'Mise a jour des rapports'")
    print("    4. git push")
    print("=" * 60)


if __name__ == "__main__":
    main()
