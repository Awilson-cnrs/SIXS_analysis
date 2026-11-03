# SIXS Analysis

Outils d'analyse des données de diffusion des rayons X en petite angle (SIXS/SAXS) et de diffraction (XRD/XAS) pour les expériences de catalyse in situ.

Ce projet fournit des notebooks Jupyter pour lire, traiter et visualiser les fichiers NeXus/HDF5 générés par les expériences SIXS au Soleil.

---

## Structure du projet

```
SIXS_analysis/
├── notebooks/           # Notebooks Jupyter pour l'analyse
│   ├── xas_sample*.ipynb    # Analyse XAS (absorption)
│   ├── xrd_sample*.ipynb    # Analyse XRD (diffraction)
│   └── plot_*.ipynb         # Scripts de visualisation
├── sixs_tools/          # Package Python avec les outils de lecture
│   ├── read_nxs5.py     # Lecteur de fichiers NeXus HDF5
│   ├── bin_util.py      # Outils de binning et traitement d'image
│   └── utilities.py     # Fonctions utilitaires diverses
├── data/                # Données locales (ignoré par git)
├── environment.yml      # Dépendances conda
└── main.py              # Point d'entrée (script de test)
```

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-repo>
cd SIXS_analysis
```

### 2. Configurer l'environnement conda

Ce projet utilise un environnement conda partagé nommé `datascience`.

```bash
# Créer l'environnement à partir du fichier environment.yml
conda env create -f environment.yml

# Activer l'environnement
conda activate datascience
```

Si l'environnement `datascience` existe déjà sur votre machine, mettez-le à jour :

```bash
conda env update -f environment.yml
```

### 3. Installer le kernel Jupyter (une seule fois)

```bash
conda activate datascience
python -m ipykernel install --user --name datascience --display-name "Python (datascience)"
```

## Utilisation

### Lancer les notebooks

1. Activez l'environnement conda :
   ```bash
   conda activate datascience
   ```

2. Lancez Jupyter Lab :
   ```bash
   jupyter lab
   ```

3. Ouvrez un notebook dans le dossier `notebooks/` et sélectionnez le kernel **Python (datascience)**.

### Importer les outils dans un notebook

```python
from sixs_tools import read_nxs5 as rn5
from sixs_tools import bin_util as bu3
from sixs_tools import utilities3 as ut3
```

## Dépendances

Les dépendances sont gérées par `environment.yml`. Pour ajouter un paquet :

```bash
conda activate datascience
conda install <paquet>
conda env export -n datascience > environment.yml
```

## Licence

Ce projet est issu d'un fork de [AndreaResta/sixs_readnxs](https://codeberg.org/AndreaResta/sixs_readnxs).
