from __future__ import annotations


__all__ = ('UploadAvatar',)


from typing import TYPE_CHECKING, Any
from io import BytesIO

from pydantic import BaseModel

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import RawResponse


class UploadAvatar(FunPayMethod[bool], BaseModel):
    """
    Uploads new user avatar (``https://funpay.com/avatar``).
    """

    file: str | BytesIO
    """Image stream or path to image to upload."""

    def __init__(self, file: str | BytesIO):
        if isinstance(file, str):
            with open(file, 'rb') as f:
                file = BytesIO(f.read())

        super().__init__(
            url='file/avatar',
            method=HTTPMethod.POST,
            data={'file': file},
            headers={'X-Requested-With': 'XMLHttpRequest'},
            file=file,
        )

    async def transform_result(self, parsing_result: str, response: RawResponse[Any]) -> bool:
        return True
