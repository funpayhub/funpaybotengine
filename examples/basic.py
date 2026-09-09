from __future__ import annotations

import sys
import asyncio
import logging

from funpaybotengine import Bot, Router, Dispatcher
from funpaybotengine.types import Message


bot: Bot = Bot(golden_key='token')
router = Router(name='my_router')
dp: Dispatcher = Dispatcher(router)


@router.on_new_message()
async def echo(message: Message) -> None:
    await message.reply(text='echo')


async def main() -> None:
    await bot.listen_events(dp)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
