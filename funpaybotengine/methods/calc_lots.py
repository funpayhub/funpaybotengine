from __future__ import annotations


__all__ = ('CalcLots',)

import json

from pydantic import BaseModel
from typing import TYPE_CHECKING

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod

from funpaybotengine.types.calc import CalcResult

if TYPE_CHECKING:
    from funpaybotengine.client import Bot
    from funpaybotengine.client import RawResponse


class CalcLots(FunPayMethod[list[CalcResult]], BaseModel):
    __model_to_build__ = None

    subcategory_id: int
    price: float

    def __init__(self, subcategory_id: int, price: float) -> None:
        super().__init__(
            url='lots/calc',
            method=HTTPMethod.POST,
            expected_status_codes=[200],
            headers={'X-Requested-With': 'XMLHttpRequest'},
            data={'nodeId': subcategory_id, 'price': price},
            allow_anonymous=False,
            allow_uninitialized=False,
            subcategory_id=subcategory_id,
            price=price,
        )

    async def parse_result(self, response: RawResponse[list[CalcResult]]) -> list[CalcResult]:
        raw_json = json.loads(response.raw_response)

        if "methods" not in raw_json:
            return []

        return CalcResult.model_validate(raw_json)

    async def transform_result(self, parsing_result: list[CalcResult], response: RawResponse[list[CalcResult]]) -> list[CalcResult]:
        return parsing_result

    async def execute(self, as_: Bot) -> list[CalcResult]:
        result = await as_.make_request(self, skip_initialization=True)
        return result.response_obj
