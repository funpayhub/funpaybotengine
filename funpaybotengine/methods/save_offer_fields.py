from __future__ import annotations


__all__ = ('SaveOfferFields',)

import json
from typing import Any

from pydantic import BaseModel
from funpayparsers.types import Language
from funpayparsers.parsers import OfferFieldsParser

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.offers import OfferFields
from funpaybotengine.client.session import HTTPMethod, RawResponse
from funpaybotengine.exceptions.method_exceptions import InvalidOfferFieldsError


class SaveOfferFields(FunPayMethod[bool], BaseModel):
    """
    Get offer fields method.

    Returns ``funpaybotengine.types.pages.OrderPage`` obj.
    """

    offer_fields: OfferFields

    def __init__(
        self,
        offer_fields: OfferFields,
        locale: Language | None = None,
    ):
        url = 'chips/saveOffers' if 'chip' in offer_fields.fields_dict else 'lots/offerSave'
        super().__init__(
            url=url,
            method=HTTPMethod.POST,
            data=offer_fields.fields_dict,
            headers={'X-Requested-With': 'XMLHttpRequest'},
            parser_cls=OfferFieldsParser,
            locale=locale,
            offer_fields=offer_fields,
        )

    async def parse_result(self, response: RawResponse[Any]) -> bool | dict[str, Any]:
        try:
            return json.loads(response.raw_response)
        except json.decoder.JSONDecodeError:
            return True

    async def transform_result(
        self,
        parsing_result: bool | dict[str, Any],
        response: RawResponse[Any]
    ) -> bool:
        if isinstance(parsing_result, bool):
            return parsing_result


        if not parsing_result.get('error'):
            return True

        error_msg = str(parsing_result.get('msg', '')) or str(parsing_result.get('error'))
        fields: list[list[str, str]] = parsing_result.get('errors')
        try:
            fields_dict = dict(fields)
        except Exception:
            fields_dict = {}

        raise InvalidOfferFieldsError(error_msg, fields_dict)
