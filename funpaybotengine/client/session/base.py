from __future__ import annotations


__all__ = ('BaseSession', 'RawResponse', 'Response')

from typing import TYPE_CHECKING, Any, Generic, TypeVar
from dataclasses import dataclass
from abc import ABC, abstractmethod
from http import HTTPStatus
from urllib.parse import urlparse

from funpaybotengine.exceptions import (
    NotFoundError,
    ForbiddenError,
    BadRequestError,
    FunPayServerError,
    UnauthorizedError,
    RateLimitExceededError,
    UnexpectedHTTPStatusError,
)


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.methods.base import FunPayMethod, MethodReturnType


_exceptions: dict[int, Any] = {
    HTTPStatus.TOO_MANY_REQUESTS: RateLimitExceededError,
    HTTPStatus.UNAUTHORIZED: UnauthorizedError,
    HTTPStatus.FORBIDDEN: ForbiddenError,
    HTTPStatus.NOT_FOUND: NotFoundError,
    HTTPStatus.BAD_REQUEST: BadRequestError,
}


ResponseObject = TypeVar('ResponseObject', bound=Any)


@dataclass
class RawResponse(Generic[ResponseObject]):
    url: str
    status_code: HTTPStatus | int
    raw_response: str
    headers: dict[str, str]
    cookies: dict[str, str]
    method_obj: FunPayMethod[ResponseObject]
    context: dict[str, Any]
    executed_as: Bot

    @property
    def locale(self) -> str:
        parsed = urlparse(self.url)
        path_parts = parsed.path.strip('/').split('/')

        if path_parts and path_parts[0] in ['en', 'uk']:
            return path_parts[0]
        return 'ru'


@dataclass
class Response(RawResponse[ResponseObject], Generic[ResponseObject]):
    response_obj: ResponseObject

    @classmethod
    def from_raw_response(
        cls,
        raw: RawResponse[ResponseObject],
        response_obj: ResponseObject,
    ) -> Response[ResponseObject]:
        return cls(**raw.__dict__, response_obj=response_obj)


class BaseSession(ABC):
    """
    Base session.
    """

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def make_request(
        self,
        method: FunPayMethod[MethodReturnType],
        bot: Bot,
        timeout: float | None = None,
        skip_session_cookies: bool = False,
    ) -> Response[MethodReturnType]: ...

    def check_status_code(self, method: FunPayMethod[Any], status_code: int | HTTPStatus) -> None:
        """
        Checks the response's status code and raises an exception if it is not in the
        list of methods expected status codes.

        :param method: Method obj.
        :param status_code: Status code to check.

        :raises BadRequestError: if `status_code` is 400.
        :raises UnauthorizedError: if `status_code` is 401.
        :raises ForbiddenError: if `status_code` is 403.
        :raises NotFoundError: if `status_code` is 404.
        :raises RateLimitExceededError: if `status_code` is 429.
        :raises FunPayServerError: if `status_code` >= 500.
        :raises UnexpectedHTTPStatusError: in any other cases.
        """

        if status_code in method.expected_status_codes:
            return

        if status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            raise FunPayServerError(method=method, status=status_code)

        if status_code not in _exceptions:
            raise UnexpectedHTTPStatusError(method=method, status=status_code)

        raise _exceptions[status_code](method=method)

    async def __aenter__(self) -> BaseSession:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
