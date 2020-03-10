#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause

from devsecops.base.base_handler import BaseApiHandler, UnexpectedApiResponse
from typing import TypeVar
from base64 import b64encode
import requests
import json

T = TypeVar("T", bound="Nexus")


class Nexus(BaseApiHandler):
    def __init__(self, base_url: str = None, username: str = None,
                 password: str = None, verbosity: int = 0) -> None:
        """
        Initialize a Nexus API wrapper with logging, url information, and other
        necessary variables to track state.
        """
        super().__init__(
            service_name='Nexus',
            base_url=base_url,
            base_endpoint='service/rest',
            username=username,
            password=password,
            verbosity=verbosity,
            auth=True
        )
        self.base_url = base_url

    def sign_in(self) -> None:
        """
        Sign in to a Nexus API instance with appropriate encoding
        """
        self._get_session()

        b64_username = b64encode(self.username.encode('utf-8'))
        b64_password = b64encode(self.password.encode('utf-8'))
        login_data = {
            'u': b64_username.decode('ascii'),
            'p': b64_password.decode('ascii')
        }
        token = json.loads(self.api_req('post', 'wonderland/authenticate',
                                        data=login_data).text).get('t')
        self.session.headers.update({'X-NX-AuthTicket': token})

    def sign_out(self) -> None:
        """
        Just close the Nexus API session
        """
        self.session.close()

    def add_user(self, username: str = None,
                 password: str = None) -> requests.Response:
        """
        Add a user to the Nexus instance, returning None if no user was created
        """
        data = {
            'userId': username,
            'firstName': username,
            'lastName': username,
            'password': password,
            'emailAddress': f'{username}@example.com',
            'status': 'active',
            'roles': ['nx-admin']
        }
        try:
            return self.api_req('post', 'beta/security/users', data)
        except UnexpectedApiResponse as e:
            self.logger.error(f'Error adding {username}')
            self.logger.info(json.loads(str(e)).get('error_message'))

    def list_users(self) -> list:
        """
        Lists all users currently on the server
        """
        return json.loads(self.api_req(endpoint='beta/security/users').text)

    def search_users(self, user) -> list:
        """
        Returns information about the queried users as a list of results
        """
        return json.loads(
            self.api_req('get', f'beta/security/users?userId={user}').text
        )

    def create_repo(self, username) -> requests.Response:
        data = {
            'name': username,
            'oneline': True,
            'storage': {
                'blobStoreName': 'default',
                'strictContentTypeValidation': True,
                'writePolicy': 'allow_once'
            },
            'cleanup': {
                'policyName': 'weekly-cleanup'
            },
            'maven': {
                'versionPolicy': 'mixed',
                'layoutPolicy': 'strict'
            }
        }
        return self.api_req('post', 'beta/repositories/maven/hosted', data)
