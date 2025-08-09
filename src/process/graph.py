from typing import TypedDict, List, Dict, Any
import pandas as pd

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools.render import render_text_description

from src.common.config import CHAT_MODEL, TOP_K, OPENAI_API_KEY, BASE_URL
from src.common.vectors import load_faiss
from src.common.io import load_manifest
from src.common.tools import PARSE_FILTERS, EXTRACT_FIELDS

# ---- Graph state ----
class AppState(TypedDict):
    prompt: str
    filters: Dict[str, Any]
    candidates: List[Dict[str, Any]]
    rows: List[Dict[str, Any]]
    export_path: str

# ---- Nodes ----
def parse_filters_node(state: AppState) -> AppState:
    llm = ChatOpenAI(model=CHAT_MODEL, api_key=OPENAI_API_KEY, base_url=BASE_URL, temperature=0)
    llm = llm.bind_tools([PARSE_FILTERS])

    system = SystemMessage(content=(
        "You parse the user's request into structured filters by calling the 'parse_filters' tool."
        "Return the tool call only."
    ))
    user = HumanMessage(content=state["prompt"])
    resp = llm.invoke([system, user])

    # Extract tool call result
    tool_calls = getattr(resp, "tool_calls", []) or []
    filt = {"airline": None, "training_type": None, "limit": None, "export_parquet": False}
    for tc in tool_calls:
        if tc["name"] == "parse_filters":
            filt = {**filt, **tc["args"]}
            break
    state["filters"] = filt
    return state

def retrieve_node(state: AppState) -> AppState:
    vs = load_faiss()
    retriever = vs.as_retriever(search_kwargs={"k": TOP_K})
    docs = retriever.invoke(state["prompt"])

    # Post-filter by airline/training_type if provided
    airline = (state["filters"] or {}).get("airline")
    training = (state["filters"] or {}).get("training_type")
    # Keep unique doc_ids
    seen = set()
    candidates = []
    for d in docs:
        md = d.metadata or {}
        if airline and md.get("airline", "").lower() != airline.lower():
            continue
        if training and md.get("training_type", "").lower() != training.lower():
            continue
        did = md.get("doc_id")
        if not did or did in seen:
            continue
        seen.add(did)
        candidates.append(md)
    state["candidates"] = candidates
    return state

def extract_node(state: AppState) -> AppState:
    # Load manifest to get raw_json per doc_id
    manifest = load_manifest().set_index("doc_id")
    llm = ChatOpenAI(model=CHAT_MODEL, api_key=OPENAI_API_KEY, base_url=BASE_URL, temperature=0)
    llm = llm.bind_tools([EXTRACT_FIELDS])

    rows = []
    for md in state["candidates"]:
        doc_id = md["doc_id"]
        raw_json = manifest.loc[doc_id]["raw_json"]

        system = SystemMessage(content=(
            "You extract seven fields from an arbitrary JSON document by calling the 'extract_fields' tool. "
            "If any field is missing or ambiguous, set its value to 'not found'. "
            "Requested keys: Who, Role, Aircraft, From, To, Duration, Autoland."
        ))
        user = HumanMessage(content=f"JSON:\n```json\n{raw_json}\n```")
        resp = llm.invoke([system, user])

        tool_calls = getattr(resp, "tool_calls", []) or []
        extracted = {
            "Who":"not found","Role":"not found","Aircraft":"not found",
            "From":"not found","To":"not found","Duration":"not found","Autoland":"not found"
        }
        for tc in tool_calls:
            if tc["name"] == "extract_fields":
                args = tc["args"] or {}
                # normalize alias From_
                if "From_" in args and "From" not in args:
                    args["From"] = args.pop("From_")
                extracted.update(args)
                break

        rows.append({
            **extracted,
            "airline": md.get("airline","not found"),
            "training_type": md.get("training_type","not found"),
            "document_type": md.get("document_type","not found"),
            "timestamp": md.get("timestamp","not found"),
            "doc_id": doc_id
        })
    state["rows"] = rows
    return state

# ---- Build graph ----
def build_graph():
    graph = StateGraph(AppState)
    graph.add_node("parse_filters", parse_filters_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("extract", extract_node)

    graph.add_edge(START, "parse_filters")
    graph.add_edge("parse_filters", "retrieve")
    graph.add_edge("retrieve", "extract")
    graph.add_edge("extract", END)
    return graph.compile()
