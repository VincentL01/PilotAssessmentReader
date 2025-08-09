from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Any
from .config import FAISS_DIR, EMBED_MODEL, EMBED_MODEL_API_KEY, BASE_URL

def build_faiss_from_chunks(texts: List[str], metadatas: List[Dict[str, Any]]) -> FAISS:
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL, api_key=EMBED_MODEL_API_KEY, base_url=BASE_URL)
    vs = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
    vs.save_local(str(FAISS_DIR))
    return vs

def load_faiss() -> FAISS:
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL, api_key=EMBED_MODEL_API_KEY, base_url=BASE_URL)
    return FAISS.load_local(str(FAISS_DIR), embeddings, allow_dangerous_deserialization=True)
