<p align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://github.com/user-attachments/assets/1b7099e0-14a4-408d-96a5-a149da1ad159">
        <source media="(prefers-color-scheme: light)" srcset="https://github.com/user-attachments/assets/0fe5e617-e20d-42b4-804c-88d3356143d3">
        <img src="https://github.com/user-attachments/assets/e9827ef4-c994-464b-a4f7-83ae9c705cdd" alt="FunpayBotEngine logo" width="300">
    </picture>
</p>

FunpayBotEngine
===============

<p align="center">
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/pypi/l/funpaybotengine.svg?style=flat-square" alt="License" /></a>
    <a href="https://pypi.org/project/funpaybotengine"><img src="https://img.shields.io/pypi/status/funpaybotengine.svg?style=flat-square" alt="PyPI status" /></a>
    <a href="https://pypi.org/project/funpaybotengine"><img src="https://img.shields.io/pypi/v/funpaybotengine.svg?style=flat-square" alt="PyPI version" /></a>
    <a href="https://pypi.org/project/funpaybotengine"><img src="https://img.shields.io/pypi/pyversions/funpaybotengine.svg?style=flat-square" alt="PyPI supported Python versions" /></a>
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
