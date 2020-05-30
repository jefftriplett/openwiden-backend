import pytest


@pytest.fixture
def create_mock_refresh_token():
    def factory(access: str, refresh: str) -> MockRefreshToken:
        return MockRefreshToken(access=access, refresh=refresh)

    return factory


class MockRefreshToken:
    def __init__(self, access: str, refresh: str):
        self.access_token = access
        self.refresh = refresh

    def __str__(self):
        return self.refresh
