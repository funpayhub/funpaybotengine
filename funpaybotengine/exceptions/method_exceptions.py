from __future__ import annotations


__all__ = ['MethodError', 'InvalidOfferFieldsError']


from .base import FunPayBotEngineError


class MethodError(FunPayBotEngineError): ...


class InvalidOfferFieldsError(MethodError):
    def __init__(self, message: str, fields: dict[str, str] | None = None):
        self.message = message
        self.fields = fields

    def __str__(self):
        return self.message
