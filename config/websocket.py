import asyncio

from asgiref.sync import sync_to_async
from django_redis import get_redis_connection
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from openwiden.users.models import User


async def send_message(pubsub, send, done):
    while not done:
        message = pubsub.get_message()
        if message and message["type"] == "message":
            await send(
                {"type": "websocket.send", "message": message["data"],}
            )
        else:
            await asyncio.sleep(0.2)


async def websocket_application(scope, receive, send):
    done = False
    while True:
        event = await receive()
        access_token = event.get("access_token")
        if not access_token:
            await send({"error_code": 1, "error_message": "Access token is not found."})
            break

        try:
            validated_token = AccessToken(access_token)
        except TokenError as e:
            await send({"error_code": 2, "error_message": e.args[0]})
            break

        try:
            user_id = validated_token["user_id"]
        except KeyError:
            await send({"error_code": 3, "error_message": "Token contained no recognizable user identification"})

        try:
            user = await sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            await send({"error_code": 4, "error_message": "User not found"})

        if not user.is_active:
            await send({"error_code": 5, "error_message": "User is inactive"})

        if event["type"] == "websocket.connect":
            redis = get_redis_connection()
            pubsub = redis.pubsub()
            pubsub.subscribe(str(user_id))
            await send({"type": "websocket.accept"})
            await send_message(pubsub, send, done)

        if event["type"] == "websocket.disconnect":
            break
