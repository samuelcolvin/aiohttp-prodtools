import re

from .settings import Settings


def _rfc_1738_quote(text):
    return re.sub(r'[:@/]', lambda m: '%{:X}'.format(ord(m.group(0))), text)


def dsn(settings: Settings=None,
        drivername: str=None,
        username: str=None,
        password: str=None,
        host: str=None,
        port: str=None,
        database: str=None,
        query: str=None):
    """
    Create a DSN from from connection settings.
    
    Stolen approximately from sqlalchemy/engine/url.py:URL.
    """
    if settings is not None:
        database = settings.DB_NAME
        password = settings.DB_PASSWORD
        host = settings.DB_HOST
        port = settings.DB_PORT
        username = settings.DB_USER
        drivername = settings.DB_DRIVER

    s = drivername + '://'
    if username is not None:
        s += _rfc_1738_quote(username)
        if password is not None:
            s += ':' + _rfc_1738_quote(password)
        s += '@'
    if host is not None:
        if ':' in host:
            s += '[{}]'.format(host)
        else:
            s += host
    if port is not None:
        s += ':{}'.format(int(port))
    if database is not None:
        s += '/' + database
    query = query or {}
    if query:
        keys = list(query)
        keys.sort()
        s += '?' + '&'.join('{}={}'.format(k, query[k]) for k in keys)
    return s
