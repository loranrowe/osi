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
