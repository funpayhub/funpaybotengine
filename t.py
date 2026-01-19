from __future__ import annotations

from funpaybotengine import Bot
from funpaybotengine.types.enums import Currency


async def main() -> None:
    bot = Bot('mbyq84w89kcju87qs3hw5gqfovx8ig0v')

    response = await bot.switch_currency(Currency.RUB)
    response = await bot.get_exchange_rate(Currency.EUR)

    print(response)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
