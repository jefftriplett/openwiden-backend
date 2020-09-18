import json
from abc import ABC
from typing import Union

from django.utils.translation import gettext_lazy as _
from rest_framework import status


class ServiceException(ABC, Exception):
    """
    Service exception.
    """

    error_message: str = _("Unexpected exception occurred.")
    app_id: int = None
    error_code: int = None
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, **error_message_format_kwargs) -> None:
        assert self.error_message is not None
        assert self.error_code is not None
        assert self.app_id is not None
        self._error_message_format_kwargs = error_message_format_kwargs

    def _get_error_message(self) -> str:
        if self._error_message_format_kwargs:
            return self.error_message.format(**self._error_message_format_kwargs)
        return self.error_message

    def _get_error_code(self) -> str:
        return f"{self.app_id:02d}{self.error_code:03d}"

    def _get_detail(self, json_dump: bool = False) -> Union[dict, str]:
        detail = dict(error_code=self._get_error_code(), error_message=str(self._get_error_message()),)

        if json_dump:
            detail = json.dumps(detail)

        return detail

    @property
    def detail(self) -> dict:
        return self._get_detail()

    @property
    def json_dumped_detail(self) -> str:
        return self._get_detail(json_dump=True)
