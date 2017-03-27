from asyncio import CancelledError

from aiohttp.web_exceptions import HTTPBadRequest, HTTPException, HTTPInternalServerError


async def log_extra(request, response=None):
    return {'data': dict(
        request_url=str(request.rel_url),
        request_method=request.method,
        request_host=request.host,
        request_headers=dict(request.headers),
        request_text=response and await request.text(),
        response_status=response and response.status,
        response_headers=response and dict(response.headers),
        response_text=response and response.text,
    )}


async def log_warning(request, response):
    request.app['error_logger'].warning('%s %d', request.rel_url, response.status, extra={
        'fingerprint': [request.rel_url, str(response.status)],
        'data': await log_extra(request, response)
    })


async def error_middleware(app, handler):
    async def _handler(request):
        try:
            http_exception = getattr(request.match_info, 'http_exception', None)
            if http_exception:
                raise http_exception
            else:
                r = await handler(request)
        except HTTPException as e:
            await log_warning(request, e)
            raise
        except BaseException as e:
            request.app['error_logger'].exception('%s: %s', e.__class__.__name__, e, extra={
                'fingerprint': [e.__class__.__name__, str(e)],
                'data': await log_extra(request)
            })
            raise HTTPInternalServerError()
        else:
            if r.status > 310:
                await log_warning(request, r)
        return r
    return _handler


class ConnectionManager:
    """
    Copies engine.acquire()'s context manager but is lazy in that you need to call get_connection()
    for a connection to be found, otherwise does nothing.
    
    """
    # TODO non lazy version
    # TODO transactions
    # TODO transactions for entire requests.
    # TODO test with aiopg, aiopg.sa, asyncpg
    def __init__(self, engine):
        self._engine = engine
        self._conn = None
        self._entered = False

    async def __aenter__(self):
        self._entered = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._conn is not None:
                await self._engine.release(self._conn)
                self._conn = None
        except CancelledError:
            raise HTTPBadRequest()

    async def get_connection(self):
        assert self._entered
        if self._conn is None:
            self._conn = await self._engine._acquire()
        return self._conn


async def pg_conn_middleware(app, handler):
    async def _handler(request):
        async with ConnectionManager(app['pg_engine']) as conn_manager:
            request['conn_manager'] = conn_manager
            return await handler(request)
    return _handler
