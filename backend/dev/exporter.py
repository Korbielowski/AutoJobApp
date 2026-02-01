import os
import yaml
from pathlib import Path

from fastapi.openapi.utils import get_openapi

from backend.app import app


def _generate_schema() -> None:
    get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    schema = yaml.dump(app.openapi(), default_flow_style=False)
    path = Path(os.path.dirname(os.path.abspath(__file__))) / ".." / ".." / "frontend" / "api" / "api.yaml"
    path.write_text(schema)

if __name__ == "__main__":
    _generate_schema()