import numpy as np
import pandas as pd
import faiss
from .config import INDEX_PATH, MANIFEST_PATH, IDXMAP_PATH

def build_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def save_index(index: faiss.IndexFlatL2):
    faiss.write_index(index, INDEX_PATH)

def load_index() -> faiss.IndexFlatL2:
    return faiss.read_index(INDEX_PATH)

def save_manifest(df: pd.DataFrame):
    df.to_parquet(MANIFEST_PATH, index=False)

def load_manifest() -> pd.DataFrame:
    return pd.read_parquet(MANIFEST_PATH)

def save_index_map(idx_map: np.ndarray):
    np.save(IDXMAP_PATH, idx_map)

def load_index_map() -> np.ndarray:
    return np.load(IDXMAP_PATH)
