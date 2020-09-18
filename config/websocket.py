import asyncio
from logging import getLogger
from typing import Generator, Optional

from asgiref.sync import sync_to_async
from django_redis import get_redis_connection
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from websockets import ConnectionClosedError
from websockets.protocol import State

from openwiden.users.models import User

log = getLogger(__name__)


class WebsocketApplication:
    def __init__(self, scope, receive, send) -> None:
        self._scope = scope
        self._receive = receive
        self._send = send

    def __await__(self) -> Generator:
        return self.handle().__await__()

    async def handle(self):
        # Receive websocket event data
        event = await self._receive()
        event_type = event["type"]

        log.info(f"[Websocket] new event with type {event_type} and scope {self._scope}")

        # Handle event
        if event["type"] == "websocket.connect":
            await self._handle_connect_event()
        else:
            log.error(f"[Websocket] received not handled event with type {event_type} " f"and scope {self._scope}")

    async def _handle_and_send_pubsub_messages(self, pubsub):
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
                    await self._send({"type": "websocket.send", "bytes": message["data"]})
            else:
                log.info(f"[Websocket] no message, checking connection...")

                # If connection is OPEN, then check it and close it if it's not
                if self._send.__self__.state == State.OPEN:
                    try:
                        log.info(f"[Websocket] ensure open")
                        await self._send.__self__.ensure_open()
                    except ConnectionClosedError:
                        log.info(f"[Websocket] closing opened connection...")
                        break

                # Close connection manually if it's already closed
                elif self._send.__self__.state == State.CLOSED:
                    log.info(f"[Websocket] closing connection...")
                    break

                # Wait for a message for a while
                await asyncio.sleep(0.2)

    async def _handle_connect_event(self):
        user_id = await self._get_user_id()

        if not user_id:
            return

        redis = get_redis_connection()
        pubsub = redis.pubsub()
        pubsub.subscribe(str(user_id))

        await self._send({"type": "websocket.accept"})
        await self._handle_and_send_pubsub_messages(pubsub)

    async def _get_user_id(self) -> Optional[str]:
        # Parse access token
        try:
            access_token = self._scope.get("query_string").decode().split("=")[-1]
        except (TypeError, KeyError, ValueError, AttributeError) as e:
            log.error(f"[Websocket] Access token is not found. Original error: {e}")
            await self._send({"type": "websocket.close"})
            return None

        # Get validated JWT token
        try:
            validated_token = AccessToken(access_token)
        except TokenError as e:
            log.error(f"[Websocket] {e.args[0]}.")
            await self._send({"type": "websocket.close"})
            return None

        # Get user_id from the validated token
        try:
            print(validated_token)
            user_id = validated_token["user_id"]
        except KeyError:
            log.error("[Websocket] Token contained no recognizable user identification.")
            await self._send({"type": "websocket.close"})
            return None

        # Get user from the DB with async operation
        try:
            user = await sync_to_async(User.objects.get)(id=user_id)
        except User.DoesNotExist:
            log.error("[Websocket] User not found.")
            await self._send({"type": "websocket.close"})
            return None

        # Check that user is active
        if not user.is_active:
            log.error("[Websocket] User is inactive.")
            await self._send({"type": "websocket.close"})
            return None

        return user_id
