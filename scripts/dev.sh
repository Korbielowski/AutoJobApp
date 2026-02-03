echo "Running backend server..."
uv run fastapi dev backend/app.py &
cd frontend/
echo "Running frontend file watcher..."
bun run vinxi dev
cd ../