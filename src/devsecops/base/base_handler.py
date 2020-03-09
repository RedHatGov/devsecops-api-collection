#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause

import requests
import json
import sys
import logging
import logging.handlers
from time import sleep
from typing import TypeVar
import urllib3
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
                 password: str = None, verbosity: int = 0) -> None:
        """
        Initialize the base class
        """
        self._set_logger(service_name, verbose)
        if base_url is not None and base_endpoint is not None:
            self.url: str = f'{base_url}/{base_endpoint}'
        if username is not None:
            self.username: str = username
        if password is not None:
            self.password: str = password

    def _set_logger(self, service_name: str = None,
                    verbosity: int = 0) -> None:
        """
        Start a logger unique to each API handler
        """
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.DEBUG)
        _format = '{asctime} {name} [{levelname:^9s}]: {message}'
        formatter = logging.Formatter(_format, style='{')

        stderr = logging.StreamHandler()
        stderr.setFormatter(formatter)
        syslog = logging.handlers.SysLogHandler(address='/dev/log')
        syslog.setFormatter(formatter)

        # When verbose, output lots of log information to stderr
        verbosity = verbosity * 10
        stderr.setLevel(max(50, min(10, 40 - verbosity)))

        # Always be pretty verbose to syslog
        syslog.setLevel(logging.INFO)

        self.logger.addHandler(stderr)
        self.logger.addHandler(syslog)

    def __enter__(self) -> T:
        """
        Context manager enter
        """
        self.sign_in()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        """
        Context manager exit
        """
        self.sign_out()

    def _sign_in(self, signin_endpoint: str = None,
                 extra_headers: dict = {}) -> bool:
        """
        Base sign in content that's similar regardless of subclass
        """
        self.session = requests.session()
        self.session.verify = False
        self.session.headers.update(
            {
                'Content-type': 'application/json',
                'Accept': 'application/json, text/plain'
            }
        )
        return json.loads(self.api_req(
            'post', signin_endpoint
        ).text).get('valid')

    def sign_in(self, new_password):



        if signed_in and new_password is not None:
            # Need to update password
            signed_in = self.change_password(new_password)
        elif not signed_in and new_password is not None:
            # Maybe we already updated
            self.password = new_password
            signed_in = json.loads(
                self.api_req('post', 'authentication/validate').text
            ).get('valid')
        else:
            # A new password wasn't set
            pass

        if not signed_in:
            # This includes trying both passwords
            raise UnexpectedApiResponse(
                'Failed to log in with provided credentials'
            )
        return signed_in

    def sign_out(self):
        ret_val = self.api_req('post', 'authentication/logout')
        self.session.close()
        return ret_val

    def api_req(self, method_name, endpoint, data=None, ok=200):
        method = getattr(self.session, method_name)

        if data is None:
            ret_val = method(f'{self.url}/{endpoint}',
                             auth=(self.username, self.password))
        else:
            ret_val = method(f'{self.url}/{endpoint}', params=data,
                             auth=(self.username, self.password))

        self.logger.info(f'{method_name} at {self.url}/{endpoint} returned {ret_val.status_code}')
        self.logger.debug(f'text: {ret_val.text}')
        self.logger.debug(f'headers: {ret_val.headers}')

        if ret_val.status_code != ok:
            raise UnexpectedApiResponse(ret_val.text)
        return ret_val

    def add_user(self, username, password):
        if not self.search_user(username):
            try:
                return self.api_req('post', 'users/create', data={
                    'login': username,
                    'password': password,
                    'name': username
                })
            except UnexpectedApiResponse as e:
                self.logger.error(f'Error adding {username}, response:')
                self.logger.error('  ' + json.loads(str(e))['error_message'])
                sys.stderr.flush()
                pass

    def change_password(self, new_password):
        if self.api_req('post', 'users/change_password',
                        data={'login': self.username,
                              'previousPassword': self.password,
                              'password': new_password}, ok=204):
            self.logger.info('Updating session password with new')
            self.password = new_password
            return True
        else:
            return False

    def search_user(self, username):
        response = self.api_req('post', 'users/search', data={'q': username})
        return json.loads(response.text).get('users')

if __name__ == '__main__':
    from argparse import ArgumentParser
    description = """
    Creates local database users in a SonarQube instance when provided with
    admin credentials and the base URL of the web interface. Only uses one API
    session to do so and reuses it for all requests.
    """
    epilog = """
    NOTE: the number of users and passwords to create must be equal. You can
    specify them in any order you wish, but they will be paired up in the order
    in which they were received for creation.
    """
    parser = ArgumentParser(description=description, epilog=epilog)
    parser.add_argument(
        'url', metavar='URL',
        help='the URL of SonarQube, not including anything after the TLD'
    )
    parser.add_argument(
        '--login-username', '-U', required=True,
        help='the username with which to log in to SonarQube'
    )
    parser.add_argument('--login-password', '-P', required=True,
                        help='the password for the login user')
    parser.add_argument('--new-login-password', '-N', required=False,
                        help='a new password to set for the login user')
    parser.add_argument(
        '--username', '-u', action='append',
        help=('a username to add to SonarQube '
              '(may be specified multiple times)')
    )
    parser.add_argument(
        '--password', '-p', action='append',
        help=('a password for the last username provided '
              '(may be specified multiple times)')
    )
    parser.add_argument(
        '--debug', '-d', action='store_true',
        help='enables Debug output on STDERR'
    )
    args = parser.parse_args()

    if args.username is not None and args.password is not None and \
                        len(args.username) != len(args.password):
        sys.stderr.write('You must provide the same number of usernames and '
                         'passwords in order to create users with this tool.\n')
        sys.stderr.flush()
        exit(1)
    try:
        if requests.get(args.url, verify=False).status_code != 200:
            sys.stderr.write(f'{args.url} appears to be offline and is not '
                             'responding to requests.\n')
            sys.stderr.flush()
            exit(1)
    except requests.exceptions.SSLError:
        sys.stderr.write(f'{args.url} appears to be offline and is not '
                         'responding to requests.\n')
        sys.stderr.flush()
        exit(1)

    with SonarQube(args.url, args.login_username,
                   args.login_password, args.new_login_password,
                   args.debug) as sq:
        if args.username is not None and args.password is not None:
            for username, password in zip(args.username, args.password):
                if sq.add_user(username, password):
                    print(f'{username} added')
