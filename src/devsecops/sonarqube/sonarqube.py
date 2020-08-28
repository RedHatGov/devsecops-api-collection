#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
from devsecops.base.base_handler import BaseApiHandler, UnexpectedApiResponse
from typing import TypeVar
from time import sleep
import requests
import json

T = TypeVar("T", bound="SonarQube")


class SonarQube(BaseApiHandler):
    def __init__(self, base_url: str = None, username: str = None,
                 password: str = None, verbosity: int = 0,
                 new_password: str = None) -> None:
        """
        Initialize a SonarQube API wrapper with logging, URL information, and
        other necessary variables to track state
        """
        super().__init__(
            service_name='SonarQube',
            base_url=base_url,
            base_endpoint='api',
            username=username,
            password=password,
            verbosity=verbosity,
            auth=True,
            kwarg_type='params'
        )
        self.new_password = new_password
        self.old_password = None

    def _sign_in(self) -> bool:
        """
        Sign in to SonarQube and return whether login was valid
        """
        return json.loads(
            self.api_req('post', 'authentication/validate').text
        ).get('valid')

    def _swap_passwords(self) -> None:
        """
        Swap new_password, password, and old_password around to try other login
        options to maximize idempotency of templated API calls via CLI
        """
        if self.old_password is None and self.new_password is not None:
            self.old_password = self.password
            self.password = self.new_password
            self.new_password = None
            self.logger.debug('Changed to new_password')
        elif self.new_password is None and self.old_password is not None:
            self.new_password = self.password
            self.password = self.old_password
            self.old_password = None
            self.logger.debug('Changed to old_password')

    def sign_in(self) -> None:
        """
        Tries to sign in to Nexus 4 times, swapping the new_password in and out
        as necessary, in case it was changed already, with a 3-second delay
        in between to account for SonarQube not instantiating the built-in
        admin user right away.
        """
        self._get_session()
        tries = 4
        while not self._sign_in():
            self._swap_passwords()
            if tries == 0:
                raise UnexpectedApiResponse('Unable to log in to SonarQube')
            tries -= 1
            sleep(3)
        if self.new_password is not None:
            self.api_req('post', 'users/change_password',
                         data={'login': self.username,
                               'previousPassword': self.password,
                               'password': self.new_password}, ok=[204])
            self._swap_passwords()
            self.sign_out()
            self._get_session()
            if not self._sign_in():
                raise UnexpectedApiResponse(
                    'Unable to log back in after changing password'
                )

    def sign_out(self) -> requests.Response:
        """
        Sign out of SonarQube
        """
        return self._sign_out(signout_endpoint='authentication/logout')

    def add_user(self, username: str = None,
                 password: str = None) -> requests.Response:
        """
        Adds a user to SonarQube
        """
        try:
            return self.api_req('post', 'users/create', data={
                'login': username,
                'password': password,
                'name': username
            })
        except UnexpectedApiResponse as e:
            self.logger.error(f'Error adding {username}')
            self.logger.error(json.loads(str(e))['error_message'])
            pass

    def search_users(self, username: str = None) -> list:
        """
        Searches for a user in SonarQube, returns results as a list
        """
        try:
            return json.loads(
                self.api_req('post', 'users/search', data={'q': username}).text
            ).get('users')
        except UnexpectedApiResponse as e:
            self.logger.warning(f'No response from query for  {username}')
            self.logger.warning(json.loads(str(e))['error_message'])
            pass

    def update_setting(self, setting_name: str,
                       setting_value: str = None) -> requests.Response:
        """
        Update a  SonarQube setting
        """
        try:
            return self.api_req('post', 'settings/set', data={
                'key': setting_name,
                'value': setting_value
            }, ok=[204])
        except UnexpectedApiResponse:
            self.logger.error(
                f'Error setting {setting_name} to value {setting_value}'
            )
            self.logger.exception("Update setting error", exc_info=True)
            pass
