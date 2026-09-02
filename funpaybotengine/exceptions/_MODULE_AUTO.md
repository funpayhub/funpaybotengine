# exceptions/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## action_exceptions.py
```
__all__ = ['RefundError', 'RaiseOffersError']

cls RefundError(FunPayBotEngineError)
  __init__(order_id: str, message: str)

cls RaiseOffersError(FunPayBotEngineError)
  __init__(response: str, category_id: int, message: str?) -> None
  parse_wait_time(response: str) -> int
  wait_time() -> int

```

## base.py
```
__all__ = ('FunPayBotEngineError',)

cls FunPayBotEngineError(Exception)
  __init__(*args: Any) -> None

```

## bot_exceptions.py
```
__all__ = ('BotNotBoundError', 'BotNotInitializedError', 'BotUnauthenticatedError', 'UserBannedError')

cls BotNotBoundError(FunPayBotEngineError, RuntimeError)
  __init__(obj: Any) -> None

cls BotNotInitializedError(FunPayBotEngineError, RuntimeError)
  __init__(bot: Bot) -> None

cls BotUnauthenticatedError(FunPayBotEngineError, RuntimeError)
  __init__() -> None

cls UserBannedError(FunPayBotEngineError, RuntimeError)
  __init__() -> None

```

## message_check_errors.py
```
__all__ = ('MessageTextTooLongError', 'MessageWordTooLongError', 'TooManyLinesError')

cls MessageTextError(FunPayBotEngineError, ValueError)
  __init__(message_text: str)

cls MessageTextTooLongError(MessageTextError)

cls MessageWordTooLongError(MessageTextError)

cls TooManyLinesError(MessageTextError)

```

## method_exceptions.py
```
__all__ = ['MethodError', 'InvalidOfferFieldsError']

cls MethodError(FunPayBotEngineError)

cls InvalidOfferFieldsError(MethodError)
  __init__(message: str, fields: dict[str, str]? = None)

```

## runner_exceptions.py
```
__all__ = ['RunnerRequestError']

cls RunnerRequestError(FunPayBotEngineError)
  __init__(runner_response: RunnerResponse)

```

## session_exceptions.py
```
__all__ = …

cls FunPayRequestError(FunPayBotEngineError)
  __init__(method: FunPayMethod[Any]) -> None

cls BannedError(FunPayRequestError)

cls UnexpectedHTTPStatusError(FunPayRequestError)
  __init__(method: FunPayMethod[Any], status: int)

cls RateLimitExceededError(UnexpectedHTTPStatusError)
  __init__(method: FunPayMethod[Any])

cls UnauthorizedError(UnexpectedHTTPStatusError)
  __init__(method: FunPayMethod[Any])

cls ForbiddenError(UnexpectedHTTPStatusError)
  __init__(method: FunPayMethod[Any])

cls BadRequestError(UnexpectedHTTPStatusError)
  __init__(method: FunPayMethod[Any])

cls NotFoundError(UnexpectedHTTPStatusError)
  __init__(method: FunPayMethod[Any])

cls FunPayServerError(UnexpectedHTTPStatusError)
  __init__(method: FunPayMethod[Any], status: int = 500)

```
