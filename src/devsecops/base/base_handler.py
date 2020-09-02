#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause

from typing import TypeVar, List
import requests
import json
import logging
import logging.handlers
import sys
import urllib3
import os.path
urllib3.disable_warnings()


T = TypeVar("T", bound="BaseApiHandler")


class UnexpectedApiResponse(Exception):
    pass


class BaseApiHandler(object):
    """
    Base class for API handlers for the various services with common
    methodologies for them.
    """

    def __init__(self, service_name: str = None, base_endpoint: str = 'api/v1',
                 base_url: str = None, username: str = None,
                 password: str = None, verbosity: int = 0, auth: bool = False,
                 kwarg_type: str = 'data') -> None:
        """
        Initialize the base class
        """
        self._set_logger(service_name, verbosity)
        if not self.check_online(base_url):
            msg = (
                f'{base_url} is providing unexpected responses to requests. '
                'Please ensure you have the correct protocol and base URL for '
                'the service.'
            )
            self.logger.error(msg)
            raise UnexpectedApiResponse(msg)
        if base_url is not None and base_endpoint is not None:
            self.url: str = f'{base_url}/{base_endpoint}'
        if username is not None:
            self.username: str = username
        if password is not None:
            self.password: str = password
        self.auth = auth
        self.kwarg_type = kwarg_type
        self.session = None

    def _set_logger(self, service_name: str = None,
                    verbosity: int = 0) -> None:
        """
        Start a logger unique to each API handler
        """
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.DEBUG)
        _format = '{asctime} [{levelname:^9s}] {name}: {message}'
        formatter = logging.Formatter(_format, style='{')

        stderr = logging.StreamHandler()
        stderr.setFormatter(formatter)

        # When verbose, output lots of log information to stderr
        verbosity = min(50, max(10, 40 - verbosity * 10))
        stderr.setLevel(verbosity)

        self.logger.addHandler(stderr)

        if os.path.exists('/dev/log'):
            syslog = logging.handlers.SysLogHandler(address='/dev/log')
            syslog.setFormatter(formatter)

            # Always be pretty verbose to syslog
            syslog.setLevel(logging.INFO)

            self.logger.addHandler(syslog)

        self.logger.info(f'Logging initialized, verbosity: {verbosity}')

    def __enter__(self) -> T:
        """
        Context manager enter
        """
        self.sign_in()
        self.logger.debug(
            f'Context manager sign-in complete for {self.__class__}'
        )
        self.logger.debug(f'Vars dump for {self.__class__}')
        self.logger.debug(vars(self))
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Context manager exit
        """
        self.sign_out()
        self.logger.debug(
            f'Context manager sign-out complete for {self.__class__}'
        )

    @staticmethod
    def check_online(url):
        try:
            if requests.get(url, verify=False).status_code != 200:
                sys.stderr.write(f'{url} appears to be offline and is not '
                                 'responding to requests.\n')
                sys.stderr.flush()
                return False
        except requests.exceptions.SSLError:
            sys.stderr.write(f'{url} appears to be offline and is not '
                             'responding to requests.\n')
            sys.stderr.flush()
            return False
        return True

    def _get_session(self, extra_headers: dict = {}) -> None:
        """
        Base session content that's similar regardless of subclass
        """
        if self.session is None:
            self.logger.debug('Creating new session')
            self.session = requests.session()
            self.session.verify = False
        self.session.headers.update(
            {
                'Content-type': 'application/json',
                'Accept': 'application/json, text/plain'
            }
        )
        for key, val in extra_headers.items():
            self.session.headers.update({key: val})

    def sign_in(self) -> requests.Response:
        """
        Intended to be overloaded by subclasses to hit appropriate endpoints,
        provide necessary headers dict, and do any post-session but pre-signin
        manipulation required.
        """
        self._get_session()
        return(self.api_req('post', 'signin'))

    def _sign_out(self, signout_endpoint: str = 'signout') -> requests.Response:  # noqa: E501
        """
        Base sign out content that's similar regardless of subclass
        """
        ret_val = self.api_req('post', signout_endpoint)
        self.session.close()
        return ret_val

    def sign_out(self) -> requests.Response:
        """
        Intended to be overloaded by subclasses to hit appropriate endpoints
        """
        return self._sign_out()

    def api_req(self, method_name: str = 'get', endpoint: str = '',
                data: dict = None, ok: List[int] = [200]) -> requests.Response:
        """
        Generic API request functionality for all other calls.

        If return is expected to be anything other than `200` for success,
        provide the HTTP response code as `ok`.
        """
        self.logger.debug('Making API request:')
        self.logger.debug(locals())
        method = getattr(self.session, method_name)
        kwargs = {}
        if self.auth:
            kwargs['auth'] = (self.username, self.password)
        if data is not None:
            if self.kwarg_type == 'data':
                kwargs[self.kwarg_type] = json.dumps(data)
            elif self.kwarg_type == 'params':
                kwargs[self.kwarg_type] = data
        ret_val = method(f'{self.url}/{endpoint}', **kwargs)

        self.logger.info((f'{method_name} at {self.url}/{endpoint} '
                          f'returned {ret_val.status_code}'))
        self.logger.debug(f'text: {ret_val.text}')
        self.logger.debug(f'headers: {ret_val.headers}')
        self.logger.debug(f'data: {data}')

        if ret_val.status_code not in ok:
            raise UnexpectedApiResponse(ret_val.text)
        return ret_val
