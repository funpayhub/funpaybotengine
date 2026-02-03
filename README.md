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
    <a href="https://github.com/funpayhub/funpaybotengine/commits"><img src="https://img.shields.io/github/commit-activity/w/funpayhub/funpaybotengine.svg?style=flat-square" alt="Commit activity" /></a>
</p>

Современная, удобная и функциональная асинхронная API-обёртка для FunPay на Python.




Установка
----------

**Необходим Python 3.10 или выше.**

``` shell
# Using uv
uv add funpaybotengine

# Or using pip
pip install funpaybotengine
```

Пример использования
--------------------
```python
import sys
import asyncio
import logging

from funpaybotengine import Bot, Dispatcher
from funpaybotengine.types import Message

bot: Bot = Bot(golden_key='token')
dp: Dispatcher = Dispatcher()


@dp.on_new_message(lambda message: message.text.lower() == 'привет')
async def echo(message: Message):
    await message.reply(text='пока')


async def main():
    await bot.listen_events(dp)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
```


Экосистема FunPayHub
-------------------

Если вам нужен **готовый, бесплатный и опенсорсный бот для FunPay** с расширяемой архитектурой, плагинами и богатым функционалом — обратите внимание на **[FunPayHub](https://github.com/funpayhub/funpayhub)**.

FunPayHub — это полноценный бот, построенный с использованием **FunpayBotEngine**, **Aiogram** и **Eventry**, который имеет богатый функционал:
- автоподнятие лотов;
- автоответы на сообщения с форматтерами и хуками;
- автовыдача товаров;
- удобное расширение с помощью плагинов;
- гибкие настройки;
- многое другое. 

👉 Репозиторий проекта: https://github.com/funpayhub/funpayhub
