# SPDX-License-Identifier: BSD-2-Clause
from devsecops.cli import opts
from devsecops.cli import dso_sonarqube
from devsecops.sonarqube import sonarqube

import click


@dso_sonarqube.command(name='add-user', epilog=opts.add_users_epilog)
@opts.default_opts
@opts.add_users_opt
@opts.new_login_pw_opt
def dso_sonarqube_add_user(url, login_username, login_password, verbose,
                           usernames, passwords, new_login_password):
    """Add users to the SonarQube instance specified by URL"""
    exit_code = 0
    with sonarqube.SonarQube(
        url, login_username, login_password, verbosity=verbose,
        new_password=new_login_password
    ) as api:
        for username, password in zip(usernames.split(','),
                                      passwords.split(',')):
            if api.search_users(username):
                print(f'{username} ok')
                continue
            new_user = api.add_user(username, password)
            if new_user is not None:
                print(f'{username} added')
            else:
                exit_code += 1
                print(f'{username}: failed')
    exit(exit_code)


@dso_sonarqube.command(name='search-user')
@opts.default_opts
@opts.search_user_opt
@opts.new_login_pw_opt
def dso_sonarqube_search_user(url, login_username, login_password, verbose,
                              username, new_login_password):
    """
    Search for users by username on the SonarQube instance specified by URL
    """
    from pprint import pprint

    with sonarqube.SonarQube(
        url, login_username, login_password, verbosity=verbose,
        new_password=new_login_password
    ) as api:
        pprint(api.search_users(username))


@dso_sonarqube.command(name='update-setting')
@opts.default_opts
@opts.new_login_pw_opt
@click.option('--setting-name', '-n', required=True,
              help=('the name of the setting to update '))
@click.option('--setting-value', '-u', required=True,
              help=('the new value of the setting to update '))
def dso_sonarqube_update_setting(url, login_username, login_password,
                                 verbose, new_login_password,
                                 setting_name, setting_value):
    """
    Change a setting in the SonarQube instance specified by URL
    """
    from pprint import pprint

    with sonarqube.SonarQube(
        url, login_username, login_password, verbosity=verbose,
        new_password=new_login_password
    ) as api:
        pprint(api.update_setting(setting_name, setting_value))
