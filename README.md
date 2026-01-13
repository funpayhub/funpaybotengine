<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/bdec8cef-0031-4e92-990e-f15895848faa?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/e9827ef4-c994-464b-a4f7-83ae9c705cdd">
  <img src="https://github.com/user-attachments/assets/e9827ef4-c994-464b-a4f7-83ae9c705cdd" alt="FunpayBotEngine logo" width="300">
</picture>
</p>




FunpayBotEngine
===============

<p align="center">
    <a href="https://github.com/funpayhub/funpaybotengine/commits"><img src="https://img.shields.io/github/commit-activity/w/funpayhub/funpaybotengine.svg?style=flat-square" alt="Commit activity" /></a>
</p>

A modern, easy to use, feature-rich, and async ready API wrapper for Funpay written in Python.

Installing
----------

**Python 3.10 or higher is required.**

``` shell
# Using uv
uv add funpaybotengine

# Or using pip
pip install funpaybotengine
```

Quick Example
-------------
```python
import sys
import asyncio
import logging

from funpaybotengine import Bot, Dispatcher
from funpaybotengine.types import Message

bot: Bot = Bot(golden_key='token')
dp: Dispatcher = Dispatcher()


@dp.on_new_message()
async def echo(message: Message):
    await message.reply(text='echo')


async def main():
    await bot.listen_events(dp)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
```
