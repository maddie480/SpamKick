import logging
import os
from typing import Final
from time import time

from discord import Client, Intents, Message, Member, NotFound

DELAY_SECONDS: Final[int] = int(os.environ["DELAY_SECONDS"])
CHANNEL_COUNT: Final[int] = int(os.environ["CHANNEL_COUNT"])
LOG_CHANNEL_ID: Final[int] = int(os.environ["LOG_CHANNEL_ID"])
DEBUG: Final[bool] = os.environ["DEBUG"] == "1"

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)


class SpamKickBot(Client):
    message_history: list[Message] = []

    def _update_message_history_with(self, received_message: Message):
        self.message_history.append(received_message)
        self.message_history.sort(key=lambda m: m.created_at)

        while self.message_history and self.message_history[0].created_at.timestamp() < time() - DELAY_SECONDS:
            self.message_history.pop(0)

        if DEBUG:
            messages_to_print = [f"[Message from {message.id} in {message.channel.id} at {message.created_at}]" for
                                 message in self.message_history]
            logging.debug("Message history: " + ", ".join(messages_to_print))

    def _list_messages_from_user(self, user: Member) -> tuple[list[Message], set[int]]:
        messages_from_user = [message for message in self.message_history if
                              message.author.id == user.id]

        message_channels = set(message.channel.id for message in messages_from_user)
        if DEBUG:
            logging.debug(f"User {user.id} has posted in {len(message_channels)} channel(s) so far")

        return messages_from_user, message_channels

    @staticmethod
    async def _delete_messages(messages: list[Message]):
        for message in messages:
            try:
                logging.info(f"Deleting message {message.id}")
                await message.delete()
            except NotFound:
                logging.warning(f"Could not delete message {message.id} because it doesn't exist anymore!")

    async def _kick_user_with_logging(self, user: Member, channel_ids: set[int]):
        await user.kick(
            reason=f"Posted in {CHANNEL_COUNT} channels within {DELAY_SECONDS} seconds")

        logging.info(f"User {user.id} was kicked successfully")

        await self.get_channel(LOG_CHANNEL_ID).send(
            f"Kicked user `{user.name}` (`{user.id}`) for sending messages within {DELAY_SECONDS} seconds in following channels: <#"
            + ">, <#".join(str(chan) for chan in channel_ids) + ">")

    async def on_message(self, received_message: Message):
        self._update_message_history_with(received_message)

        user = received_message.author
        messages_from_user, message_channels = self._list_messages_from_user(user)

        if len(message_channels) >= CHANNEL_COUNT:
            await self._kick_user_with_logging(user, message_channels)
            await self._delete_messages(messages_from_user)


SpamKickBot(intents=Intents.default()).run(os.environ["TOKEN"])
