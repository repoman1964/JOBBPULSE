"""Application HTTP errors with stable error codes."""

from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail={"code": code, "message": message, "details": self.details})


def unauthorized(message: str = "Authentication required.") -> AppError:
    return AppError("UNAUTHORIZED", message, status.HTTP_401_UNAUTHORIZED)


def forbidden(message: str = "You do not have permission to perform this action.") -> AppError:
    return AppError("FORBIDDEN", message, status.HTTP_403_FORBIDDEN)


def not_found(code: str, message: str) -> AppError:
    return AppError(code, message, status.HTTP_404_NOT_FOUND)


def conflict(code: str, message: str) -> AppError:
    return AppError(code, message, status.HTTP_409_CONFLICT)
