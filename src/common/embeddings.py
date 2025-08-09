import numpy as np
from typing import List
from openai import OpenAI
from .config import OPENAI_API_KEY, EMBED_MODEL, EMBED_MODEL_API_KEY, BASE_URL

_client = OpenAI(api_key=EMBED_MODEL_API_KEY, base_url=BASE_URL)

def embed_texts(texts: List[str]) -> np.ndarray:
    vectors = []
    # Simple per-text call (can be batched later if needed)
    for t in texts:
        r = _client.embeddings.create(model=EMBED_MODEL, input=t)
        vectors.append(r.data[0].embedding)
    return np.array(vectors, dtype=np.float32)
