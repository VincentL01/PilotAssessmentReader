import pandas as pd
from typing import Optional
from src.process.graph import build_graph
from src.common.io import load_manifest
from src.common.config import DATA_DIR

def run_query(prompt: str, out_path: Optional[str] = None):
    graph = build_graph()
    state = {"prompt": prompt, "filters": {}, "candidates": [], "rows": [], "export_path": out_path or ""}
    result = graph.invoke(state)
    rows = result["rows"]
    df = pd.DataFrame(rows, columns=[
        "Who","Role","Aircraft","From","To","Duration","Autoland",
        "airline","training_type","document_type","timestamp","doc_id"
    ])
    if out_path and out_path.endswith(".parquet"):
        df.to_parquet(DATA_DIR / out_path, index=False)
        print(f"✅ Exported {len(df)} rows to {out_path}")
    else:
        print(df.to_string(index=False))

def export_direct(airline: str, training_type: str, out_path: str):
    """
    Deterministic filter-based export (no NL). Still schema-agnostic because
    extraction is done in the graph's 'extract' node via function calling.
    """
    prompt = f"Return all pilot training records for airline '{airline}' and training type '{training_type}'. Export parquet."
    run_query(prompt, out_path)
