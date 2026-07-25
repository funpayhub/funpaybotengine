from __future__ import annotations


__all__ = ['UploadImage']


import json
from typing import TYPE_CHECKING, Any
from io import BytesIO

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class UploadImage(FunPayMethod[int]):
    """
    Uploads chat image (``https://funpay.com/``).

    Returns image ID (``int``).
    """
    url = 'file/addChatImage'
    method = HTTPMethod.POST
    data = lambda m, *_: {'file': m.file}
    headers = {'X-Requested-With': 'XMLHttpRequest'}

    file: str | BytesIO
    """Image stream or path to image to upload."""

    def model_post_init(self, context: Any, /) -> None:
        if isinstance(self.file, str):
            with open(self.file, 'rb') as f:
                self.file = BytesIO(f.read())

    async def transform_result(self, parsing_result: str, response: RawResponse[Any]) -> int:
        return int(json.loads(parsing_result)['fileId'])
