from __future__ import annotations


__all__ = ['RaiseOffers']

import json
from typing import TYPE_CHECKING, Any
from collections.abc import Sequence

from pydantic import Field
from typing_extensions import Annotated

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.common import RaiseOffersResponse
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class RaiseOffers(FunPayMethod[RaiseOffersResponse]):
    url = 'lots/raise'
    method = HTTPMethod.POST
    data = lambda m, *_: {
        'game_id': m.game_id,
        'node_id': m.subcategory_ids[0],
        'node_ids[]': m.subcategory_ids,
    }
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    model_to_build = RaiseOffersResponse

    category_id: int
    subcategory_ids: Annotated[Sequence[int], Field(min_length=1)]

    async def parse_result(self, response: RawResponse[bool]) -> dict[str, Any]:
        data = json.loads(response.raw_response)
        return {'raw_source': response.raw_response} | data
