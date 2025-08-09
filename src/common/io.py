from pathlib import Path
import json
import pandas as pd
from typing import Dict, Any
from .config import DATA_DIR, MANIFEST_PATH

def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def safe_meta(doc: Dict[str, Any], key: str) -> str:
    try:
        v = doc.get(key, "not found")
        if v in (None, ""): return "not found"
        return str(v)
    except Exception:
        return "not found"

def save_manifest(rows):
    df = pd.DataFrame(rows)
    df.to_parquet(MANIFEST_PATH, index=False)

def load_manifest() -> pd.DataFrame:
    return pd.read_parquet(MANIFEST_PATH)

def read_json_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def parse_json(text: str) -> Dict[str, Any]:
    return json.loads(text)
