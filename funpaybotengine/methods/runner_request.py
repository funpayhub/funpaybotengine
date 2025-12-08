from __future__ import annotations


__all__ = ('RunnerRequest',)

import json
from typing import TYPE_CHECKING, Any, Literal
from collections.abc import Sequence

from pydantic import BaseModel
from funpayparsers.parsers import UpdatesParser
from funpayparsers.types.updates import RunnerResponse as PRunnerResponse

from funpaybotengine.types import RunnerResponse
from funpaybotengine.exceptions import RunnerRequestError
from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.requests import Action, RequestableObject
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client import RawResponse
    from funpaybotengine.client.bot import Bot


class RunnerRequest(FunPayMethod[RunnerResponse], BaseModel):
    """
    Get info from runner (``https://funpay.com/runner``).

    Returns ``funpaybotengine.types.UpdatesPack`` obj.
    """

    objects_to_request: Sequence[RequestableObject] | Literal[False] = False
    action: Action | Literal[False] = False

    __model_to_build__ = RunnerResponse

    def __init__(
        self,
        objects_to_request: Sequence[RequestableObject] | Literal[False] = False,
        action: Action | Literal[False] = False,
        locale: Language | None = None,
    ):
        if objects_to_request and len(objects_to_request) > 10:
            raise ValueError(f'Too many objects to request ({len(objects_to_request)} > 10).')

        super().__init__(
            url='runner/',
            method=HTTPMethod.POST,
            locale=locale,
            parser_cls=UpdatesParser,
            data=make_data,
            headers={'X-Requested-With': 'XMLHttpRequest'},
            objects_to_request=objects_to_request,
            action=action,
        )

    async def transform_result(
        self,
        parsing_result: PRunnerResponse,
        response: RawResponse[Any],
    ) -> RunnerResponse:
        result: RunnerResponse = await super().transform_result(parsing_result, response)
        if result.response and result.response.error:
            raise RunnerRequestError(result)
        return result


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
