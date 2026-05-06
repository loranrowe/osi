"""OSI model loader — YAML/JSON → Pydantic objects."""
from pathlib import Path
import json

import yaml
from pydantic import ValidationError

from .models import OSIDocument, SemanticModel
from .exceptions import OsiValidationError


def load_osi(path: str | Path) -> OSIDocument:
    path = Path(path)
    text = path.read_text(encoding="utf-8")

    if path.suffix in (".yaml", ".yml"):
        raw = yaml.safe_load(text)
    elif path.suffix == ".json":
        raw = json.loads(text)
    else:
        raise OsiValidationError(f"Unsupported file format: {path.suffix}")

    if isinstance(raw, dict) and "semantic_model" in raw:
        model_list = raw["semantic_model"]
    else:
        model_list = raw

    if not isinstance(model_list, list):
        model_list = [model_list]

    try:
        models = [SemanticModel.model_validate(m) for m in model_list]
    except ValidationError as e:
        raise OsiValidationError(str(e)) from e

    return OSIDocument(models=models)
