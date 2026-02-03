#!/bin/sh

echo "Generating OpenAPI client..."
cd frontend/
bun run openapi-typescript api/api.yaml -o api/api.ts
echo "Building static files..."
bun run vinxi build
cd ../
echo "Removing old static files..."
rm -rf backend/_static
echo "Moving new static files..."
mkdir -p backend/_static
mv frontend/.output/public/* backend/_static
echo "Frontend has been successfully built"
