from __future__ import annotations


__all__ = ['GetOfferFields']


from typing import Any
from funpayparsers.parsers import OfferFieldsParser

from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.offers import OfferFields
from funpaybotengine.client.session import HTTPMethod


def gen_data(m: GetOfferFields, *_: Any) -> dict[str, Any]:
    if m.subcategory_type is SubcategoryType.OFFERS:
        return {'offer': m.offer_id} if m.offer_id is not None else {'node': m.subcategory_id}
    return {}


class GetOfferFields(FunPayMethod[OfferFields]):
    """
    Get offer fields method.

    Returns ``funpaybotengine.types.pages.OrderPage`` obj.
    """

    url = lambda m, *_: \
        'logs/offerEdit' if m.subcategory_type is SubcategoryType.OFFERS else f'chips/{m.subcategory_id}/trade'
    method = HTTPMethod.GET
    data = gen_data
    parser_cls = OfferFieldsParser
    model_to_build = OfferFields

    subcategory_type: SubcategoryType
    subcategory_id: int
    offer_id: int | None = None
