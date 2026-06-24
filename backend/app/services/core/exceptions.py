class ServiceError(Exception):
    """Base exception for service-layer errors."""


class LLMServiceError(ServiceError):
    """Raised when the LLM service encounters an unrecoverable error."""


class ValidationError(ServiceError):
    """Raised when input validation fails."""
