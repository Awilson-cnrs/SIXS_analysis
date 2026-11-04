# SIXS Analysis — Setup Guide for Junie (AI Assistant)

> **Purpose:** This guide documents every pitfall encountered when setting up this project
> so that Junie on a different machine can avoid them and make the right decisions from
> the start. Read this **before** attempting any setup or troubleshooting.

---

## 1. Project Overview

- **Type:** Data science project for XAS and XRD analysis from surface diffraction experiments at the SOLEIL synchrotron.
- **Experimental approach:** The beamline is designed for fixed-energy surface diffraction, not energy scanning. "Braggap" scans simultaneously control the undulator gap and Bragg angle to track the harmonic and maintain intensity while scanning energy. XAS signals are extracted from the **background noise of the XPAD diffraction detector** instead of a fluorescence detector — the increase in background scattering at an absorption edge serves as the absorption signal.
- **Origin:** Forked from `AndreaResta/sixs_readnxs` on Codeberg, then heavily refactored.
- **Host:** GitHub repository `Awilson-cnrs/SIXS_analysis` (branch `main`).
- **Code:** Python package `sixs_tools/` + Jupyter notebooks in `notebooks/`.
- **Data:** `.nxs` (NeXus/HDF5) files stored on Nextcloud — **not in the repo**.

---

## 2. Critical Setup Decisions (Do These First)

### 2.1. Use a Shared Conda Environment — Never venv

- **Mandatory:** Use a **single shared conda environment** named `datascience`.
- **Never** create a project-local `venv/` or `.venv/` — the user explicitly forbids it.
- The environment is shared across multiple projects on the same machine.
- Python version: **3.12** (not 3.13 or 3.14 — see §3.3 for why).

### 2.2. Install Order Matters: Conda-Forge First, Then pip

The `environment.yml` uses a **mixed conda + pip** strategy:

1. **conda-forge** installs all binary packages (numpy, scipy, matplotlib, h5py, etc.).
2. **pip** installs only `xraylarch` — the XAS analysis library that is **not available on conda-forge**.

**Why this order matters:** Installing pip packages before conda packages (or mixing them
randomly) causes DLL conflicts, especially with HDF5 libraries. The conda dependency graph
must resolve first, then pip adds the one package it can't find on conda.

### 2.3. Set PYTHONNOUSERSITE=1 Immediately

**This is the single most important environment variable.**

On Windows, Python loads packages from `%APPDATA%\Python\PythonXX\site-packages\` **before**
the active conda environment. This directory often contains stale or wrong packages that
shadow the correct ones in conda.

**Symptom of the problem:**
- `from larch import Group` fails because it loads the wrong `larch` (a statistics library,
  not the XAS analysis library `xraylarch`).
- `import sixs_tools` fails because PyCharm's IDE-managed Jupyter server uses the system
  Python instead of the conda environment.

**Fix (Windows, set as User-level env var):**
```powershell
[System.Environment]::SetEnvironmentVariable("PYTHONNOUSERSITE", "1", "User")
```

**Fix (macOS/Linux):**
```bash
echo 'export PYTHONNOUSERSITE=1' >> ~/.bashrc
```

**After setting this, restart PyCharm completely** — not just the kernel. The variable is
read when the Python process starts, so killing a kernel isn't enough.

---

## 3. Known Pitfalls

### 3.1. The `larch` Package Name Hijack

**Problem:** The conda-forge package `larch` was hijacked by a statistics/discrete-choice
library (v6.x). The XAS analysis library you need is now distributed on PyPI as
`xraylarch`.

**Wrong:** `conda install larch` → installs the statistics library (no `Group` class).
**Right:** `pip install xraylarch` → installs the correct XAS library with `Group` and `pre_edge`.

**In `environment.yml`:** `xraylarch` appears under the `pip:` section, not under `dependencies:`.

### 3.2. HDF5 Library Version Mismatch

**Problem:** The `.nxs` data files were written with HDF5 1.14 format. If the installed
`h5py` bundles an older HDF5 library (e.g., 2.2.0), it can open the file header but
crashes when reading internal structure:

```
OSError: unable to synchronously open object (truncated file)
KeyError: "Unable to open object (bad symbol table node signature)"
```

**Fix:** Ensure `h5py` comes from conda-forge (which bundles HDF5 1.14+). Do **not**
install h5py via pip unless you're sure it bundles a compatible HDF5 version.

**Verification:** After installation, check:
```python
import h5py
print(h5py.__version__)       # Should be 3.x
print(h5py.get_config().hdf5) # Should show HDF5 1.14+
```

### 3.3. Python 3.14 Has No HDF5 1.14 Support on Windows

**Problem:** Python 3.14 was initially used, but conda-forge has no HDF5 1.14 build for
Python 3.14 on Windows. This forced a downgrade to Python 3.12.

**Fix:** Pin Python to `3.12` in `environment.yml`:
```yaml
dependencies:
  - python=3.12
