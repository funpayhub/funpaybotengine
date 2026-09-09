from __future__ import annotations


__all__ = ['CalcLots']

import json
from typing import TYPE_CHECKING, Any

from funpaybotengine.types.calc import CalcResult
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse


class CalcLots(FunPayMethod[CalcResult]):
    url = 'lots/calc'
    method = HTTPMethod.POST
    data = lambda m, *_: {'nodeId': m.subcategory_id, 'price': m.price}
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    model_to_build = CalcResult

    subcategory_id: int
    price: float

    async def parse_result(self, response: RawResponse[CalcResult]) -> dict[str, Any]:
        return json.loads(response.raw_response)  # type: ignore # always dict
