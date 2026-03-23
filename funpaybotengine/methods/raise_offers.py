from __future__ import annotations


__all__ = ('RaiseOffers',)

import json
from typing import TYPE_CHECKING
from collections.abc import Sequence

from pydantic import Field
from typing_extensions import Literal, Annotated

from funpaybotengine.exceptions import RaiseOffersError
from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class RaiseOffers(FunPayMethod[Literal[True]]):
    category_id: int
    subcategory_ids: Annotated[Sequence[int], Field(min_length=1)]

    def __init__(
        self,
        category_id: int,
        subcategory_ids: Sequence[int],
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

        if url or error:
            raise RaiseOffersError(response.raw_response, self.category_id, url or msg)

        return True

    async def transform_result(
        self,
        parsing_result: Literal[True],
        response: RawResponse[bool],
    ) -> Literal[True]:
        return True
