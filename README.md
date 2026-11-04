# SIXS Analysis

Tools for analyzing X-ray absorption (XAS) and X-ray diffraction (XRD) data from surface diffraction experiments at the SOLEIL synchrotron.

This project provides Jupyter notebooks to read, process, and visualize NeXus/HDF5 files generated at SOLEIL beamlines.

---

## Project structure

```
SIXS_analysis/
├── notebooks/
│   ├── xas/               # XAS (absorption) analysis notebooks
│   │   ├── xas_sample1.ipynb
│   │   ├── xas_sample2.ipynb
│   │   ├── xas_sample3.ipynb
│   │   ├── xas_sample4.ipynb
│   │   ├── xas_sample8.ipynb
│   │   └── plot_xas_v1.ipynb
│   └── xrd/               # XRD (diffraction) analysis notebooks
│       ├── xrd_sample2.ipynb
│       ├── xrd_sample3.ipynb
│       ├── xrd_sample4.ipynb
│       └── xrd_sample8.ipynb
├── sixs_tools/          # Python package for reading NeXus files
│   ├── read_nxs5.py     # NeXus HDF5 file reader
│   ├── bin_util.py      # Binning and image processing tools
│   ├── utilities.py     # General utility functions
│   └── alias_dict.txt   # Alias dictionary for NeXus files
├── config.example.json  # Template for local data paths (copy to config.json)
├── data/                # Local data (ignored by git)
├── environment.yml      # Conda dependencies
├── pyproject.toml       # Package metadata (for editable install)
├── setup.bat            # One-click setup script (Windows)
├── setup.sh             # One-click setup script (macOS / Linux)
└── main.py              # Entry point script
```

## Quick start

### Prerequisites

- **Git** — to clone the repository.
- **Miniconda** or **Anaconda** — to manage the Python environment. Download from https://docs.conda.io/en/latest/miniconda.html.

### 1. Clone the repository

```bash
git clone https://github.com/Awilson-cnrs/SIXS_analysis.git
cd SIXS_analysis
```

### 2. Run the setup script

The setup script creates the conda environment, installs all dependencies, registers the Jupyter kernel, and configures environment variables to avoid package conflicts.

**Windows:**
```bash
setup.bat
```

**macOS / Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

> **Note:** After the script finishes, **restart your terminal and PyCharm** so the `PYTHONNOUSERSITE` environment variable takes effect.

### 3. Configure PyCharm

1. **Set the project interpreter**:
   - **Settings → Project → Python Interpreter** → gear icon ⚙️ → **Add...**
   - Choose **Conda Environment → Existing environment**.
   - Point to the conda Python executable:
     ```
     # Windows
     %USERPROFILE%\anaconda3\envs\datascience\python.exe
     # or miniconda3 instead of anaconda3

     # macOS / Linux
     ~/anaconda3/envs/datascience/bin/python
     ```
   - Click **OK**.

2. **Open a notebook** and verify the kernel in the top-right corner shows **Python (datascience)**.

### 4. (Optional) Launch Jupyter Lab from the terminal

```bash
conda activate datascience
jupyter lab
```

Then open a notebook from `notebooks/xas/` or `notebooks/xrd/` and select the **Python (datascience)** kernel.

---

### Manual installation (alternative)

If the setup script doesn't work for your system, follow these steps manually:

```bash
# 1. Create the conda environment
conda env create -f environment.yml

# 2. Activate and install the package
conda activate datascience
pip install -e .

# 3. Register the Jupyter kernel
python -m ipykernel install --user --name datascience --display-name "Python (datascience)"

# 4. Prevent user site-packages from shadowing the conda environment
# Windows (PowerShell):
[System.Environment]::SetEnvironmentVariable("PYTHONNOUSERSITE", "1", "User")
# macOS / Linux:
echo 'export PYTHONNOUSERSITE=1' >> ~/.bashrc
```

## Usage

### Import tools in a notebook

```python
from sixs_tools import read_nxs5 as rn5
from sixs_tools import bin_util as bu3
from sixs_tools import utilities as ut3
```

### Configure data paths

Each collaborator has their own local data directory (Nextcloud, NFS, etc.). To avoid hardcoding paths in the notebooks, create a `config.json` file:

```bash
cp config.example.json config.json
```

Then edit `config.json` with your paths:

```json
{
    "data_root": "/path/to/your/data/",
    "mask_path": "binoculars/mask_nxs00057_20261013_22h40.npy"
}
```

- **`data_root`**: Root directory containing your `.nxs` data files.
- **`mask_path`**: Relative path to the mask `.npy` file from `data_root`.

The `config.json` file is ignored by git, so each collaborator keeps their own configuration without affecting others.

## Troubleshooting

### "ModuleNotFoundError: No module named 'sixs_tools'"

Make sure you installed the package in editable mode:
```bash
conda activate datascience
pip install -e .
```

### "ImportError: cannot import name 'Group' from 'larch'"

The wrong `larch` package is installed (a statistics library, not the XAS one). Fix it:
```bash
conda activate datascience
pip uninstall larch -y
pip install xraylarch
```

### Notebooks use the wrong Python kernel

In PyCharm, click the kernel name in the top-right corner of the notebook editor and select **Python (datascience)**. If it doesn't appear, verify the project interpreter is set to the `datascience` conda environment (Settings → Project → Python Interpreter).

### "HDF5 error: bad symbol table node signature"

The `.nxs` file is corrupted, likely from an incomplete cloud sync (Nextcloud, Dropbox, etc.). Re-download the file from the original source.

### Packages installed but not found in notebooks

Your user site-packages may shadow the conda environment. Set this environment variable:
```bash
# Windows (PowerShell)
[System.Environment]::SetEnvironmentVariable("PYTHONNOUSERSITE", "1", "User")

# macOS/Linux
echo 'export PYTHONNOUSERSITE=1' >> ~/.bashrc
```
Then restart PyCharm.

## Dependencies

Managed by `environment.yml` (conda) and `pyproject.toml` (pip editable install).

To add a new package:
```bash
conda activate datascience
conda install <package>
conda env export -n datascience > environment.yml
```

## License

This project is forked from [AndreaResta/sixs_readnxs](https://codeberg.org/AndreaResta/sixs_readnxs). Data was collected at the SOLEIL synchrotron (surface diffraction beamline).
