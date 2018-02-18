import os
from importlib import import_module


class ConfigurationError(Exception):
    pass


try:
    settings_module_name = os.environ['SETTINGS_MODULE']
except KeyError:
    raise ConfigurationError('You have to specify SETTINGS_MODULE env variable.')

settings = import_module(settings_module_name)

__all__ = ['settings']
