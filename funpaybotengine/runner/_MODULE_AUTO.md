# runner/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## config.py
```
__all__ = ('RunnerConfig', 'BackoffConfig', 'Backoff')

cls BackoffConfig: min_delay: float, max_delay: float, factor: float

cls RunnerConfig: interval: int | float, discover_sales: bool, discover_purchases: bool, keep_unread: bool, on_unauthenticated_error_policy: Literal['ignore', 'event', 'stop'], backoff_config: BackoffConfig

cls Backoff
  __init__(config: BackoffConfig) -> None
  min_delay() -> float
  max_delay() -> float
  factor() -> float
  next_delay() -> float
  current_delay() -> float
  counter() -> int
  async asleep() -> None
  reset() -> None

```

## event_collector.py
```
CHAT_EVENTS = ChatChangedEvent | NewMessageEvent
F = TypeVar('F', bound=Callable[..., Any])

cls EventsPack
  __init__(timestamp: int | float) -> None
  chainmap() -> ChainMap[NewMessageEvent, OrderEvent | ReviewEvent | None]
  total_events() -> list[RunnerEvent[Any]]
  add_chat_event(event: ChatChangedEvent) -> None
  add_message_event() -> None

cls EventCollector
  # Collects updates from FunPay and transforms them into update objects
  __init__(bot: Bot, config: RunnerConfig, *, session_storage: Storage? = None) -> None
  async get_chat_histories(chat_ids: list[int]) -> dict[int, list[Message]]
  async init_chats() -> None
  async get_chat_changed_events() -> EventsPack | None
  async get_new_message_events(total: EventsPack) -> None
  async resolve_unknown_order_related_event(total: EventsPack, unknown: NewMessageEvent, sale_previews: dict[str, OrderPreview], purchase_previews: dict[str, OrderPreview]) -> None
  async make_order_events(total: EventsPack) -> None
  async get_events() -> list[RunnerEvent[Any]]

attempts(amount: int = 0) -> Callable[[F], F]

```

## runner.py
```
__all__ = ('Runner', 'EventsStack')

cls EventsStack: events: tuple[RunnerEvent[Any] | BotEngineEvent[Any], ...], data: dict[Any, Any], id: str
  get(value: str, fallback: Any = None) -> Any

cls Runner
  __init__(bot: Bot)
  bot() -> Bot
  async listen(config: RunnerConfig? = None, session_storage: Storage? = None) -> AsyncGenerator[tuple[RunnerEvent[Any], EventsStack], None]

async _sleep(start_time: int | float, interval: int | float) -> None

```
