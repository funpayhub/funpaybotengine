from __future__ import annotations


__all__ = ['RunnerRequestError']


from typing import TYPE_CHECKING

from .base import FunPayBotEngineError


if TYPE_CHECKING:
    from funpaybotengine.types import RunnerResponse


class RunnerRequestError(FunPayBotEngineError):
    def __init__(self, runner_response: RunnerResponse):
        self.runner_response = runner_response

    def __str__(self) -> str:
        response = self.runner_response.response

        if not response or not response.error:
            return 'Unknown error'

        return response.error
