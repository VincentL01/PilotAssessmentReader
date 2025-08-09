import glob
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from src.common.config import DATA_DIR, FAISS_DIR
from src.common.io import ensure_dirs, read_json_text, parse_json, safe_meta, save_manifest
from src.common.digest import digest_for_embedding
from src.common.vectors import build_faiss_from_chunks

def ingest(folders: List[str]):
    ensure_dirs()
    texts, metadatas, manifest_rows = [], [], []

    files: List[Path] = []
    for folder in folders:
        files.extend(Path(folder).glob("*.json"))
    if not files:
        print("No JSON files found.")
        return

    for fp in sorted(files):
        raw_text = read_json_text(fp)
        doc = parse_json(raw_text)

        airline = safe_meta(doc, "Airline")
        training_type = safe_meta(doc, "TrainingType")
        document_type = safe_meta(doc, "Type")
        timestamp = safe_meta(doc, "Date")
        if timestamp == "not found":
            timestamp = datetime.utcfromtimestamp(fp.stat().st_mtime).strftime("%Y-%m-%d")

        chunks = digest_for_embedding(doc, raw_text, str(fp))
        for i, ch in enumerate(chunks):
            texts.append(ch)
            metadatas.append({
                "doc_id": str(fp),
                "chunk_id": i,
                "airline": airline,
                "training_type": training_type,
                "document_type": document_type,
                "timestamp": timestamp,
            })

        manifest_rows.append({
            "doc_id": str(fp),
            "path": str(fp),
            "airline": airline,
            "training_type": training_type,
            "document_type": document_type,
            "timestamp": timestamp,
            "raw_json": raw_text,   # keep original text verbatim
        })

    # Build & save FAISS
    vs = build_faiss_from_chunks(texts, metadatas)
    save_manifest(manifest_rows)

    print(f"✅ Ingested {len(files)} files; stored {len(texts)} chunks into {FAISS_DIR}")
