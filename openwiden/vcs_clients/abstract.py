from openwiden.users import services, models


class AbstractVCSClient:
    def __init__(self, vcs_account: models.VCSAccount) -> None:
        self._vcs_account = vcs_account
        self._client = services.get_client(vcs=vcs_account.vcs)

    def _post(self, *, url: str, data: dict) -> dict:
        response = self._client.post(url, token=self._vcs_account.to_token(), json=data)

        # TODO: rewrite exception handler
        if response.status_code != 201:
            raise ValueError(f"Unable to create webhook with data: {data}\n" f"Response: {response.json()}")

        return response.json()
