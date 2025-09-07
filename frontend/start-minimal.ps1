Write-Host "Fixing npm dependencies..." -ForegroundColor Green

Write-Host "Backing up current package.json..." -ForegroundColor Yellow
Copy-Item "package.json" "package.json.backup" -Force

Write-Host "Using minimal package.json..." -ForegroundColor Yellow
Copy-Item "package-minimal.json" "package.json" -Force

Write-Host "Clearing npm cache..." -ForegroundColor Yellow
npm cache clean --force

Write-Host "Installing minimal dependencies..." -ForegroundColor Yellow
npm install

Write-Host "Starting development server..." -ForegroundColor Green
npm run dev
