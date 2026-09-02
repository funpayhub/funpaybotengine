# session/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## aiohttp_session.py
```
__all__ = ('AioHttpSession',)

cls AioHttpSession(BaseSession)
  __init__(proxy: str? = None, default_headers: dict[str, str]? = None)
  async session() -> ClientSession
  async close() -> None
  prepare_cookies(session: ClientSession, bot: Bot, skip_session_cookies: bool = False) -> None
  async make_request(method: FunPayMethod[MethodReturnType], bot: Bot, timeout: float? = None, skip_session_cookies: bool = False) -> Response[MethodReturnType]
  async resolve_url(method: FunPayMethod[Any], bot: Bot, session: ClientSession) -> str
  proxy() -> str | None

```

## base.py
```
__all__ = ('BaseSession', 'RawResponse', 'Response')
ResponseObject = TypeVar('ResponseObject', bound=Any)

cls RawResponse(Generic[ResponseObject]): url: str, status_code: HTTPStatus | int, raw_response: str, headers: dict[str, str], cookies: dict[str, str], method_obj: FunPayMethod[ResponseObject], context: dict[str, Any], executed_as: Bot
  locale() -> str

cls Response(RawResponse[ResponseObject], Generic[ResponseObject]): response_obj: ResponseObject
  from_raw_response(raw: RawResponse[ResponseObject], response_obj: ResponseObject) -> Response[ResponseObject]

cls BaseSession(ABC)
  # Base session.
  async close() -> None
  async make_request(method: FunPayMethod[MethodReturnType], bot: Bot, timeout: float? = None, skip_session_cookies: bool = False) -> Response[MethodReturnType]
  check_status_code(method: FunPayMethod[Any], status_code: int | HTTPStatus) -> None
    # Checks the response's status code and raises an exception if it is not in the

```

## http_methods.py
```
__all__ = ('HTTPMethod',)

cls HTTPMethod(Enum): CONNECT, DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT, TRACE

```
