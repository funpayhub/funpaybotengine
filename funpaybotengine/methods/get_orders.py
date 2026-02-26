from __future__ import annotations


__all__ = ('GetOrders',)

import json
from typing import Any

from pydantic import Field, BaseModel
from funpayparsers.types import Language

from funpaybotengine.client import RawResponse
from funpaybotengine.types.pages import OfferPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetOrders(FunPayMethod[str], BaseModel):
    order_ids: list[str] = Field(min_length=1, max_length=10)
    include_users: bool = True
    include_reviews: bool = True
    include_details: bool = True

    __model_to_build__ = OfferPage

    def __init__(
        self,
        order_ids: list[str],
        include_users: bool = True,
        include_reviews: bool = True,
        include_details: bool = True,
        locale: Language | None = None,
    ) -> None:
        include = []
        if include_users:
            include.append('users')
        if include_reviews:
            include.append('review')
        if include_details:
            include.append('details')

        data = {'order_uids': order_ids, 'include': include}

        super().__init__(
            url='api/orders/get',
            data=json.dumps(data),
            method=HTTPMethod.POST,
            parser_cls=None,
            order_ids=order_ids,
            include_users=include_users,
            include_reviews=include_reviews,
            include_details=include_details,
            locale=locale,
            headers={'Content-Type': 'application/json', 'Accept-Language': 'ru'},
        )

    async def parse_result(self, response: RawResponse[Any]) -> Any:
        return json.loads(response.raw_response)

    async def transform_result(self, parsing_result: Any, response: RawResponse[Any]) -> Any:
        return parsing_result
