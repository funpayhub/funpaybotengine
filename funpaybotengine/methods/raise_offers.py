from __future__ import annotations


__all__ = ('RaiseOffers',)

import json
from typing import TYPE_CHECKING, Any, cast
from collections.abc import Sequence

from pydantic import Field
from typing_extensions import Annotated

from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.common import RaiseOffersResponse
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class RaiseOffers(FunPayMethod[RaiseOffersResponse]):
    category_id: int
    subcategory_ids: Annotated[Sequence[int], Field(min_length=1)]
    __model_to_build__ = RaiseOffersResponse

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

    async def parse_result(self, response: RawResponse[bool]) -> dict[str, Any]:
        data = json.loads(response.raw_response)
        return {'raw_source': response.raw_response} | cast(dict[str, Any], data)
