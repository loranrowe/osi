"""OSI Pydantic models — typed representations of OSI semantic model entities."""
from pydantic import BaseModel, field_validator, model_validator

from .enums import Dialect, Vendor


class DialectDef(BaseModel):
    model_config = {"extra": "forbid"}
    dialect: Dialect
    expression: str


class FieldExpression(BaseModel):
    model_config = {"extra": "forbid"}
    dialects: list[DialectDef]


class DimensionMeta(BaseModel):
    model_config = {"extra": "forbid"}
    is_time: bool = False


class AIContext(BaseModel):
    model_config = {"extra": "forbid"}
    instructions: str | None = None
    synonyms: list[str] = []
    examples: list[str] = []

    @field_validator("synonyms", "examples", mode="before")
    @classmethod
    def _default_empty_list(cls, v):
        return v or []

    @model_validator(mode="wrap")
    @classmethod
    def _wrap_string_or_none(cls, data, handler):
        if isinstance(data, str):
            data = {"instructions": data}
        if data is None:
            data = {}
        return handler(data)


class CustomExtension(BaseModel):
    model_config = {"extra": "forbid"}
    vendor_name: Vendor
    data: str


class Field(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    expression: FieldExpression
    dimension: DimensionMeta | None = None
    label: str | None = None
    description: str | None = None
    ai_context: AIContext | str | None = None
    custom_extensions: list[CustomExtension] = []

    @field_validator("ai_context", mode="before")
    @classmethod
    def _normalize_ai_context(cls, v):
        if v is None or isinstance(v, AIContext):
            return v
        if isinstance(v, str):
            return AIContext(instructions=v)
        return v
