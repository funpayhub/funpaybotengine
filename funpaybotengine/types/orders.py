from __future__ import annotations


__all__ = ('OrderPreview', 'OrderPreviewsBatch')


from typing import Any

from pydantic import BaseModel, PrivateAttr, computed_field

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import OrderStatus, OrderPreviewType
from funpaybotengine.types.common import MoneyValue, UserPreview


class OrderPreview(FunPayObject, BaseModel):
    """Represents an order preview."""

    def model_post_init(self, context: dict[Any, Any]) -> None:
        super().model_post_init(context)
        if context and context.get('order_preview_type') is not None:
            self._type = context['order_preview_type']

    id: str
    """Order ID."""

    date_text: str
    """Order date (as human-readable text)."""

    title: str
    """Order title."""

    category_text: str
    """Order category and subcategory text."""

    status: OrderStatus
    """Order status."""

    total: MoneyValue
    """Order total."""

    counterparty: UserPreview
    """Associated counterparty info."""

    _type: OrderPreviewType = PrivateAttr(OrderPreviewType.UNKNOWN)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def type(self) -> OrderPreviewType:
        return self._type


class OrderPreviewsBatch(FunPayObject):
    """
    Represents a single batch of order previews.

    This batch contains a portion of all available order previews (typically 100),
    along with metadata required to fetch the next batch.
    """

    orders: tuple[OrderPreview, ...]
    """List of order previews included in this batch."""

    next_order_id: str | None
    """
    ID of the next order to use as a cursor for pagination.

    If present, this value should be included in the next request to fetch the 
    following batch of order previews. 

    If ``None``, there are no more orders to load.
    """

    _type: OrderPreviewType = PrivateAttr(OrderPreviewType.UNKNOWN)
    _order_id_filter: str | None = PrivateAttr(None)
    _buyer_username_filter: str | None = PrivateAttr(None)
    _status_filter: OrderStatus | str | None = PrivateAttr(None)
    _game_id_filter: int | None = PrivateAttr(None)
    _other_filters: dict[str, str] | None = PrivateAttr(None)

    def model_post_init(self, context: dict[Any, Any]) -> None:
        super().model_post_init(context)
        self._order_id_filter = context.get('order_id_filter')
        self._buyer_username_filter = context.get('buyer_username_filter')
        self._status_filter = context.get('status_filter')
        self._game_id_filter = context.get('game_id_filter')
        self._other_filters = context.get('other_filters')
        self._type = context.get('order_preview_type', OrderPreviewType.UNKNOWN)

    async def next_batch(self) -> OrderPreviewsBatch:
        if not self.next_order_id:
            raise ValueError('Last batch.')
        if self.type is OrderPreviewType.UNKNOWN:
            raise ValueError('Unknown type')

        if self.type == OrderPreviewType.SALE:
            method = self.get_bound_bot().get_sales
        else:
            method = self.get_bound_bot().get_purchases

        return await method(
            from_order_id=self.next_order_id,
            order_id_filter=self.order_id_filter,
            buyer_username_filter=self.buyer_username_filter,
            status_filter=self.status_filter,
            game_id_filter=self.game_id_filter,
            other_filters=self.other_filters,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def order_id_filter(self) -> str | None:
        return self._order_id_filter

    @computed_field  # type: ignore[prop-decorator]
    @property
    def buyer_username_filter(self) -> str | None:
        return self._buyer_username_filter

    @computed_field  # type: ignore[prop-decorator]
    @property
    def status_filter(self) -> OrderStatus | str | None:
        return self._status_filter

    @computed_field  # type: ignore[prop-decorator]
    @property
    def game_id_filter(self) -> int | None:
        return self._game_id_filter

    @computed_field  # type: ignore[prop-decorator]
    @property
    def other_filters(self) -> dict[str, str] | None:
        return self._other_filters

    @computed_field  # type: ignore[prop-decorator]
    @property
    def type(self) -> OrderPreviewType:
        return self._type
