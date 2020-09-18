import asyncio
import os

import pytest
from asgiref.compatibility import guarantee_single_callable
from asgiref.sync import sync_to_async
from asgiref.testing import ApplicationCommunicator
from django_redis import get_redis_connection
from rest_framework_simplejwt.tokens import RefreshToken
from websockets.protocol import State

from config.websocket import websocket_application


pytestmark = [pytest.mark.functional, pytest.mark.django_db, pytest.mark.asyncio]


@pytest.fixture(autouse=True)
def cache_settings(settings):
    """
    Set redis as default cache.
    """
    settings.CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # Mimicing memcache behavior.
                # http://jazzband.github.io/django-redis/latest/#_memcached_exceptions_behavior
                "IGNORE_EXCEPTIONS": True,
            },
        }
    }


@pytest.fixture()
def redis():
    return get_redis_connection()


@pytest.fixture()
def create_websocket_app():
    def _create(query_string: str) -> ApplicationCommunicator:
        class Queue(asyncio.Queue):
            state = None

            async def ensure_open(self) -> None:
                return

        class WebsocketApp(ApplicationCommunicator):
            def __init__(self, application, scope):
                self.application = guarantee_single_callable(application)
                self.scope = scope
                self.input_queue = Queue()
                self.output_queue = Queue()
                self.future = asyncio.ensure_future(
                    self.application(scope, self.input_queue.get, self.output_queue.put)
                )

        websocket_app = WebsocketApp(
            websocket_application, {"type": "websocket", "query_string": query_string.encode()},
        )
        return websocket_app

    return _create


@pytest.fixture()
def create_user(create_user):
    def _create_user(**kwargs):
        return sync_to_async(create_user)(**kwargs)

    return _create_user


@pytest.fixture()
def create_refresh_token():
    def _create_access_token(user):
        return sync_to_async(RefreshToken.for_user)(user)

    return _create_access_token


@pytest.fixture()
def create_access_token(create_refresh_token):
    async def _create_access_token(user):
        refresh_token = await create_refresh_token(user)
        return str(refresh_token.access_token)

    return _create_access_token


@pytest.mark.parametrize(
    "query_string", [pytest.param("", id="access token is not found"), pytest.param("fake", id="token error"),]
)
async def test_parse_access_token_from_query_string(create_websocket_app, query_string: str):
    websocket_app = create_websocket_app(query_string)
    await websocket_app.send_input({"type": "websocket.connect"})
    assert await websocket_app.receive_output() == {"type": "websocket.close"}


# async def test_token_contained_no_recognizable_user_identification(
#     create_websocket_app,
#     create_user,
#     create_access_token,
# ):
#     user = await create_user()
#     access_token = await create_access_token(user)
#     websocket_app = create_websocket_app(f"access_token={access_token}")
#
#     patched_access_token = mock.patch("rest_framework_simplejwt.tokens.AccessToken")
#     patched_access_token.side_effect = {}
#
#     await websocket_app.send_input({"type": "websocket.connect"})
#
#     assert await websocket_app.receive_output() == {'type': 'websocket.close'}


async def test_user_not_found(create_websocket_app, create_user, create_access_token):
    user = await create_user()
    access_token = await create_access_token(user)
    await sync_to_async(user.delete, thread_sensitive=True)()
    websocket_app = create_websocket_app(f"access_token={access_token}")

    await websocket_app.send_input({"type": "websocket.connect"})

    assert await websocket_app.receive_output() == {"type": "websocket.close"}


async def test_user_is_inactive(create_websocket_app, create_user, create_access_token):
    user = await create_user()
    user.is_active = False
    await sync_to_async(user.save)()
    access_token = await create_access_token(user)
    websocket_app = create_websocket_app(f"access_token={access_token}")

    await websocket_app.send_input({"type": "websocket.connect"})

    assert await websocket_app.receive_output() == {"type": "websocket.close"}


async def test_success(
    create_user, create_access_token, cache, redis, create_websocket_app,
):
    # Create user and access token
    user = await create_user()
    user.is_active = True
    await sync_to_async(user.save)()
    access_token = await create_access_token(user)
    websocket_app = create_websocket_app(f"access_token={access_token}")

    # Test success connect
    await websocket_app.send_input({"type": "websocket.connect"})
    assert await websocket_app.receive_output() == {"type": "websocket.accept"}

    # Trigger event for a user
    redis.publish(str(user.id), "test message")

    # Test message receive
    websocket_app.output_queue.state = State.OPEN
    assert await websocket_app.receive_output() == {"bytes": b"test message", "type": "websocket.send"}
