import json
import os
from importlib import import_module
from pathlib import Path
from typing import Any, Type


class Setting:
    def __init__(self, default: Any=None, *, v_type: Type=None, required: bool=False, env: str=None):
        if default and v_type:
            raise RuntimeError('"default" and "v_type" cannot both be defined.')
        elif default and required:
            raise RuntimeError('It doesn\'t make sense to have "default" set and required=True.')
        if default:
            self.default = default
            self.v_type = type(default)
        else:
            self.v_type = v_type
        self.required = required
        self.env_var_name = env


class BaseSettings:
    """
    Base class for settings, any setting defined on inheriting classes here can be overridden by:

    Setting the appropriate environment variable, eg. to override FOOBAR, `export APP_FOOBAR="whatever"`.
    This is useful in production for secrets you do not wish to save in code and
    also plays nicely with docker(-compose). Settings will attempt to convert environment variables to match the
    type of the value here.

    Or, passing the custom setting as a keyword argument when initialising settings (useful when testing)
    """
    _ENV_PREFIX = 'APP_'
    Setting = Setting

    DB_DATABASE = None
    DB_USER = None
    DB_PASSWORD = None
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_DRIVER = 'postgres'

    def __init__(self, **custom_settings):
        """
        :param custom_settings: Custom settings to override defaults, only attributes already defined can be set.
        """
        self._dict = {
            **self._substitute_environ(custom_settings),
            **self._get_custom_settings(custom_settings),
        }
        [setattr(self, k, v) for k, v in self._dict.items()]

    @property
    def dict(self):
        return self._dict

    @property
    def db_dsn(self):
        from .urls import make_settings_dsn
        return make_settings_dsn(self)

    def _substitute_environ(self, custom_settings):
        """
        Substitute environment variables into settings.
        """
        d = {}
        for attr_name in dir(self):
            if attr_name.startswith('_') or attr_name.upper() != attr_name:
                continue

            orig_value = getattr(self, attr_name)

            if isinstance(orig_value, Setting):
                is_required = orig_value.required
                default = orig_value.default
                orig_type = orig_value.v_type
                env_var_name = orig_value.env_var_name
            else:
                default = orig_value
                is_required = False
                orig_type = type(orig_value)
                env_var_name = self._ENV_PREFIX + attr_name

            env_var = os.getenv(env_var_name, None)
            d[attr_name] = default

            if env_var is not None:
                if issubclass(orig_type, bool):
                    env_var = env_var.upper() in ('1', 'TRUE')
                elif issubclass(orig_type, int):
                    env_var = int(env_var)
                elif issubclass(orig_type, Path):
                    env_var = Path(env_var)
                elif issubclass(orig_type, bytes):
                    env_var = env_var.encode()
                elif issubclass(orig_type, str) and env_var.startswith('py::'):
                    env_var = self._import_string(env_var[4:])
                elif issubclass(orig_type, (list, tuple, dict)):
                    # TODO more checks and validation
                    env_var = json.loads(env_var)
                d[attr_name] = env_var
            elif is_required and attr_name not in custom_settings:
                raise RuntimeError('The required environment variable "{0}" is currently not set, '
                                   'you\'ll need to set the environment variable with '
                                   '`export {0}="<value>"`'.format(env_var_name))
        return d

    def _get_custom_settings(self, custom_settings):
        d = {}
        for name, value in custom_settings.items():
            if not hasattr(self, name):
                raise TypeError('{} is not a valid setting name'.format(name))
            d[name] = value
        return d

    @classmethod
    def _import_string(cls, dotted_path):
        """
        Stolen from django. Import a dotted module path and return the attribute/class designated by the
        last name in the path. Raise ImportError if the import failed.
        """
        try:
            module_path, class_name = dotted_path.strip(' ').rsplit('.', 1)
        except ValueError as e:
            raise ImportError("{} doesn't look like a module path".format(dotted_path)) from e

        module = import_module(module_path)
        try:
            return getattr(module, class_name)
        except AttributeError as e:
            raise ImportError('Module "{}" does not define a "{}" attribute'.format(module_path, class_name)) from e

    def __iter__(self):
        # so `dict(settings)` works
        yield from self._dict.items()

    def __repr__(self):
        return '<Settings {}>'.format(' '.join('{}={!r}'.format(k, v) for k, v in self.dict.items()))
