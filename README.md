# Rapport_Rejet - Rapports de Coherence EHCVM

Releve des Incoherences dans le questionnaire menage.

Interface web pour consulter et telecharger les rapports de coherence de l'enquete EHCVM.

## Acces

L'interface est accessible a l'adresse : https://mojoop.github.io/Rapport_Rejet/

## Structure

```
Rapport_Web/
├── index.html          # Interface web principale
├── files.json          # Index des fichiers disponibles
├── sync_rapports.py    # Script de synchronisation
├── rapports/           # Dossier contenant les rapports Word
│   └── dd_mm_yyyy/     # Dossiers par date
│       └── SUPERVISEUR/# Dossiers par superviseur
│           └── *.docx  # Rapports Word
└── README.md
```

## Mise a jour des rapports

1. Generer les rapports avec le script principal :
   ```bash
   python generer_rapports.py --par-grappe
   ```

2. Synchroniser vers le dossier web :
   ```bash
   cd Rapport_Web
   python sync_rapports.py
   ```

3. Pousser vers GitHub :
   ```bash
   git add .
   git commit -m "Mise a jour des rapports du $(date +%d_%m_%Y)"
   git push
   ```

## Fonctionnalites

- Navigation par date et superviseur
- Recherche de rapports
- Selection multiple
- Telechargement direct des fichiers Word