```

### 3.4. PyCharm IDE-Managed Jupyter Server

**Problem:** PyCharm's "IDE-Managed Server (IPyKernel)" uses PyCharm's **project interpreter**,
not the system Jupyter kernels. If the project interpreter points to the wrong Python,
all imports fail.

**Fix:**
1. Set project interpreter to the `datascience` conda environment:
   ```
   Settings → Project → Python Interpreter → gear icon → Add...
   → Conda Environment → Existing environment
   → Point to: <conda_root>/envs/datascience/python
   ```
2. After setting, **invalidate caches** (File → Invalidate Caches → Invalidate and Restart).
3. Open a notebook — the kernel should now show "Python (datascience)".

**If the kernel doesn't appear in the dropdown:**
- Re-register it: `python -m ipykernel install --user --name datascience --display-name "Python (datascience)"`
- Invalidate caches and restart PyCharm.

### 3.5. Corrupted .nxs Files from Nextcloud Sync

**Problem:** Large `.nxs` files (~138 MB) synced through Nextcloud can become corrupted
due to chunked transfer interruptions. Symptoms:

```
OSError: unable to synchronously open object (truncated file)
KeyError: "Unable to open object (bad symbol table node signature)"
```

**Fix:** Re-sync the corrupted file from the original beamline data source, not from
the Nextcloud server (which may also have the corrupted version).

**Workaround:** Switch to a valid neighboring scan number. In `xas_sample1.ipynb`, the
list `nxstoPlot = [83, 89, 100, 141, 144, 147, 228, 232, 236, 253, 255, 257]` contains
scan numbers — only 83, 89, and 100 were verified as valid HDF5 files.

### 3.6. Corrupted msgpack in Conda Environment

**Problem:** The `msgpack` package in the conda environment had all `.py` files renamed
to `.c~`, breaking the entire Jupyter kernel chain (`ipykernel → jupyter_client → msgpack`).

**Fix:** `pip install --ignore-installed msgpack`

### 3.7. Circular Imports in `sixs_tools/__init__.py`

**Problem:** `bin_util.py` imports `utilities`, and `__init__.py` imported them in the
wrong order, causing circular import errors.

**Fix:** In `__init__.py`, import `utilities` **before** `bin_util`:
```python
from . import utilities
from . import bin_util
from . import read_nxs5
```

Also use relative imports inside the package:
```python
# In bin_util.py:
from . import utilities  # NOT: from sixs_tools import utilities
```

---

## 4. Setup Checklist (Order Matters)

When setting up on a new machine, follow these steps **in order**:

### Step 1: Clone the Repository
```bash
git clone https://github.com/Awilson-cnrs/SIXS_analysis.git
cd SIXS_analysis
```

### Step 2: Run the Setup Script
The project includes automated setup scripts that handle all the pitfalls above:

**Windows:** `setup.bat`
**macOS/Linux:** `chmod +x setup.sh && ./setup.sh`

The script:
1. Creates the `datascience` conda environment from `environment.yml`.
2. Installs the `sixs_tools` package in editable mode (`pip install -e .`).
3. Registers the Jupyter kernel.
4. Sets `PYTHONNOUSERSITE=1`.

### Step 3: Restart Terminal and PyCharm
**Mandatory** — the `PYTHONNOUSERSITE` environment variable only takes effect on process
start.

### Step 4: Configure PyCharm
1. **Settings → Project → Python Interpreter → Add...**
2. Choose **Conda Environment → Existing environment**.
3. Point to `<conda_root>/envs/datascience/python`.
4. **File → Invalidate Caches → Invalidate and Restart**.

### Step 5: Verify
Open `notebooks/xas_sample1.ipynb` and run the import cells:
```python
import numpy as np
import matplotlib.pyplot as plt
from sixs_tools import read_nxs5 as rn5
from scipy.signal import savgol_filter
from larch import Group
from larch.xafs import pre_edge
```

All should succeed without error.

---

## 5. Package Dependency Map

| Package | Source | Why | Common Pitfall |
|---|---|---|---|
| `numpy`, `scipy`, `matplotlib` | conda-forge | Core data science | None |
| `h5py` | conda-forge | Read .nxs HDF5 files | HDF5 version mismatch (§3.2) |
| `xraylarch` | **pip** | XAS analysis (`Group`, `pre_edge`) | `conda install larch` installs wrong package (§3.1) |
| `pandas` | conda-forge | Data manipulation | None |
| `natsort` | conda-forge | Natural sorting in utilities | None |
| `lmfit` | conda-forge | Curve fitting in utilities | None |
| `trimesh` | conda-forge | 3D mesh in bin_util | None |
| `scikit-image` | conda-forge | Image processing in bin_util | None |
| `imageio` | conda-forge | Image I/O in bin_util | None |
| `scikit-learn` | conda-forge | ML utilities | None |
| `jupyterlab` | conda-forge | Notebook IDE | None |
| `ipykernel` | conda-forge | Jupyter kernel | None |

**Key rule:** `xraylarch` is the **only** pip package. Everything else comes from conda-forge.

---

## 6. Project Structure

```
SIXS_analysis/
├── notebooks/           # Jupyter notebooks (snake_case names)
│   ├── xas_sample1.ipynb  # XAS analysis for Sample 1
│   ├── xas_sample2-4,8.ipynb
│   ├── xrd_sample2-4,8.ipynb
│   └── plot_xas_v1.ipynb
├── sixs_tools/          # Python package (editable install)
│   ├── __init__.py      # Package init — import order matters!
│   ├── read_nxs5.py     # NeXus file reader
│   ├── bin_util.py      # Binning utilities
│   ├── utilities.py     # General utilities
│   └── alias_dict.txt   # Element alias mappings (package data)
├── data/                # Local data (ignored by git)
├── environment.yml      # Conda environment definition
├── pyproject.toml       # Package metadata for editable install
├── setup.bat            # Windows setup script
├── setup.sh             # macOS/Linux setup script
├── README.md            # User-facing documentation
├── SETUP_GUIDE.md       # This file — AI assistant setup guide
└── .gitignore           # Git exclusions
```

---

## 7. Troubleshooting Flowchart

When a user reports "imports don't work":

1. **Check Python executable:** Is it the `datascience` conda env?
   - `sys.executable` should point to `<conda>/envs/datascience/python`
   - If not → fix project interpreter (§3.4)

2. **Check PYTHONNOUSERSITE:** Is it set to `1`?
   - `import os; print(os.environ.get('PYTHONNOUSERSITE'))`
   - If not → set it (§2.3) and restart PyCharm

3. **Check larch package:** Is it the right one?
   - `from larch import Group` should succeed
   - If `ImportError: cannot import name 'Group'` → wrong larch installed (§3.1)

4. **Check h5py/HDF5:** Can it read .nxs files?
   - `import h5py; print(h5py.get_config().hdf5)`
   - If HDF5 < 1.14 → reinstall from conda-forge (§3.2)

5. **Check sixs_tools:** Is it installed?
   - `from sixs_tools import read_nxs5` should succeed
   - If not → `pip install -e .` in the project root

6. **Check kernel:** Is Jupyter using the right Python?
   - In a notebook: `import sys; print(sys.executable)`
   - Should match the `datascience` conda env

---

## 8. What NOT To Do

| Action | Why |
|---|---|
| `conda install larch` | Installs wrong package (statistics, not XAS) |
| Create `venv/` or `.venv/` | User requires shared conda env |
| Install h5py via pip | Causes HDF5 DLL conflicts with conda packages |
| Skip `PYTHONNOUSERSITE=1` | User site-packages shadow conda env |
| Use Python 3.13/3.14 | No HDF5 1.14 support on Windows |
| Delete `alias_dict.txt` | Required by `read_nxs5.py` at runtime |
| Rename `sixs_tools/` back to `lib/` | Breaks all imports |
| Use `sys.path.append()` in notebooks | Unnecessary with editable install |

---

## 9. Git Branch History

The project was refactored on branch `refactor/structure-propre`, then merged into `main`.
The refactoring included:
- Renamed `lib/` → `sixs_tools/` with PEP-8 filenames.
- Renamed `Notebook/` → `notebooks/` with snake_case filenames.
- Removed 2 duplicate notebooks.
- Cleaned all imports (removed `sys.path.append`, `binoculars`, unused modules).
- Created `environment.yml`, `pyproject.toml`, `setup.bat/sh`, `README.md`.

Current branch: `main` (up to date with `origin/main`).

---

## 10. Contact & Context

- **User:** Novice data scientist, works at CNRS.
- **Data source:** Beamline experiments, stored on Nextcloud.
- **Original code:** Forked from `AndreaResta/sixs_readnxs` (Codeberg).
- **Refactoring goal:** Clean structure, shared conda env, no venv, portable setup.
