from __future__ import annotations


__all__ = ('CalcChips',)


import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from funpaybotengine.types.calc import CalcResult
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse


class CalcChips(FunPayMethod[CalcResult], BaseModel):
    game_id: int
    price: float

    __model_to_build__ = CalcResult

    def __init__(self, game_id: int, price: float) -> None:
        super().__init__(
            url='chips/calc',
            method=HTTPMethod.POST,
            expected_status_codes=[200],
            headers={'X-Requested-With': 'XMLHttpRequest'},
            data={'game': game_id, 'price': price},
            allow_anonymous=False,
            allow_uninitialized=False,
            game_id=game_id,
            price=price,
        )

    async def parse_result(self, response: RawResponse[CalcResult]) -> dict[str, Any]:
        return json.loads(response.raw_response)  # type: ignore # always dict
