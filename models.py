from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Action(BaseModel):
    id: str
    description: str
    owner: str = ""
    owner_type: str = "unclear"
    status: str = "open"
    due_date: Optional[str] = None
    waiting_on: List[str] = Field(default_factory=list)
    people: List[str] = Field(default_factory=list)
    source_id: str
    evidence: str = ""
    uncertainty: str = "low"

    @field_validator("owner", mode="before")
    @classmethod
    def normalize_owner(cls, value):
        if value is None:
            return ""
        return str(value)

    @field_validator("evidence", mode="before")
    @classmethod
    def normalize_evidence(cls, value):
        if value is None:
            return ""

        if isinstance(value, list):
            return "; ".join(str(item) for item in value)

        return str(value)

    @field_validator("waiting_on", mode="before")
    @classmethod
    def normalize_waiting_on(cls, value):
        if value is None:
            return []

        if isinstance(value, str):
            return [value]

        if isinstance(value, list):
            return [str(item) for item in value]

        return []

    @field_validator("uncertainty", mode="before")
    @classmethod
    def normalize_uncertainty(cls, value):
        if isinstance(value, bool):
            return "high" if value else "low"

        if isinstance(value, str):
            value = value.lower().strip()

            if value in {"low", "medium", "high"}:
                return value

        return "medium"


class ExtractionResult(BaseModel):
    actions: List[Action] = Field(default_factory=list)