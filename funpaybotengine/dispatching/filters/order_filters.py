from __future__ import annotations


__all__ = ('FinalOrderStatusFilter',)


from typing import TYPE_CHECKING, Any

from funpaybotengine.types.enums import MessageType, OrderStatus
from funpaybotengine.dispatching.events.builtin_events import NewMessage

from .base import Filter


if TYPE_CHECKING:
    from funpaybotengine.dispatching.events.base import Event
    from funpaybotengine.dispatching.events.builtin_events import OrderEvent


_message_type_to_order_status_mapping = {
    MessageType.NEW_ORDER: OrderStatus.PAID,
    MessageType.ORDER_CLOSED: OrderStatus.COMPLETED,
    MessageType.ORDER_CLOSED_BY_ADMIN: OrderStatus.COMPLETED,
    MessageType.ORDER_REFUNDED: OrderStatus.REFUNDED,
    MessageType.ORDER_PARTIALLY_REFUNDED: OrderStatus.REFUNDED,
    MessageType.ORDER_REOPENED: OrderStatus.PAID,
}


class FinalOrderStatusFilter(Filter):
    def __init__(self, status: OrderStatus, /):
        super().__init__()
        self.order_status = status

    async def __call__(self, event: OrderEvent, events_stack: list[Event[Any]]) -> bool:
        order_id = event.object.meta.order_id
        if not order_id:
            return False

        curr_status: OrderStatus | None = None

        for i in events_stack:
            if not isinstance(i, NewMessage):
                continue

            if i.object.meta.type not in _message_type_to_order_status_mapping:
                continue

            curr_status = _message_type_to_order_status_mapping[i.object.meta.type]

        if curr_status is None:
            return False

        return curr_status == self.order_status
