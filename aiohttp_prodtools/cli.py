import click
from .version import VERSION


@click.group()
@click.version_option(VERSION, '-V', '--version', prog_name='aiohttp-prodtools')
def cli():
    pass


EXEC_LINES = [
    'import asyncio, os, re, sys',
    'from datetime import datetime, timedelta, timezone',
    'from pprint import pprint as pp',
    '',
    # 'from aiopg.sa import create_engine',
    'from app.settings import Settings',
    '',
    'loop = asyncio.get_event_loop()',
    'await_ = loop.run_until_complete',
    'settings = Settings()',
    # 'pg = await_(create_engine(pg_dsn(settings[\'database\'])))',
    # 'conn = await_(pg._acquire())',
]
EXEC_LINES += (
    ['print("\\n    Python {v.major}.{v.minor}.{v.micro}\\n".format(v=sys.version_info))'] +
    [f'print("    {l}")' for l in EXEC_LINES]
)


@cli.command()
def shell():
    from IPython import start_ipython
    from IPython.terminal.ipapp import load_default_config
    c = load_default_config()

    c.TerminalIPythonApp.display_banner = False
    c.TerminalInteractiveShell.confirm_exit = False
    c.InteractiveShellApp.exec_lines = EXEC_LINES
    start_ipython(argv=(), config=c)

