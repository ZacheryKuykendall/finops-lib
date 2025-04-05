# Stop any existing Python processes
Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force

# Stop any existing Docker containers
cd azure_finops_cli
docker-compose down

# Start Docker containers
docker-compose up -d

# Wait for containers to be ready
Start-Sleep -Seconds 5

# Start the Flask application
cd ..
python -m finops_lib.web 