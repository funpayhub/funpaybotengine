from __future__ import annotations


__all__ = ('GetSales',)

from pydantic import BaseModel
from funpayparsers.types import Language
from funpayparsers.parsers import OrderPreviewsParser

from funpaybotengine.types import OrderPreviewsBatch
from funpaybotengine.types.enums import OrderStatus, OrderPreviewType
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


STATE_FILTERS = {
    OrderStatus.COMPLETED: 'closed',
    OrderStatus.PAID: 'paid',
    OrderStatus.REFUNDED: 'refunded',
}


class GetSales(FunPayMethod[OrderPreviewsBatch], BaseModel):
    """
    Get a sales list (``https://funpay.com/orders/trade``).

    Returns ``funpaybotengine.types.OrderPreviewsBatch`` obj.
    """

    from_order_id: str | None = None
    order_id_filter: str | None = None
    buyer_username_filter: str | None = None
    status_filter: OrderStatus | str | None = None
    game_id_filter: int | None = None
    other_filters: dict[str, str] | None = None

    __model_to_build__ = OrderPreviewsBatch

    def __init__(
        self,
        from_order_id: str | None = None,
        order_id_filter: str | None = None,
        buyer_username_filter: str | None = None,
        status_filter: OrderStatus | str | None = None,
        game_id_filter: str | None = None,
        other_filters: dict[str, str] | None = None,
        locale: Language | None = None,
    ):
        url = self._construct_url(
            order_id_filter=order_id_filter,
            buyer_username_filter=buyer_username_filter,
            status_filter=status_filter,
            game_id_filter=game_id_filter,
            other_filters=other_filters,
        )

        super().__init__(
            url=url,
            method=HTTPMethod.POST,
            parser_cls=OrderPreviewsParser,
            data={'continue': from_order_id} if from_order_id is not None else {},
            locale=locale,
            context={
                'order_preview_type': OrderPreviewType.SALE,
                'order_id_filter': order_id_filter,
                'buyer_username_filter': buyer_username_filter,
                'status_filter': status_filter,
                'game_id_filter': game_id_filter,
                'other_filters': other_filters,
            },
            from_order_id=from_order_id,
            order_id_filter=order_id_filter,
            buyer_username_filter=buyer_username_filter,
            status_filter=status_filter,
            game_id_filter=game_id_filter,
            other_filters=other_filters,
        )

    def _construct_url(
        self,
        order_id_filter: str | None = None,
        buyer_username_filter: str | None = None,
        status_filter: OrderStatus | str | None = None,
        game_id_filter: str | None = None,
        other_filters: dict[str, str] | None = None,
    ) -> str:
        url = 'orders/trade'

        queries = []
        if order_id_filter is not None:
            queries.append(f'id={order_id_filter}')
        if buyer_username_filter is not None:
            queries.append(f'buyer={buyer_username_filter}')
        if status_filter is not None:
            if isinstance(status_filter, str):
                queries.append(f'state={status_filter}')
            else:
                queries.append(f'state={STATE_FILTERS[status_filter]}')
        if game_id_filter is not None:
            queries.append(f'game_id={game_id_filter}')

        if other_filters:
            for k, v in other_filters.items():
                queries.append(f'{k}={v}')

        if not queries:
            return url

        query = '&'.join(queries)
        return url + '?' + query
