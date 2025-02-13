# Deactivate current venv if active
deactivate
# Remove venv directory
Remove-Item -Recurse -Force venv
# Remove all build artifacts
Get-ChildItem -Path . -Include *.egg-info,build,dist,__pycache__,*.pyc -Recurse | Remove-Item -Recurse -Force
# Remove setup files
if (Test-Path setup.py) { Remove-Item setup.py }
if (Test-Path pyproject.toml) { Remove-Item pyproject.toml }
if (Test-Path setup.cfg) { Remove-Item setup.cfg }
