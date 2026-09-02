# events/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## base.py
```
__all__ = …
EventObject = TypeVar('EventObject')

cls Event(EventryEvent, BindableObject, Generic[EventObject])
  event_context_injection() -> dict[str, Any]
  set_flag(flag: Any) -> None
  set_flags(*flags: Any) -> None
  unset_flag(flag: Any) -> None
  unset_flags(*flags: Any) -> None
  has_flag(flag: Any) -> bool
  flags() -> frozenset[Any]
  data() -> MappingProxyType[Any, Any]

cls RunnerEvent(Event[EventObject])
  event_context_injection() -> dict[str, Any]

cls BotEngineEvent(Event[EventObject])

cls ExceptionEvent(BotEngineEvent[Exception])
  event_context_injection() -> dict[str, Any]

cls BotUnauthenticatedEvent(BotEngineEvent[float])
  event_context_injection() -> dict[str, Any]

cls BotAuthenticatedEvent(BotEngineEvent[None])

```

## builtin_events.py
```
__all__ = …

cls NewEventsPack(BotEngineEvent[str])

cls ChatChangedEvent(RunnerEvent[PrivateChatPreview])
  chat_preview() -> PrivateChatPreview
  event_context_injection() -> dict[str, Any]

cls NewMessageEvent(RunnerEvent[Message])
  message() -> Message
  event_context_injection() -> dict[str, Any]

cls FromMessageEvent(NewMessageEvent)
  event_context_injection() -> dict[str, Any]

cls OrderEvent(FromMessageEvent)
  async get_order_preview(update: bool = False) -> OrderPreview

cls SaleEvent(OrderEvent)
  async get_order_preview(update: bool = False) -> OrderPreview

cls PurchaseEvent(OrderEvent)
  async get_order_preview(update: bool = False) -> OrderPreview

cls NewSaleEvent(SaleEvent)

cls SaleStatusChangedEvent(SaleEvent)

cls SaleClosedEvent(SaleStatusChangedEvent)

cls SaleClosedByAdminEvent(SaleClosedEvent)

cls SaleRefundedEvent(SaleStatusChangedEvent)

cls SalePartiallyRefundedEvent(SaleRefundedEvent)

cls SaleReopenedEvent(SaleStatusChangedEvent)

cls NewPurchaseEvent(PurchaseEvent)

cls PurchaseStatusChangedEvent(PurchaseEvent)

cls PurchaseClosedEvent(PurchaseStatusChangedEvent)

cls PurchaseClosedByAdminEvent(PurchaseClosedEvent)

cls PurchaseRefundedEvent(PurchaseStatusChangedEvent)

cls PurchasePartiallyRefundedEvent(PurchaseRefundedEvent)

cls PurchaseReopenedEvent(PurchaseStatusChangedEvent)

cls ReviewEvent(FromMessageEvent)
  async get_order_page(update: bool = False) -> OrderPage
  async get_review(update: bool = False) -> Review | None

cls NewReviewEvent(ReviewEvent)

cls ReviewChangedEvent(ReviewEvent)

cls ReviewDeletedEvent(ReviewEvent)

cls NewReviewResponseEvent(ReviewEvent)

cls ReviewResponseChangedEvent(ReviewEvent)

cls ReviewResponseDeletedEvent(ReviewEvent)

```
