import os

import pytest
from asgiref.sync import sync_to_async
from asgiref.testing import ApplicationCommunicator
from django_redis import get_redis_connection
from rest_framework_simplejwt.tokens import RefreshToken

from config.websocket import websocket_application


@pytest.mark.functional
@pytest.mark.django_db
@pytest.mark.asyncio
async def test_success(create_user, settings, cache):
    # Set redis as default cache
    settings.CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # Mimicing memcache behavior.
                # http://jazzband.github.io/django-redis/latest/#_memcached_exceptions_behavior
                # "IGNORE_EXCEPTIONS": True,
            },
        }
    }

    # Create user and access token
    user = await sync_to_async(create_user, thread_sensitive=True)()
    refresh_token = await sync_to_async(RefreshToken.for_user, thread_sensitive=True)(user)
    access_token = str(refresh_token.access_token)
    assert access_token is not None

    # Init redis
    redis = get_redis_connection()

    # Create websocket client
    ws = ApplicationCommunicator(websocket_application, {"type": "websocket"})

    # Test success connect
    await ws.send_input({"type": "websocket.connect", "access_token": access_token})
    assert await ws.receive_output() == {"type": "websocket.accept"}

    # Trigger event for a user
    redis.publish(str(user.id), "test message")

    assert await ws.receive_output() == {"message": b"test message", "type": "websocket.send"}
