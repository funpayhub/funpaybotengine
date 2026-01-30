"""
Example docker compose file:

services:
  redis:
    image: redis:7.4-alpine
    container_name: redis
    hostname: redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - network
    healthcheck:
      test: [ "CMD-SHELL", "redis-cli ping | grep PONG" ]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
        reservations:
          cpus: '0.05'
          memory: 64M

volumes:
  redis_data:

networks:
  network:
    driver: bridge
"""
from __future__ import annotations

import sys
import asyncio
import logging
from contextlib import suppress

from redis.asyncio import Redis
from funpaybotengine import Bot, Dispatcher
from funpaybotengine.types import Message
from funpaybotengine.storage import RedisStorage


# It is recommended to use more reliable data storage means, some kind of relational databases
# This recommendation is only for bot storage; you can safely use Redis for listen_events.
redis: Redis = Redis()
storage: RedisStorage = RedisStorage(redis=redis)

bot: Bot = Bot(
    golden_key='token',
    storage=storage,
)
dp: Dispatcher = Dispatcher()


@dp.on_new_message()
async def echo(message: Message) -> None:
    await message.reply(text='echo')


async def main() -> None:
    await bot.listen_events(dp, session_storage=storage)


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
