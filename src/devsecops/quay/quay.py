#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
from devsecops.base.base_handler import BaseApiHandler, UnexpectedApiResponse
from typing import TypeVar, List
import requests
import json
import random
import string

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
                data: dict = None, ok: List[int] = [200]) -> requests.Response:
        """
        Wrap API requests with next-CSRF tokens from the last request.
        """
        ret_val = super().api_req(method_name=method_name, endpoint=endpoint,
                                  data=data, ok=ok)
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

    def add_org(self, org_name: str = None) -> requests.Response:
        """
        Add an Organization to the Quay instance, returning None if no
        organization was created.
        """
        try:
            return self.api_req('post', 'organization', data={
                'name': org_name,
                'email': 'devsecops_{}@{}'.format(
                    ''.join(random.choice(string.ascii_letters)
                            for i in range(10)),
                    '.'.join(
                        self.base_url.strip('/').split('/')[-1].split('.')[-2:]
                    )
                )
            }, ok=[201])
        except UnexpectedApiResponse as e:
            self.logger.warning(f'Unable to add {org_name}')
            self.logger.info(json.loads(str(e)).get('error_message'))
            pass

    def add_app(self, org_name: str = None, app_name: str = None,
                description: str = None) -> requests.Response:
        """
        Add an Application to an Organization on the Quay instance, returning
        None if no application was created.
        """
        try:
            return self.api_req(
                'post',
                f'organization/{org_name}/applications',
                data={
                    'name': app_name,
                    'description': description or "Created with devsecops-api"
                }
            )
        except UnexpectedApiResponse as e:
            self.logger.warning(f'Unable to add {app_name}')
            self.logger.info(json.loads(str(e)).get('error_message'))
            pass

    def add_repo(self, org_name: str = None, repo_name: str = None,
                description: str = None) -> requests.Response:
        """
        Add a Repository to an Organization on the Quay instance.
        """
        try:
            return self.api_req(
                'post',
                'repository',
                data={
                    'repo_kind': 'image',
                    'namespace': org_name,
                    'visibility': 'public',
                    'repository': repo_name,
                    'description': description or "Created with devsecops-api"
                }
            )
        except UnexpectedApiResponse as e:
            self.logger.warning(f'Unable to add {repo_name}')
            self.logger.info(json.loads(str(e)).get('error_message'))
            pass

    def get_robot(self, org_name: str = None,
                  robot_name: str = None) -> requests.Response:
        """
        Returns the response from the API server about a given robot account,
        returning None if no robot is present.
        """
        try:
            return self.api_req(
                'get',
                f'organization/{org_name}/robots/{robot_name}',
            )
        except UnexpectedApiResponse as e:
            self.logger.warning(f'Unable to find {robot_name}')
            self.logger.info(json.loads(str(e)).get('error_message'))
            pass

    def add_robot(self, org_name: str = None, robot_name: str = None,
                  description: str = None) -> requests.Response:
        """
        Add a robot account to an Organization on the Quay instance, returning
        None if no robot was created.
        """
        try:
            return self.api_req(
                'put',
                f'organization/{org_name}/robots/{robot_name}',
                data={
                    'description': description or
                    "Created with devsecops-api",
                },
                ok=[200, 201]
            )
        except UnexpectedApiResponse as e:
            self.logger.warning(f'Unable to add {robot_name}')
            self.logger.info(json.loads(str(e)).get('error_message'))
            pass
