from __future__ import annotations


__all__ = ['GetSales']


from typing import Any
from funpayparsers.parsers import OrderPreviewsParser

from funpaybotengine.types import OrderPreviewsBatch
from funpaybotengine.types.enums import OrderStatus, OrderType
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


STATE_FILTERS = {
    OrderStatus.COMPLETED: 'closed',
    OrderStatus.PAID: 'paid',
    OrderStatus.REFUNDED: 'refunded',
}


def _construct_url(m: GetSales, *_: Any) -> str:
    url = 'orders/trade'

    queries = []
    if m.order_id_filter is not None:
        queries.append(f'id={m.order_id_filter}')
    if m.buyer_username_filter is not None:
        queries.append(f'buyer={m.buyer_username_filter}')
    if m.status_filter is not None:
        if isinstance(m.status_filter, str):
            queries.append(f'state={m.status_filter}')
        else:
            queries.append(f'state={STATE_FILTERS[m.status_filter]}')
    if m.game_id_filter is not None:
        queries.append(f'game_id={m.game_id_filter}')

    if m.other_filters:
        for k, v in m.other_filters.items():
            queries.append(f'{k}={v}')

    if not queries:
        return url

    return url + '?' + '&'.join(queries)


class GetSales(FunPayMethod[OrderPreviewsBatch]):
    """
    Get a sales list (``https://funpay.com/orders/trade``).

    Returns ``funpaybotengine.types.OrderPreviewsBatch`` obj.
    """
    url = _construct_url
    method = HTTPMethod.POST
    data = lambda m, *_: {'continue': m.from_order_id} if m.from_order_id is not None else {}
    context = lambda m, *_: {
        'order_preview_type': OrderType.SALE,
        'order_id_filter': m.order_id_filter,
        'buyer_username_filter': m.buyer_username_filter,
        'status_filter': m.status_filter,
        'game_id_filter': m.game_id_filter,
        'other_filters': m.other_filters,
    }
    parser_cls = OrderPreviewsParser
    model_to_build = OrderPreviewsBatch

    from_order_id: str | None = None
    order_id_filter: str | None = None
    buyer_username_filter: str | None = None
    status_filter: OrderStatus | str | None = None
    game_id_filter: int | None = None
    other_filters: dict[str, str] | None = None
