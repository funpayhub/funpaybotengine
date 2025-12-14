from __future__ import annotations


__all__ = ('FunPayMethod', 'MethodReturnType')

import inspect
from typing import TYPE_CHECKING, Any, Type, Generic, TypeVar
from abc import ABC
from http import HTTPStatus
from email.utils import parsedate_to_datetime
from collections.abc import Callable, Awaitable

from pydantic import Field, BaseModel, ConfigDict
from funpayparsers.parsers.base import ParsingOptions, FunPayObjectParser

from funpaybotengine.types.enums import Language
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.client.session.base import Response, RawResponse


R = TypeVar('R')
MethodReturnType = TypeVar('MethodReturnType', bound=Any)

if TYPE_CHECKING:
    CallableField = Callable[['FunPayMethod[Any]', Bot], R | Awaitable[R]]
else:
    CallableField = Callable[[Any, Any], R | Awaitable[R]]


class FunPayMethod(BaseModel, Generic[MethodReturnType], ABC):
    """Base method class."""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    url: CallableField[str] | str
    """Method URL."""

    method: HTTPMethod
    """
    HTTP Method.
    """

    locale: Language | None = None
    """
    FunPay locale.

    If specified and ``FunPayMethod.ignore_locale`` is ``False``,
    it will override bots locale when making a request.

    Defaults to ``None``.
    """

    ignore_locale: bool = False
    """
    Whether to ignore locale or not.
    
    If ``True``, ``FunPayMethod.locale`` will be ignored.
    """

    headers: CallableField[dict[str, str]] | dict[str, str] = Field(default_factory=dict)
    """
    Headers.

    Defaults to empty dict.
    """

    data: CallableField[dict[str, Any]] | dict[str, Any] = Field(default_factory=dict)
    """
    Additional data.

    Defaults to empty dict.
    """

    expected_status_codes: list[int | HTTPStatus] = [HTTPStatus.OK]
    """
    List of expected status codes.

    Defaults to ``[HTTPStatus.OK]``.
    """

    allow_anonymous: bool = False
    """
    Whether this method can be executed as anonymous user or not.
    
    Defaults to ``False``.
    """

    allow_uninitialized: bool = False
    """
    Whether this method can be executed as uninitialized user or not.
    
    Defaults to ``False``.
    """

    parser_cls: Type[FunPayObjectParser] | None = None  # type: ignore[type-arg]
    # unsupported by pydantic
    """
    Parser class (not an instance!) for parsing raw source.

    Defaults to ``None``.
    """

    parser_options: ParsingOptions | None = None
    """
    Instance of parser options for ``FunPayMethod.parser_cls``.

    Defaults to ``None``.
    """

    timeout: int | float = 10.0
    """
    Request timeout.

    Defaults to ``10.0``.
    """

    context: CallableField[dict[str, Any]] | dict[str, Any] = Field(default_factory=dict)
    """
    Additional context for building a final `funpaybotengine` object.
    
    Defaults to empty dict.
    """

    __model_to_build__: Type[MethodReturnType] | None = None

    def model_post_init(self, context: Any, /) -> None:
        super().model_post_init(context)
        if self.parser_cls and self.parser_options is None:
            self.parser_options = self.parser_cls.get_options_cls()()

    async def parse_result(self, response: RawResponse[Any]) -> Any:
        """
        Method that parses raw response.

        By default, this method will use ``FunPayMethod.parser_cls`` and
        ``FunPayMethod.parser_options`` to parse raw response, if
        ``FunPayMethod.parser_cls`` is specified.

        If ``FunPayMethod.parser_options`` is not specified, it will be
        generated automatically.

        If ``FunPayMethod.parser_cls`` not specified, returns raw response.

        :param response: raw response.  # todo: not a string, but an object!
        """
        if self.parser_cls is None:
            return response.raw_response

        return self.parser_cls(response.raw_response, options=self.parser_options).parse()

    async def transform_result(
        self,
        parsing_result: Any,
        response: RawResponse[Any],
    ) -> MethodReturnType:
        """
        Transforms a raw response or parser output
        (i.e., the result of ``FunPayMethod.parse_result``)
        into a type expected by or compatible with funpaybotengine
        (``MethodReturnType``).
        """
        if self.__model_to_build__ is not None and issubclass(self.__model_to_build__, BaseModel):
            return self.__model_to_build__.model_validate(
                parsing_result,
                context=await self.get_full_context(response),
            )

        raise NotImplementedError(
            f"{self.__class__.__name__} must either define a BaseModel in '__model_to_build__' "
            f"or override 'transform_result'. "
            f"Currently, '__model_to_build__' is {self.__model_to_build__}, and "
            f"'transform_result' has not been overridden.",
        )

    async def to_obj(self, response: RawResponse[Any]) -> MethodReturnType:
        parsing_result = await self.parse_result(response)
        return await self.transform_result(parsing_result, response)

    async def get_full_context(
        self,
        response: RawResponse[Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        context = context or {}
        context_from_response: dict[str, Any] = {}
        self_context = await self.get_context(response.executed_as)

        if 'date' in response.headers:
            context_from_response['response_timestamp'] = parsedate_to_datetime(
                response.headers['date'],
            ).timestamp()

        return self_context | context_from_response | context | {'bot': response.executed_as}

    async def _resolve_callable_field_value(self, value: R | CallableField[R], bot: Bot) -> R:
        if not callable(value):
            return value

        result = value(self, bot)
        if inspect.isawaitable(result):
            return await result
        return result

    async def get_url(self, bot: Bot) -> str:
        return await self._resolve_callable_field_value(self.url, bot)

    async def get_headers(self, bot: Bot) -> dict[str, str]:
        return await self._resolve_callable_field_value(self.headers, bot)

    async def get_data(self, bot: Bot) -> dict[str, Any]:
        return await self._resolve_callable_field_value(self.data, bot)

    async def get_context(self, bot: Bot) -> dict[str, Any]:
        return await self._resolve_callable_field_value(self.context, bot)

    async def execute(self, as_: Bot) -> Response[MethodReturnType]:
        """
        Execute method as bot and return result.

        :param as_: Bot instance to execute.
        """
        return await as_.make_request(self)
