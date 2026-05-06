"""OSI Pydantic models — typed representations of OSI semantic model entities."""
from pydantic import BaseModel

from .enums import Dialect


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
