import json
from typing import Any, Dict, List
from .config import DIGEST_MODE, CHUNK_SIZE, CHUNK_OVERLAP

def flatten_json(obj: Any, prefix: str = "", out: Dict[str, str] = None, max_items: int = 50000) -> Dict[str, str]:
    if out is None:
        out = {}
    if len(out) >= max_items:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            flatten_json(v, key, out, max_items)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}[{i}]"
            flatten_json(v, key, out, max_items)
    else:
        try:
            s = str(obj)
        except Exception:
            s = repr(obj)
        out[prefix] = s
    return out

def _chunk(text: str) -> List[str]:
    if CHUNK_SIZE <= 0: return [text]
    chunks, i, n = [], 0, len(text)
    while i < n:
        j = min(i + CHUNK_SIZE, n)
        chunks.append(text[i:j])
        if j == n: break
        i = max(j - CHUNK_OVERLAP, 0)
    return chunks

def digest_for_embedding(doc: dict, raw_text: str, file_path: str) -> List[str]:
    header = f"__FILE_PATH__={file_path}\n"
    if DIGEST_MODE == "verbatim":
        return [header + c for c in _chunk(raw_text)]
    if DIGEST_MODE == "canonical":
        body = json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return [header + c for c in _chunk(body)]
    # pathlines (default)
    flat = flatten_json(doc)
    body = "\n".join(f"{k}: {flat[k]}" for k in sorted(flat))
    return [header + c for c in _chunk(body)]
