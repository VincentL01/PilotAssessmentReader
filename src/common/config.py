import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Models (per assignment)
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-small")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY")
EMBED_MODEL_API_KEY = os.getenv("EMBED_MODEL_API_KEY", "YOUR_API_KEY")
BASE_URL = os.getenv("BASE_URL", "YOUR_BASE_URL")

# Storage
DATA_DIR = Path(os.getenv("DATA_DIR", "data")).resolve()
FAISS_DIR = DATA_DIR / "faiss_index"
MANIFEST_PATH = DATA_DIR / "manifest.parquet"

# Digest strategy
#  - verbatim: exact file contents
#  - canonical: sorted-keys JSON string
#  - pathlines: keypath: value lines (default)
DIGEST_MODE = os.getenv("DIGEST_MODE", "pathlines").lower()
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "2000"))     # chars (approx tokens)
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Retrieval
TOP_K = int(os.getenv("TOP_K", "50"))
