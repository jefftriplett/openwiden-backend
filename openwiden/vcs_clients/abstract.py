from typing import Union, List, Dict

from openwiden.users import services, models

JsonAbleType = Union[str, int, float, bool, None]
JsonDictType = Dict[JsonAbleType, Union[JsonAbleType, List[dict]]]
JsonListType = List[JsonDictType]
JsonType = Union[JsonListType, JsonDictType]


class AbstractVCSClient:
    def __init__(self, vcs_account: models.VCSAccount) -> None:
        self._vcs_account = vcs_account
        self._client = services.get_client(vcs=vcs_account.vcs)

    def _post(self, *, url: str, data: dict) -> JsonType:
        response = self._client.post(url, token=self._vcs_account.to_token(), json=data)

        # TODO: rewrite exception handler
        if response.status_code not in [201, 200]:
            raise ValueError(f"request failed: {data}\n" f"Response: {response.json()}")

        return response.json()

    def _get(self, *, url: str) -> JsonType:
        response = self._client.get(url, token=self._vcs_account.to_token())

        if response.status_code != 200:
            raise ValueError(f"request failed: {response.json()}")

        return response.json()
