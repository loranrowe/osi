"""OSI Pydantic models — typed representations of OSI semantic model entities."""
from pydantic import BaseModel, Field as PydanticField, field_validator, model_validator

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


class Dataset(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    source: str
    primary_key: list[str] = []
    unique_keys: list[list[str]] = []
    description: str | None = None
    ai_context: AIContext | str | None = None
    fields: list[Field] = []
    custom_extensions: list[CustomExtension] = []

    @field_validator("ai_context", mode="before")
    @classmethod
    def _normalize_ai_context(cls, v):
        if v is None or isinstance(v, AIContext):
            return v
        if isinstance(v, str):
            return AIContext(instructions=v)
        return v


class Metric(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    expression: FieldExpression
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


class Relationship(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    from_: str = PydanticField(alias="from")
    to: str
    from_columns: list[str]
    to_columns: list[str]
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

    @model_validator(mode="after")
    def _check_column_count(self):
        if len(self.from_columns) != len(self.to_columns):
            raise ValueError(
                f"from_columns and to_columns must have same length, "
                f"got {len(self.from_columns)} and {len(self.to_columns)}"
            )
        return self


class SemanticModel(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    description: str | None = None
    ai_context: AIContext | str | None = None
    datasets: list[Dataset]
    relationships: list[Relationship] = []
    metrics: list[Metric] = []
    custom_extensions: list[CustomExtension] = []

    @field_validator("ai_context", mode="before")
    @classmethod
    def _normalize_ai_context(cls, v):
        if v is None or isinstance(v, AIContext):
            return v
        if isinstance(v, str):
            return AIContext(instructions=v)
        return v

    @model_validator(mode="after")
    def _check_referential_integrity(self):
        dataset_names = {d.name for d in self.datasets}
        for rel in self.relationships:
            if rel.from_ not in dataset_names:
                raise ValueError(
                    f"Relationship '{rel.name}': 'from' dataset '{rel.from_}' "
                    f"not found in datasets"
                )
            if rel.to not in dataset_names:
                raise ValueError(
                    f"Relationship '{rel.name}': 'to' dataset '{rel.to}' "
                    f"not found in datasets"
                )
        return self


class OSIDocument(BaseModel):
    model_config = {"extra": "forbid"}
    models: list[SemanticModel]
