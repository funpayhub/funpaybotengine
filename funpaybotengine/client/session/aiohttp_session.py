from __future__ import annotations


__all__ = ('AioHttpSession',)


import time
import asyncio
from typing import TYPE_CHECKING, Any

from yarl import URL
from aiohttp import TCPConnector, ClientSession, ClientTimeout
from aiohttp.hdrs import USER_AGENT
from aiohttp_socks import ProxyConnector
from typing_extensions import Self

from funpaybotengine.loggers import session_logger
from funpaybotengine.types.enums import Language
from funpaybotengine.client.session.base import Response, BaseSession, RawResponse
from funpaybotengine.client.session.http_methods import HTTPMethod
from funpaybotengine.exceptions.session_exceptions import BannedError


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.methods.base import FunPayMethod, MethodReturnType


class AioHttpSession(BaseSession):
    def __init__(
        self,
        proxy: str | None = None,
        default_headers: dict[str, str] | None = None,
    ):
        super().__init__()

        self._proxy = proxy
        self._default_headers = (
            default_headers
            if default_headers is not None
            else {
                USER_AGENT: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) '
                'Gecko/20100101 Firefox/140.0',
            }
        )

        self._connector: TCPConnector | ProxyConnector | None = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def session(self) -> ClientSession:
        if self._connector is None or self._connector.closed:
            self._connector = (
                ProxyConnector.from_url(self._proxy) if self._proxy else TCPConnector()
            )
        return ClientSession(
            # proxy=self.proxy,
            base_url='https://funpay.com',
            connector=self._connector,
            connector_owner=False,
        )

    async def close(self) -> None:
        if self._connector is not None and not self._connector.closed:
            await self._connector.close()

            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.25)

    def prepare_cookies(
        self,
        session: ClientSession,
        bot: Bot,
        skip_session_cookies: bool = False,
    ) -> None:
        session.cookie_jar.update_cookies({'cookie_prefs': '1'})  # no 3rd-party cookies

        if bot.golden_key:
            session.cookie_jar.update_cookies({'golden_key': bot.golden_key})

        if bot.phpsessid and not skip_session_cookies:
            session.cookie_jar.update_cookies({'PHPSESSID': bot.phpsessid})

    async def make_request(
        self,
        method: FunPayMethod[MethodReturnType],
        bot: Bot,
        timeout: float | None = None,
        skip_session_cookies: bool = False,
    ) -> Response[MethodReturnType]:
        session = await self.session()

        self.prepare_cookies(session, bot, skip_session_cookies=skip_session_cookies)
        csrf_token = bot.csrf_token if (bot.csrf_token and not skip_session_cookies) else ''
        timeout_obj = ClientTimeout(total=timeout if timeout is not None else method.timeout)
        url = await self.resolve_url(method, bot, session)
        session_logger.info('Making %s request to %s', method.method.name, url)

        start_time = time.time()
        async with session:
            if method.method == HTTPMethod.GET:
                response = await session.get(
                    url,
                    params=await method.get_data(bot),
                    timeout=timeout_obj,
                    headers=self._default_headers | await method.get_headers(bot),
                )
            elif method.method == HTTPMethod.POST:
                response = await session.post(
                    url,
                    data=await method.get_data(bot)
                    | ({'csrf_token': csrf_token} if csrf_token else {}),
                    timeout=timeout_obj,
                    headers=self._default_headers | await method.get_headers(bot),
                )
            else:
                raise ValueError(f'Unsupported HTTP method {method.method.name}.')

        session_logger.debug(
            f'Requesting {url} took {time.time() - start_time}s. Status: {response.status}.',
        )

        if response.url.parts[-1] == 'blocked' and response.status == 200:
            raise BannedError(method=method)

        self.check_status_code(method, response.status)

        cookies: dict[str, str] = {}
        if response.history:
            for i in response.history:
                cookies = cookies | {k: v.value for k, v in i.cookies.items()}
        else:
            cookies = {k: v.value for k, v in response.cookies.items()}

        raw_response = RawResponse(
            url=str(response.real_url),
            status_code=response.status,
            raw_response=await response.text(),
            headers={k.lower(): v for k, v in response.headers.items()},
            cookies=cookies,
            method_obj=method,
            executed_as=bot,
            context={'session': self, 'bot': bot},
        )

        start_time = time.time()
        response_obj = await method.to_obj(raw_response)
        result = Response.from_raw_response(raw_response, response_obj)

        session_logger.debug('Parsing response of %s took %.10fs.', url, time.time() - start_time)
        return result

    @staticmethod
    async def resolve_url(
        method: FunPayMethod[Any],
        bot: Bot,
        session: ClientSession,
    ) -> str:
        method_url = await method.get_url(bot)
        if URL(method_url).is_absolute():
            return method_url

        locale = bot.locale

        if method.ignore_locale or bot is None:
            locale = Language.RU
        elif method.locale is not None:
            locale = method.locale

        if locale is None:
            locale = Language.RU

        if method_url.startswith('/'):
            method_url = method_url[1:]

        url = f'{locale.value.url_alias}/{method_url}'

        if not session._base_url:
            return url

        return str(session._base_url.join(URL(url)))

    @property
    def proxy(self) -> str | None:
        return self._proxy
