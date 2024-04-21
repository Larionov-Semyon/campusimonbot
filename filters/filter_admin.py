import os
from aiogram.filters import BaseFilter
from aiogram.types import Message


class AdminFilter(BaseFilter):
    def __init__(self, admin_ids):
        self.admins = admin_ids

    async def __call__(self, message: Message) -> bool:
        return str(message.from_user.id) in self.admins

