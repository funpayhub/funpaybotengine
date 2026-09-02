# routers/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## base.py
```
__all__ = ['Router']

cls Router(BaseRouter)
  __init__(name: str? = None) -> None
  on_event() -> HandlerManager

```

## dispatcher.py
```
__all__ = ('Dispatcher',)

cls Dispatcher(BaseDispatcher, Router)
  __init__(workflow_data: dict[str, Any]? = None)

error_event_factory(event: EventryEvent, exception: Exception) -> ExceptionEvent

```
