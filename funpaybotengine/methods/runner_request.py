from __future__ import annotations


__all__ = ['RunnerRequest']

import json
from typing import TYPE_CHECKING, Any, Literal, Annotated
from collections.abc import Sequence

from pydantic import Field
from funpayparsers.parsers import UpdatesParser
from funpayparsers.types.updates import RunnerResponse as PRunnerResponse

from funpaybotengine.types import RunnerResponse
from funpaybotengine.exceptions import RunnerRequestError
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.requests import Action, RequestableObject
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse
    from funpaybotengine.client.bot import Bot


async def make_data(method: RunnerRequest, bot: Bot) -> dict[str, str]:
    return {
        'objects': json.dumps(
            [await i.as_data_dict(bot) for i in method.objects_to_request]
            if method.objects_to_request
            else 'false',
        ),
        'request': method.action.model_dump_json(exclude_none=True, by_alias=True)
        if method.action
        else 'false',
    }


class RunnerRequest(FunPayMethod[RunnerResponse]):
    """
    Get info from runner (``https://funpay.com/runner``).

    Returns ``funpaybotengine.types.UpdatesPack`` obj.
    """

    url = 'runner/'
    method = HTTPMethod.POST
    data = make_data
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    parser_cls = UpdatesParser
    model_to_build = RunnerResponse

    objects_to_request: Annotated[Sequence[RequestableObject], Field(min_length=1, max_length=10)] | Literal[False] = False
    action: Action | Literal[False] = False

    async def transform_result(
        self,
        parsing_result: PRunnerResponse,
        response: RawResponse[Any],
    ) -> RunnerResponse:
        result: RunnerResponse = await super().transform_result(parsing_result, response)
        if result.response and result.response.error:
            raise RunnerRequestError(result)
        return result
