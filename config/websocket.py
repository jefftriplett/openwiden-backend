import asyncio
from logging import getLogger

from asgiref.sync import sync_to_async
from django_redis import get_redis_connection
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from websockets import ConnectionClosedError
from websockets.protocol import State

from openwiden.users.models import User

log = getLogger(__name__)


async def send_message(pubsub, send):
    """
    Listens redis pubsub and sends message on receive.
    """
    while True:

        # Check redis for a message
        message = pubsub.get_message()

        # Perform message if exist
        if message:
            log.info(f"[Websocket] received pubsub message {message}")

            # If message type is message, then send it to the client
            if message.get("type") == "message":
                log.info(f"[Websocket] sending websocket message '{message['data']}'")
                await send({"type": "websocket.send", "bytes": message["data"]})
        else:
            log.info(f"[Websocket] no message, checking connection...")

            # If connection is OPEN, then check it and close it if it's not
            if send.__self__.state == State.OPEN:
                try:
                    log.info(f"[Websocket] ensure open")
                    await send.__self__.ensure_open()
                except ConnectionClosedError:
                    log.info(f"[Websocket] closing opened connection...")
                    break

            # Close connection manually if it's already closed
            elif send.__self__.state == State.CLOSED:
                log.info(f"[Websocket] closing connection...")
                break

            # Wait for a message for a while
            await asyncio.sleep(0.2)


async def websocket_application(scope, receive, send) -> None:
    """
    Websocket application.
    """
    redis = get_redis_connection()

    # Receive websocket event data
    event = await receive()
    event_type = event["type"]

    log.info(f"[Websocket] new event with type {event_type} and scope {scope}")

    # Subscribe user for events
    if event["type"] == "websocket.connect":

        # Parse access token
        try:
            access_token = scope.get("query_string").decode().split("=")[-1]
        except (TypeError, KeyError, ValueError, AttributeError) as e:
            log.error(f"[Websocket] Access token is not found. Original error: {e}")
            await send({"type": "websocket.close"})
            return

        # Get validated JWT token
        try:
            validated_token = AccessToken(access_token)
        except TokenError as e:
            log.error(f"[Websocket] {e.args[0]}.")
            await send({"type": "websocket.close"})
            return

        # Get user_id from the validated token
        try:
            user_id = validated_token["user_id"]
        except KeyError:
            log.error("[Websocket] Token contained no recognizable user identification.")
            await send({"type": "websocket.close"})
            return

        # Get user from the DB with async operation
        try:
            user = await sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            log.error("[Websocket] User not found.")
            await send({"type": "websocket.close"})
            return

        # Check that user is active
        if not user.is_active:
            log.error("[Websocket] User is inactive.")
            await send({"type": "websocket.close"})
            return

        pubsub = redis.pubsub()
        pubsub.subscribe(str(user_id))
        await send({"type": "websocket.accept"})
        await send_message(pubsub, send)
