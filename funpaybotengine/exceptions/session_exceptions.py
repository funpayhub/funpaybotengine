from __future__ import annotations


__all__ = (
    'FunPayRequestError',
    'UnexpectedHTTPStatusError',
    'RateLimitExceededError',
    'UnauthorizedError',
    'ForbiddenError',
    'BadRequestError',
    'NotFoundError',
    'FunPayServerError',
    'BannedError',
)

from typing import TYPE_CHECKING, Any

from funpaybotengine.exceptions.base import FunPayBotEngineError


if TYPE_CHECKING:
    from funpaybotengine.methods.base import FunPayMethod


class FunPayRequestError(FunPayBotEngineError):
    def __init__(self, method: FunPayMethod[Any]) -> None:
        super().__init__(
            f'An unexpected error occurred while processing a request to {method.url!r}.',
            method,
        )
        self.method = method

    def __str__(self) -> str:
        return str(self.args[0])


class BannedError(FunPayRequestError): ...


class UnexpectedHTTPStatusError(FunPayRequestError):
    def __init__(self, method: FunPayMethod[Any], status: int):
        super().__init__(method=method)
        self.status = status
        self.expected_status_codes = method.expected_status_codes

    def __str__(self) -> str:
        return (
            f'Unexpected response status code {self.status} for {self.method.url!r} '
            f'(expected: {self.method.expected_status_codes!r})'
        )


class RateLimitExceededError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any]):
        super().__init__(method=method, status=429)


class UnauthorizedError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any]):
        super().__init__(method=method, status=401)


class ForbiddenError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any]):
        super().__init__(method=method, status=403)


class BadRequestError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any]):
        super().__init__(method=method, status=400)


class NotFoundError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any]):
        super().__init__(method=method, status=404)


class FunPayServerError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any], status: int = 500):
        super().__init__(method=method, status=status)
