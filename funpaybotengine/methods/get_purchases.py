from __future__ import annotations


__all__ = ['GetPurchases']

from typing import Any

from funpayparsers.parsers import OrderPreviewsParser

from funpaybotengine.types import OrderPreviewsBatch
from funpaybotengine.types.enums import OrderType, OrderStatus
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


STATE_FILTERS = {
    OrderStatus.COMPLETED: 'closed',
    OrderStatus.PAID: 'paid',
    OrderStatus.REFUNDED: 'refunded',
}


def _construct_url(m: GetPurchases, *_: Any) -> str:
    url = 'orders/'

    queries = []
    if m.order_id_filter is not None:
        queries.append(f'id={m.order_id_filter}')
    if m.seller_username_filter is not None:
        queries.append(f'buyer={m.seller_username_filter}')
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


class GetPurchases(FunPayMethod[OrderPreviewsBatch]):
    """
    Get a purchases list (``https://funpay.com/orders/``).

    Returns ``funpaybotengine.types.OrderPreviewsBatch`` obj.
    """

    url = _construct_url
    method = HTTPMethod.POST
    data = lambda m, *_: {'continue': m.from_order_id} if m.from_order_id is not None else {}
    context = {'order_preview_type': OrderType.PURCHASE}
    parser_cls = OrderPreviewsParser
    model_to_build = OrderPreviewsBatch

    from_order_id: str | None = None
    order_id_filter: str | None = None
    seller_username_filter: str | None = None
    status_filter: OrderStatus | str | None = None
    game_id_filter: int | None = None
    other_filters: dict[str, str] | None = None
