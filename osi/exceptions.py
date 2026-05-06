"""OSI custom exceptions for agent-readable errors."""


class OsiError(Exception):
    """Base exception for all OSI errors."""
    pass


class OsiValidationError(OsiError):
    """Validation failure — wraps Pydantic ValidationError with readable paths."""
    pass


class OsiIntegrityError(OsiError):
    """Referential integrity violation — e.g., relationship references unknown dataset."""
    pass
