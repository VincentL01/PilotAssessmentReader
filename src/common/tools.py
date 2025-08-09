# src/common/tools.py
from typing import Optional, Dict
from collections import OrderedDict

from pydantic import BaseModel, Field, field_validator, ConfigDict
from langchain.tools import StructuredTool


# -------------------------------
# Helpers for normalization
# -------------------------------
def _nf(v: Optional[str]) -> str:
    if v is None:
        return "not found"
    s = str(v).strip()
    return s if s else "not found"

def _norm_boolish(v: Optional[str]) -> str:
    s = _nf(v).lower()
    if s in ("true", "yes", "y", "1", "checked"):
        return "true"
    if s in ("false", "no", "n", "0", "unchecked", "not found"):
        return "false" if s != "not found" else "not found"
    # tolerate random inputs like "N/A"
    return "not found"

def _norm_role(v: Optional[str]) -> str:
    s = _nf(v).lower()
    # common variants
    if s in ("pf", "pilot flying", "pilot-flying", "p/f"):
        return "PF"
    if s in ("pm", "pilot monitoring", "pilot-monitoring", "p/m"):
        return "PM"
    if s in ("pf/pm", "pm/pf", "both"):
        return "PF/PM"
    # if it's clearly not found or junk
    if s == "not found" or len(s) > 40:
        return "not found"
    # last-chance heuristic (don't overfit)
    if "flying" in s:
        return "PF"
    if "monitor" in s:
        return "PM"
    return "not found"


# -------------------------------
# Tool 1: Parse filters from NL
# -------------------------------
class FiltersInput(BaseModel):
    """Structured filters for retrieval/export."""
    model_config = ConfigDict(extra="forbid")

    airline: Optional[str] = Field(None, description="Airline name if specified.")
    training_type: Optional[str] = Field(None, description="Training type (e.g., 'Flight Training') if specified.")
    limit: Optional[int] = Field(None, description="Limit the number of records.")
    export_parquet: bool = Field(False, description="Whether to export the result as a Parquet file.")

def parse_filters_tool(
    airline: Optional[str] = None,
    training_type: Optional[str] = None,
    limit: Optional[int] = None,
    export_parquet: bool = False,
) -> Dict:
    # Identity: return exactly what the model parsed.
    return {
        "airline": airline,
        "training_type": training_type,
        "limit": limit,
        "export_parquet": export_parquet,
    }

PARSE_FILTERS = StructuredTool.from_function(
    name="parse_filters",
    func=parse_filters_tool,
    args_schema=FiltersInput,
    description="Parse a natural language request for pilot training records into structured filters.",
)


# -------------------------------
# Tool 2: Extract fields from raw JSON (model fills values)
# -------------------------------
class ExtractFieldsInput(BaseModel):
    """
    The model must provide values for these keys after reading the raw JSON in-context.
    This tool only validates/normalizes them. Any missing/empty -> 'not found'.
    """
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    Who: Optional[str] = Field(None, description="Pilot/person name or 'not found'")
    Role: Optional[str] = Field(None, description="PF/PM/other or 'not found'")
    Aircraft: Optional[str] = Field(None, description="Aircraft type or 'not found'")
    From_: Optional[str] = Field(None, alias="From", description="Departure airport code or 'not found'")
    To: Optional[str] = Field(None, description="Arrival airport code or 'not found'")
    Duration: Optional[str] = Field(None, description="Duration or 'not found'")
    Autoland: Optional[str] = Field(None, description="'true'/'false'/'not found'")

    # Normalizers
    @field_validator("Who", mode="before")
    @classmethod
    def _val_who(cls, v): return _nf(v)

    @field_validator("Role", mode="before")
    @classmethod
    def _val_role(cls, v): return _norm_role(v)

    @field_validator("Aircraft", mode="before")
    @classmethod
    def _val_ac(cls, v): return _nf(v)

    @field_validator("From_", mode="before")
    @classmethod
    def _val_from(cls, v): return _nf(v)

    @field_validator("To", mode="before")
    @classmethod
    def _val_to(cls, v): return _nf(v)

    @field_validator("Duration", mode="before")
    @classmethod
    def _val_dur(cls, v): return _nf(v)

    @field_validator("Autoland", mode="before")
    @classmethod
    def _val_autoland(cls, v): return _norm_boolish(v)


def extract_fields_tool(**kwargs) -> Dict:
    """
    Identity-ish: returns sanitized values the model provided.
    Ensures alias 'From' maps to our internal key and all outputs are strings,
    with 'not found' if missing/empty.
    """
    data = ExtractFieldsInput(**kwargs)
    # Preserve output order as required by your assignment
    out = OrderedDict()
    out["Who"] = data.Who or "not found"
    out["Role"] = data.Role or "not found"
    out["Aircraft"] = data.Aircraft or "not found"
    out["From"] = data.From_ or "not found"
    out["To"] = data.To or "not found"
    out["Duration"] = data.Duration or "not found"
    out["Autoland"] = data.Autoland or "not found"
    return dict(out)

EXTRACT_FIELDS = StructuredTool.from_function(
    name="extract_fields",
    func=extract_fields_tool,
    args_schema=ExtractFieldsInput,
    description=(
        "Return a JSON object with the requested keys extracted from the provided raw JSON (seen in the chat). "
        "If a field is missing or ambiguous, set it to 'not found'."
    ),
)
