from __future__ import annotations


__all__ = ('FieldCondition', 'SubcategoryFieldDef', 'SubcategoryStructure')


import json
from dataclasses import asdict
from typing import TYPE_CHECKING, Any
from functools import cached_property

from pydantic import BaseModel, Field, field_validator, model_validator
from funpayparsers.types.enums import SubcategoryFieldType

from funpaybotengine.types.base import FunPayObject


if TYPE_CHECKING:
    from funpaybotengine.types.offers import OfferFields


class FieldCondition(FunPayObject, BaseModel):
    """
    Represents a visibility condition for a ``SubcategoryFieldDef``.

    The owning field is shown only when the field identified by ``field_id``
    has one of the values listed in ``values``.
    """

    field_id: str
    """ID of the field whose value controls visibility of the owning field."""

    values: set[str]
    """
    Values of ``field_id`` that make the owning field visible.

    Sourced from the ``list`` key in the ``data-fields`` JSON condition object.
    Stored as a ``set`` — duplicates are not possible by definition.

    Values are compared case-insensitively in :meth:`is_satisfied_by`,
    because FunPay's public listing page and the ``offerEdit`` form render
    the same underlying value with inconsistent casing.
    """

    @model_validator(mode='before')
    @classmethod
    def _add_raw_source(cls, data: Any) -> Any:
        # funpayparsers.FieldCondition has no raw_source — convert to dict first
        if not isinstance(data, dict):
            data = asdict(data)
        if 'raw_source' not in data:
            data['raw_source'] = json.dumps({'field_id': data.get('field_id')})
        return data

    @field_validator('values', mode='after')
    @classmethod
    def _casefold_values(cls, value: set[str]) -> set[str]:
        return {str(v).casefold() for v in value}

    def is_satisfied_by(self, value: Any) -> bool:
        """Return ``True`` if *value* (case-insensitively) is present in ``values``."""
        return str(value).casefold() in self.values


class SubcategoryFieldDef(FunPayObject, BaseModel):
    """Represents a single field definition within a subcategory."""

    id: str
    """Field identifier as used by FunPay (e.g. ``'arena'``, ``'quantity'``)."""

    type: SubcategoryFieldType
    """Field type."""

    label: str
    """Human-readable label from ``label.control-label`` in the form HTML."""

    conditions: list[FieldCondition]
    """
    Visibility conditions.

    Empty list means the field is always visible.
    The field is shown only when all conditions are satisfied simultaneously.
    """

    options: list[str] | None
    """
    Available option values for ``SELECT`` and ``DROPDOWN`` type fields.

    ``None`` for non-select fields (``NUMERIC_RANGE``, ``TEXT``, ``TEXTAREA``, ``IMAGES``).
    """

    @model_validator(mode='before')
    @classmethod
    def _add_raw_source(cls, data: Any) -> Any:
        # funpayparsers.SubcategoryFieldDef has raw_source — let from_attributes handle it
        if not isinstance(data, dict):
            return data
        if 'raw_source' not in data:
            data['raw_source'] = json.dumps({
                'id': data.get('id'),
                'label': data.get('label'),
            })
        return data


class SubcategoryStructure(FunPayObject, BaseModel):
    """
    Derived subcategory field structure for quick lookups.

    Not parsed directly from HTML — constructed from ``OfferFields.field_schema``
    via the ``OfferFields.subcategory_structure`` property.
    """

    subcategory_id: int | None
    """Subcategory ID. ``None`` for currency (chips) offer fields."""

    fields: dict[str, SubcategoryFieldDef] = Field(default_factory=dict)
    """
    Field definitions keyed by field ID, in declaration order.

    Use ``fields[field_id]`` for O(1) lookup by ID,
    or iterate over ``fields.values()`` to process fields in declaration order.
    """

    @model_validator(mode='before')
    @classmethod
    def _add_raw_source(cls, data: Any) -> Any:
        # SubcategoryStructure is not parsed from HTML — generate a stable raw_source
        if not isinstance(data, dict):
            return data
        if 'raw_source' not in data:
            data['raw_source'] = json.dumps({'subcategory_id': data.get('subcategory_id')})
        return data

    @cached_property
    def label_map(self) -> dict[str, list[str]]:
        """
        Mapping from FunPay label to list of field IDs for reverse lookup.

        Values are lists because different fields may share the same label
        (notably empty labels on fields that have no ``<label>`` in the form).
        Field IDs appear in declaration order.
        """
        result: dict[str, list[str]] = {}
        for f in self.fields.values():
            result.setdefault(f.label, []).append(f.id)
        return result

    @cached_property
    def lower_label_map(self) -> dict[str, list[str]]:
        """Case-insensitive variant of ``label_map`` — keys are lowercased."""
        result: dict[str, list[str]] = {}
        for label, ids in self.label_map.items():
            result.setdefault(label.lower(), []).extend(ids)
        return result

    @classmethod
    def from_offer_fields(cls, offer_fields: OfferFields) -> SubcategoryStructure:
        """
        Build a ``SubcategoryStructure`` from engine ``OfferFields``.

        :param offer_fields: An ``OfferFields`` instance returned by ``GetOfferFields``.
        :return: A ``SubcategoryStructure`` with field map and label maps populated.
        """
        return cls(
            raw_source=json.dumps({'subcategory_id': offer_fields.subcategory_id}),
            subcategory_id=offer_fields.subcategory_id,
            fields={f.id: f for f in offer_fields.field_schema},
        )
