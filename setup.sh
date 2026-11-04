#!/usr/bin/env bash
# Setup script for SIXS_analysis on macOS/Linux
# This script creates the conda environment, installs the package, and configures Jupyter.

set -e

echo "========================================"
echo "SIXS Analysis - Setup Script (macOS/Linux)"
echo "========================================"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda is not found in your PATH."
    echo "Please install Miniconda or Anaconda from https://docs.conda.io/en/latest/miniconda.html"
    echo "Then add it to your PATH and try again."
    exit 1
fi

echo "Step 1: Creating conda environment 'datascience'..."
if conda env create -f environment.yml; then
    echo "Environment created successfully."
else
    echo ""
    echo "WARNING: Environment creation failed. It may already exist. Updating instead..."
    conda env update -f environment.yml
fi

echo ""
echo "Step 2: Activating environment and installing package..."
eval "$(conda shell.bash hook)"
conda activate datascience
python -m pip install -e .

echo ""
echo "Step 3: Registering Jupyter kernel..."
python -m ipykernel install --user --name datascience --display-name "Python (datascience)"

echo ""
echo "Step 4: Setting PYTHONNOUSERSITE environment variable..."
echo 'export PYTHONNOUSERSITE=1' >> ~/.bashrc
echo 'export PYTHONNOUSERSITE=1' >> ~/.zshrc 2>/dev/null || true
echo ""
echo "IMPORTANT: Please restart your terminal and PyCharm for the environment variable to take effect."

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Next steps in PyCharm:"
echo "1. Set project interpreter to the 'datascience' conda environment:"
echo "   Settings > Project > Python Interpreter > gear icon > Add..."
echo "   Choose 'Conda Environment > Existing environment' and point to:"
echo "   ~/anaconda3/envs/datascience/bin/python"
echo "   (or ~/miniconda3 instead of ~/anaconda3)"
echo ""
echo "2. Open a notebook and verify the kernel shows 'Python (datascience)'"
echo ""
