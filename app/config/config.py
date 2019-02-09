import logging
from configparser import ConfigParser
from os.path import dirname, abspath, join
from os import getenv

CONFIG_FILE_ENV = 'DDDC_CREDENTIAL_ISSUER_CONFIGFILE'
DEFAULT_CONFIG_FILENAME = 'config.ini'


class BaseConfig(object):
    def __init__(self):
        self._directory = dirname(dirname(abspath(__file__)))
        _default_config = join(self._directory, DEFAULT_CONFIG_FILENAME)
        self._config_file = getenv(CONFIG_FILE_ENV, _default_config)

    def parse_config(self):
        log = self.logger
        config_parser = ConfigParser()
        _config_files = config_parser.read(self._config_file)
        if _config_files:
            log.info('Correctly loading configuration from => %s' % self._config_file)
        else:
            raise RuntimeError('No configuration file was found. Please set following environment variable "%s" '
                               'containing the path to the configuration file' % CONFIG_FILE_ENV)
        return config_parser

    @property
    def values(self):
        return self.parse_config()

    @property
    def logger(self):
        return logging.getLogger('gunicorn.error')
