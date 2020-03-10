#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
from devsecops.base.base_handler import BaseApiHandler, UnexpectedApiResponse
from typing import TypeVar
import requests
import json

T = TypeVar("T", bound="Quay")


class Quay(BaseApiHandler):
    def __init__(self, base_url: str = None, username: str = None,
                 password: str = None, verbosity: int = 0) -> None:
        """
        Initialize a Quay API wrapper with logging, url information, and other
        necessary variables to track state.
        """
        super().__init__(
            service_name='Quay',
            base_url=base_url,
            username=username,
            password=password,
            verbosity=verbosity
        )
        self.base_url = base_url

    def sign_in(self) -> requests.Response:
        """
        Sign in to a Quay API instance with CSRF token handling.
        """
        self.session = requests.session()
        self.session.verify = False
        load_login = self.session.get(self.base_url)
        for line in load_login.text.split('\n'):
            if '__token' in line:
                token = line.split("'")[1]
                break
        self._get_session(extra_headers={'X-CSRF-Token': token})

        return self.api_req('post', 'signin', data={
            'username': self.username,
            'password': self.password
        })

    def api_req(self, method_name: str = None, endpoint: str = None,
                data: dict = None) -> requests.Response:
        """
        Wrap API requests with next-CSRF tokens from the last request.
        """
        ret_val = super().api_req(method_name=method_name, endpoint=endpoint,
                                  data=data)
        token = ret_val.headers.get('X-Next-CSRF-Token')
        if token is not None:
            self.session.headers.update({'X-CSRF-Token': token})
        return ret_val

    def add_user(self, username: str = None,
                 password: str = None) -> requests.Response:
        """
        Add a user to the Quay instance, returning None if no user was created.
        """
        try:
            return self.api_req('post', 'user', data={'username': username,
                                                      'password': password})
        except UnexpectedApiResponse as e:
            self.logger.warning(f'Unable to add {username}')
            self.logger.info(json.loads(str(e)).get('error_message'))
            pass
