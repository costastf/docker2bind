#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# File: modules.py
"""
Here are all the modules

"""

import logging
from dns.resolver import Resolver
from dns.exception import DNSException
import dns.tsigkeyring
import dns.update

LOGGER_BASENAME = '''docker2bind'''
LOGGER = logging.getLogger(LOGGER_BASENAME)


class Container(object):
    def __init__(self, configuration):
        self.configuration = configuration
        self.container_ip = None

    @property
    def hostname(self):
        return self.configuration['Config']['Hostname']

    @property
    def name(self):
        return self.configuration['Name'].split('/', 1)[1]

    @property
    def network_mode(self):
        return self.configuration['HostConfig']['NetworkMode']

    @property
    def ip(self):
        if self.network_mode == 'default':
            return self.configuration['NetworkSettings']['IPAddress']
        else:
            networks = self.configuration['NetworkSettings']['Networks']
            return networks[self.network_mode]['IPAddress']

    @property
    def id(self):
        return self.configuration['Id']

    @property
    def short_id(self):
        return self.configuration['Id'][:12]


class BindServer(object):
    def __init__(self, ip, domain, key, zone=None, overwrite_container_ip=True):
        self.logger = logging.getLogger('{base}.{suffix}'.
                                        format(base=LOGGER_BASENAME,
                                               suffix=self.__class__.__name__))
        self.ip = ip
        self.domain = domain
        self.key = key
        self.zone = zone or domain
        self.keyring = dns.tsigkeyring.from_text({domain: key})
        self._overwrite_ip = overwrite_container_ip
        self._resolver = Resolver()
        self._resolver.nameservers = [ip]

    def _get_hostname(self, container):
        return '{hostname}.{domain}.'.format(hostname=container.hostname,
                                             domain=self.domain)

    def _get_alias(self, container):
        return '{name}.{domain}.'.format(name=container.name,
                                         domain=self.domain)

    def register(self, container):
        update = dns.update.Update(self.domain, keyring=self.keyring)
        hostname = self._get_hostname(container)
        print(hostname)
        alias = self._get_alias(container)
        ip = self.ip if self._overwrite_ip else container.ip
        self.logger.info('Updating {}|{} to ip {}'.format(container.hostname,
                                                          container.name,
                                                          ip))
        update.add(hostname, '60', 'A', ip)
        self.logger.debug('Setting alias to {}'.format(alias))
        update.add(alias, '600', 'CNAME', hostname)
        update.add(hostname, '600', 'TXT', '"DDNS-ALIAS:{}"'.format(alias))
        return self._submit_query(update)

    def delete(self, container):
        update = dns.update.Update(self.domain, keyring=self.keyring)
        self.logger.info('Removing entry for {}'.format(container.hostname))
        hostname = self._get_hostname(container)
        alias = self._get_alias(container)
        self.logger.debug('Looking for alias {}'.format(alias))
        try:
            answers = self._resolver.query(hostname,
                                           "TXT",
                                           raise_on_no_answer=False).rrset
            records_to_delete = [answer.to_text().split()[0]
                                 for answer in answers
                                 if 'DDNS-ALIAS' in answer.to_text()]
            for record in records_to_delete:
                update = dns.update.Update(self.domain, keyring=self.keyring)
                update.delete(record)
        except DNSException:
            message = "Can't get TXT record for {}".format(hostname)
            self.logger.exception(message)
        return self._submit_query(update)

    def _submit_query(self, update):
        self.logger.debug('Submitting update {}'.format(update.to_text()))
        response = dns.query.tcp(update, self.ip)
        if 'NOERROR' not in response.to_text():
            self.logger.error(('Could not update, '
                               'response:{}').format(response.to_text()))
            return False
        else:
            self.logger.debug('Received response {}'.format(response.to_text()))
            return True
