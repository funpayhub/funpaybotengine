from __future__ import annotations


__all__ = ('RaiseOffers',)

import re
import json
from typing import TYPE_CHECKING

from pydantic import Field
from typing_extensions import Literal, Annotated

from funpaybotengine.exceptions import RaiseOffersError
from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


def parse_wait_time(response: str) -> int:
    x = re.search(r'(\d+)', response)
    time = int(x.group()) if x else 0

    if 'секунд' in response or 'second' in response:
        return time or 2
    if 'минут' in response or 'хвилин' in response or 'minute' in response:
        return (time - 1 if time else 1) * 60
    if 'час' in response or 'годин' in response or 'hour' in response:
        return int((time - 0.5 if time else 1) * 3600)
    return 10


class RaiseOffers(FunPayMethod[Literal[True]]):
    category_id: int
    subcategory_ids: Annotated[list[int], Field(min_length=1)]

    def __init__(
        self,
        category_id: int,
        subcategory_ids: list[int],
        locale: Language | None = None,
    ):
        super().__init__(
            url='lots/raise',
            method=HTTPMethod.POST,
            locale=locale,
            data={
                'game_id': category_id,
                'node_id': subcategory_ids[0],
                'node_ids[]': subcategory_ids,
            },
            headers={'x-requested-with': 'XMLHttpRequest'},
            category_id=category_id,
            subcategory_ids=subcategory_ids,
        )

    async def parse_result(self, response: RawResponse[bool]) -> Literal[True]:
        data = json.loads(response.raw_response)
        error, url, msg = data.get('error'), data.get('url'), data.get('msg')

        if url:
            raise RaiseOffersError(response.raw_response, self.category_id, url, None)

        if error:
            if msg:
                if any(_ in msg for _ in ('Подождите ', 'Please wait ', 'Зачекайте ')):
                    wait = parse_wait_time(msg)
                else:
                    wait = None
                raise RaiseOffersError(response.raw_response, self.category_id, msg, wait)
            raise RaiseOffersError(response.raw_response, self.category_id, msg, None)
        return True

    async def transform_result(
        self,
        parsing_result: Literal[True],
        response: RawResponse[bool],
    ) -> Literal[True]:
        return True
