from vkbottle.dispatch.rules import ABCRule
from vkbottle.bot import Message

from config import USER_ID_VK


class Permission(ABCRule[Message]):

    async def check(self, event: Message) -> bool:
        return event.from_id == USER_ID_VK
