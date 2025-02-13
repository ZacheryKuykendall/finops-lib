# Deactivate venv if active
if (Get-Command "deactivate" -errorAction SilentlyContinue) {
    deactivate
}

# Remove virtual environment
if (Test-Path venv) { Remove-Item -Recurse -Force venv }

# Remove build artifacts and cache directories
Get-ChildItem -Path . -Include *.egg-info,build,dist,__pycache__,*.pyc,.pytest_cache,.eggs -Recurse | 
    Where-Object { $_.FullName -notlike '*\.git\*' } | 
    Remove-Item -Recurse -Force

# Clean pip cache
pip cache purge
