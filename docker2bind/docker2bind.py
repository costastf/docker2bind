#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# File: docker2bind.py
"""
Main module file

main() will be called by scripts
"""

from docker import Client
from docker.utils import kwargs_from_env
from modules import BindServer, Container
import logging
import logging.handlers
import logging.config
import json
import argparse

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = 'plaintext'
__date__ = '''9-3-2016'''

# This is the main prefix used for logging
LOGGER_BASENAME = '''docker2bind'''
LOGGER = logging.getLogger(LOGGER_BASENAME)


def get_arguments():
    """
    This get us the cli arguments.

    Returns the args as parsed from the argsparser.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(
        description=('''A tool to dynamically update a bind9 server with
        records based on docker events'''))
    parser.add_argument('--log-config',
                        '-l',
                        action='store',
                        dest='logger_config',
                        help='The location of the logging config json file',
                        default='')
    parser.add_argument('--log-level',
                        '-L',
                        help='Provide the log level. Defaults to INFO.',
                        dest='log_level',
                        action='store',
                        default='INFO',
                        choices=['DEBUG',
                                 'INFO',
                                 'WARNING',
                                 'ERROR',
                                 'CRITICAL'])
    parser.add_argument('--log-file',
                        help='The file to log into.',
                        dest='log_file',
                        default='./docker-ddns.log')
    parser.add_argument('--key',
                        '-k',
                        dest='key',
                        required=True,
                        help='The dns key')
    parser.add_argument('--server',
                        '-s',
                        dest='server',
                        help='IP/Hostname of the server to update',
                        required=True)
    parser.add_argument('--domain',
                        '-d',
                        dest='domain',
                        help='The domain to be updated',
                        required=True)
    parser.add_argument('--zone',
                        '-z',
                        dest='zone',
                        help='The zone to be updated (defaults to the domain)',
                        default=None)
    parser.add_argument('--register-running',
                        '-r',
                        dest='register_running',
                        help='Register the running containers on startup',
                        default=False,
                        action="store_true")
    args = parser.parse_args()
    args.zone = args.zone or args.domain
    return args


def setup_logging(args):
    """
    This sets up the logging.

    Needs the args to get the log level supplied
    :param args: The command line arguments
    """
    # This will configure the logging, if the user has set a config file.
    # If there's no config file, logging will default to stdout.
    if args.logger_config:
        # Get the config for the logger. Of course this needs exception
        # catching in case the file is not there and everything. Proper IO
        # handling is not shown here.
        config = json.loads(open(args.logger_config).read())
        # Configure the logger
        logging.config.dictConfig(config)
    else:
        global LOGGER
        handler = logging.StreamHandler()
        handler.setLevel(args.log_level)
        formatter = logging.Formatter(('%(asctime)s - '
                                       '%(name)s - '
                                       '%(levelname)s - '
                                       '%(message)s'))
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)


def main():
    """
    Main method.

    This method holds what you want to execute when
    the script is run on command line.
    """
    args = get_arguments()
    setup_logging(args)

    docker_server = Client(**(kwargs_from_env()))
    LOGGER.debug(('Setting up a bind server with '
                  'ip {} for domain {} and zone {}').format(args.server,
                                                            args.domain,
                                                            args.zone))
    bind = BindServer(args.server, args.domain, args.key, args.zone)

    if args.register_running:
        LOGGER.info('Registering existing containers')
        containers = docker_server.containers()
        for configuration in containers:
            container = Container(configuration)
            LOGGER.debug(('Registering container with '
                          'hostname {} and id {}').format(container.hostname,
                                                          container.id))
            bind.register(container)

    for event in docker_server.events():
        data = json.loads((event.decode('utf-8')))
        status = data.get('status', False)
        if status in ('start', 'destroy', 'die'):
            LOGGER.debug('Got status {}'.format(status))
            details = docker_server.inspect_container(data.get('id'))
            container = Container(details)
            if status == 'start':
                LOGGER.info('Trying to add {}'.format(container.hostname))
                bind.register(container)
            elif status in ('destroy', 'die'):
                LOGGER.info('Trying to delete {}'.format(container.hostname))
                bind.delete(container)


if __name__ == '__main__':
    main()
