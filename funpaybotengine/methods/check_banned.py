from __future__ import annotations


__all__ = ('CheckBanned',)

from typing import TYPE_CHECKING

from pydantic import BaseModel

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import Bot, Response, RawResponse


class CheckBanned(FunPayMethod[bool], BaseModel):
    __model_to_build__ = None

    def __init__(self) -> None:
        super().__init__(
            url='account/blocked',
            method=HTTPMethod.GET,
            expected_status_codes=[200, 404],
            allow_anonymous=False,
            allow_uninitialized=True,
        )

    async def parse_result(self, response: RawResponse[bool]) -> bool:
        return response.status_code == 200

    async def transform_result(self, parsing_result: bool, response: RawResponse[bool]) -> bool:
        return parsing_result

    async def execute(self, as_: Bot) -> Response[bool]:
        return await as_.make_request(self, skip_update=True)
