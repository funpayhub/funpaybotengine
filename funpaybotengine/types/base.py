from __future__ import annotations


__all__ = ('FunPayObject', 'FunPayMutableObject')

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, PrivateAttr, model_validator

from funpaybotengine.base import BindableObject


class FunPayObject(BindableObject, BaseModel):
    """Base class for all FunPay-parsed objects."""

    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
        validate_default=True,
        from_attributes=True,
    )

    raw_source: str
    """
    Raw source of an object.
    Typically a HTML string, but in rare cases can be a JSON string.
    """

    _cache_: dict[str, Any] = PrivateAttr(default_factory=dict)

    @model_validator(mode='before')
    @classmethod
    def _add_raw_source(cls, data: Any) -> Any:
        if isinstance(data, dict) and 'raw_source' not in data:
            data['raw_source'] = json.dumps(data)
        return data


class FunPayMutableObject(FunPayObject, BaseModel):
    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )
