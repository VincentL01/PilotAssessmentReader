import json
from typing import Dict, List
from openai import OpenAI
from .config import OPENAI_API_KEY, CHAT_MODEL, BASE_URL

_client = OpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL)

REQUESTED_FIELDS = ["Who", "Role", "Aircraft", "From", "To", "Duration", "Autoland"]

def parse_nl_filters(prompt: str) -> Dict:
    """
    Parse airline/training_type/limit/export_parquet from NL.
    Schema-agnostic wrt records; this only guides filtering/export UX.
    """
    sys = "You convert a user request about pilot training records into JSON filters."
    user = f"""Request: {prompt}
Return a compact JSON object with keys:
- airline (string or null)
- training_type (string or null)
- limit (int or null)
- export_parquet (true/false)
Only return JSON."""
    try:
        resp = _client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role":"system","content":sys},{"role":"user","content":user}],
            temperature=0
        )
        txt = resp.choices[0].message.content.strip()
        if txt.startswith("```"):
            txt = txt.strip("`").split("\n",1)[1]
        data = json.loads(txt)
        return {
            "airline": data.get("airline"),
            "training_type": data.get("training_type"),
            "limit": data.get("limit"),
            "export_parquet": bool(data.get("export_parquet", False))
        }
    except Exception:
        p = prompt.lower()
        return {
            "airline": "VirginAir Australia" if "virgin" in p else ("AirTransat" if "airtransat" in p else None),
            "training_type": "Flight Training" if "training" in p else None,
            "limit": None,
            "export_parquet": ("parquet" in p)
        }

def llm_extract_fields(raw_json: str, requested_fields: List[str] = None) -> Dict[str, str]:
    """
    Ask gpt-4o-mini to map UNKNOWN schemas to requested fields.
    Missing/ambiguous => 'not found'. No extra keys. Strings only.
    """
    if requested_fields is None:
        requested_fields = REQUESTED_FIELDS

    sys = (
        "You are a strict JSON information extractor. "
        "Input is an arbitrary JSON document representing a training assessment. "
        "Return ONLY a compact JSON object with the requested keys. "
        "If a field is missing or ambiguous, set its value exactly to 'not found'."
    )
    user = f"""Requested keys: {requested_fields}

JSON document:
{raw_json}

Return ONLY a JSON object with keys {requested_fields}, values as strings. For route, use:
- "From" = departure location/airport code if present, else "not found"
- "To"   = arrival location/airport code if present, else "not found"
Do not add extra keys."""
    resp = _client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role":"system","content":sys},{"role":"user","content":user}],
        temperature=0
    )
    txt = resp.choices[0].message.content.strip()
    if txt.startswith("```"):
        txt = txt.strip("`").split("\n",1)[1]
    try:
        data = json.loads(txt)
    except Exception:
        data = {}
    out = {}
    for k in requested_fields:
        v = data.get(k, "not found")
        if v in (None, ""):
            v = "not found"
        out[k] = str(v)
    return out


