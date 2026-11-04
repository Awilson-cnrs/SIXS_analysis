@echo off
REM Setup script for SIXS_analysis on Windows
REM This script creates the conda environment, installs the package, and configures Jupyter.

echo ========================================
echo SIXS Analysis - Setup Script (Windows)
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: conda is not found in your PATH.
    echo Please install Miniconda or Anaconda from https://docs.conda.io/en/latest/miniconda.html
    echo Then add it to your PATH and try again.
    pause
    exit /b 1
)

echo Step 1: Creating conda environment 'datascience'...
call conda env create -f environment.yml
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Environment creation failed. It may already exist. Updating instead...
    call conda env update -f environment.yml
)

echo.
echo Step 2: Activating environment and installing package...
call conda activate datascience
python -m pip install -e .

echo.
echo Step 3: Registering Jupyter kernel...
python -m ipykernel install --user --name datascience --display-name "Python (datascience)"

echo.
echo Step 4: Setting PYTHONNOUSERSITE environment variable...
setx PYTHONNOUSERSITE 1
echo.
echo IMPORTANT: Please restart PyCharm for the environment variable to take effect.

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps in PyCharm:
echo 1. Set project interpreter to the 'datascience' conda environment:
echo    Settings ^> Project ^> Python Interpreter ^> gear icon ^> Add...
echo    Choose 'Conda Environment ^> Existing environment' and point to:
echo    %USERPROFILE%\anaconda3\envs\datascience\python.exe
echo    (or miniconda3 instead of anaconda3)
echo.
echo 2. Open a notebook and verify the kernel shows 'Python (datascience)'
echo.
pause
