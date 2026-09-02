# funpaybotengine/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## Submodules

- [`client/`](client/_MODULE_AUTO.md) (5 py, 7 cls, 2 fn)
- [`dispatching/`](dispatching/_MODULE_AUTO.md) (8 py, 44 cls, 1 fn)
- [`exceptions/`](exceptions/_MODULE_AUTO.md) (7 py, 23 cls)
- [`methods/`](methods/_MODULE_AUTO.md) (35 py, 35 cls, 5 fn)
- [`runner/`](runner/_MODULE_AUTO.md) (3 py, 7 cls, 2 fn)
- [`storage/`](storage/_MODULE_AUTO.md) (3 py, 4 cls)
- [`types/`](types/_MODULE_AUTO.md) (28 py, 68 cls, 2 fn)

## __init__.py
```
__all__ = ['Bot', 'BaseSession', 'AioHttpSession', 'Router', 'Dispatcher', 'events', 'filters']

```

## base.py
```
__all__ = ('BindableObject', 'check_bound')
F = TypeVar('F', bound=Callable[..., Any])

cls BindableObject(BaseModel)
  model_post_init(context: dict[Any, Any]) -> None
  as_() -> Self
  unbind() -> None
  bind_to() -> None
  bot() -> Bot | None
  get_bound_bot() -> Bot

check_bound(func: F) -> F
  # Decorator for instance methods to ensure the object is bound to any Bot instance.

```

## loggers.py
```
__all__ = ('session_logger', 'router_logger', 'dispatcher_logger', 'runner_logger')
session_logger = getLogger('funpaybotengine.session')
router_logger = getLogger('funpaybotengine.router')
dispatcher_logger = getLogger('funpaybotengine.dispatcher')
runner_logger = getLogger('funpaybotengine.runner')

```

## utils.py
```
__all__ = ('random_runner_tag', 'check_message_text', 'enforce_message_text_whitespaces')

random_runner_tag() -> str
  # Generate a random lowercase string tag used to identify the first request

check_message_text() -> None
  # Checks if a message text meets FunPay rules:

enforce_message_text_whitespaces(enforce_spaces: bool = True, enforce_line_breaks: bool = True) -> str
  # By default, FunPay trims the message text and replaces multiple consecutive spaces

_replace_multiple_spaces(match: re.Match[str]) -> str

_replace_first_space(match: re.Match[str]) -> str

_replace_last_space(match: re.Match[str]) -> str

_replace_line_breaks(match: re.Match[str]) -> str

```
