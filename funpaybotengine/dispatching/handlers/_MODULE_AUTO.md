# handlers/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## handler_manager.py
```
__all__ = ('HandlerManager',)

cls HandlerManager(BaseHandlerManager[FilterType, HandlerType, MiddlewareType, 'Router'])
  __init__(router: 'Router', name: str, event_filter: str?)
  inner_middleware() -> MiddlewareManager
  outer_middleware() -> MiddlewareManager
  manager_outer() -> MiddlewareManager
  manager_inner() -> MiddlewareManager
  handling_process() -> MiddlewareManager

```
