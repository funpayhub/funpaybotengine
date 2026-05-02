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
    from funpaybotengine.types.pages.offer_page import OfferPage


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
        # Parser FieldCondition is a @dataclass — convert to dict first when ingested
        # via model_validate. Since funpayparsers PR #104 it ships its own raw_source;
        # fall back to a synthetic value for older parsers / direct construction.
        if not isinstance(data, dict):
            data = asdict(data)
        if not data.get('raw_source'):
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

    aliases: set[str] = Field(default_factory=set)
    """
    Additional, casefolded label aliases for this field.

    Used to bridge cross-locale label mismatches between the data-fields JSON
    (English IDs), the filter form ``<label>`` (locale-dependent), the
    per-offer ``param-list`` rendering, and ``OrderPage`` data labels.

    Always casefolded — populated via :class:`SubcategoryStructure.add_alias`
    or :class:`SubcategoryStructure.enrich_from_offer`.
    """

    @model_validator(mode='before')
    @classmethod
    def _add_raw_source(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        if not data.get('raw_source'):
            data['raw_source'] = json.dumps({
                'id': data.get('id'),
                'label': data.get('label'),
            })
        return data

    @field_validator('aliases', mode='after')
    @classmethod
    def _casefold_aliases(cls, value: set[str]) -> set[str]:
        return {str(a).casefold() for a in value if a}


class SubcategoryStructure(FunPayObject, BaseModel):
    """
    Derived subcategory field structure for quick lookups.

    Built either from ``OfferFields`` (authenticated ``offerEdit`` page) or
    directly from the public subcategory listing page's ``div.lot-fields``.
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
        # Parser SubcategoryStructure is a @dataclass — convert when ingesting via
        # model_validate. Parser ships its own raw_source since funpayparsers PR #104;
        # we keep a fallback for older parsers / direct construction.
        if not isinstance(data, dict):
            data = asdict(data)
        if not data.get('raw_source'):
            data['raw_source'] = json.dumps({'subcategory_id': data.get('subcategory_id')})
        return data

    @cached_property
    def label_map(self) -> dict[str, list[str]]:
        """
        Mapping from FunPay label (or alias) to list of field IDs for reverse lookup.

        Indexes both ``f.label`` (as-is, possibly localized) and every entry in
        ``f.aliases`` (casefolded). Values are lists because different fields
        may share the same label/alias.
        """
        result: dict[str, list[str]] = {}
        for f in self.fields.values():
            seen: set[str] = set()
            for key in (f.label, *f.aliases):
                if key in seen:
                    continue
                seen.add(key)
                result.setdefault(key, []).append(f.id)
        return result

    @cached_property
    def lower_label_map(self) -> dict[str, list[str]]:
        """Case-insensitive variant of ``label_map`` — keys are casefolded."""
        result: dict[str, list[str]] = {}
        for label, ids in self.label_map.items():
            key = label.casefold()
            existing = result.setdefault(key, [])
            for fid in ids:
                if fid not in existing:
                    existing.append(fid)
        return result

    def lookup_field_id(self, label: str) -> str | None:
        """
        Resolve *label* (case-insensitively) to a single field ID.

        Returns ``None`` if there is no match or the match is ambiguous.
        """
        ids = self.lower_label_map.get(label.casefold())
        if not ids or len(ids) > 1:
            return None
        return ids[0]

    def add_alias(self, field_id: str, alias: str) -> None:
        """Register *alias* for *field_id* and invalidate cached label maps."""
        if field_id not in self.fields or not alias:
            return
        casefolded = alias.casefold()
        if casefolded in self.fields[field_id].aliases:
            return
        self.fields[field_id].aliases.add(casefolded)
        self.__dict__.pop('label_map', None)
        self.__dict__.pop('lower_label_map', None)

    def enrich_from_offer(self, offer: OfferPage) -> SubcategoryStructure:
        """
        Add aliases from an ``OfferPage.fields`` mapping.

        For each ``(label, value)`` in ``offer.fields``:

        * If *label* already resolves via ``label_map`` — leave it alone.
        * Otherwise, try to match *value* against ``options`` of any
          ``SELECT``/``DROPDOWN`` field. If exactly one field matches,
          register *label* as an alias for that field.

        Returns ``self`` for chaining. Mutates the underlying field defs.
        """
        for label, value in offer.fields.items():
            if not label:
                continue
            if label.casefold() in self.lower_label_map:
                continue
            value_cf = str(value).casefold()
            matches = [
                fid
                for fid, fd in self.fields.items()
                if fd.options
                and any(opt.casefold() == value_cf for opt in fd.options)
            ]
            if len(matches) == 1:
                self.add_alias(matches[0], label)
        return self

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
