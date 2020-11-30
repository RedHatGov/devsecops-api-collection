# SPDX-License-Identifier: BSD-2-Clause
import click

add_users_epilog = """
NOTE: the number of users and passwords to create must be equal. You can
specify them in any order you wish, but they will be paired up in the order
in which they were received for creation.
"""


def url_arg(f):
    return click.argument('url', metavar='URL')(f)


def login_user_opt(f):
    return click.option('--login-username', '-U', required=True,
                        help='the username with which to log in')(f)


def login_pw_opt(f):
    return click.option('--login-password', '-P', required=True,
                        help='the password for the login user')(f)


def add_users_opt(f):
    for option in reversed([
        click.option('--usernames', '-u', required=True,
                     help=('usernames to add to the service '
                           '(separate multiples with commas)')),
        click.option('--passwords', '-p', required=True,
                     help=('a password for the last username provided '
                           '(separate multiples with commas)'))
    ]):
        f = option(f)
    return f


def add_orgs_opt(f):
    return click.option('--organizations', '-o', required=True,
                        help=('organizations to add to the service '
                              '(separate multiples with commas)'))(f)


def add_org_opt(f):
    return click.option('--organization', '-o', required=True,
                        help='the organization to add the app to')(f)


def add_app_opt(f):
    for option in reversed([
        add_org_opt,
        click.option('--app-name', '-a', required=True,
                     help='the application to add to the org'),
        click.option('--app-description', '-d', required=False,
                     help='the description of the application'),
    ]):
        f = option(f)
    return f


def add_repo_opt(f):
    for option in reversed([
        add_org_opt,
        click.option('--repo-name', '-n', required=True,
                     help='the repository to add to the org'),
        click.option('--repo-description', '-d', required=False,
                     help='the description of the repository'),
    ]):
        f = option(f)
    return f


def add_robot_opt(f):
    for option in reversed([
        add_org_opt,
        click.option('--robot-name', '-r', required=True,
                     help='the robot name to add to the org'),
        click.option('--robot-description', '-d', required=False,
                     help='the description of the robot account'),
    ]):
        f = option(f)
    return f


def new_login_pw_opt(f):
    return click.option('--new-login-password', '-N', required=False,
                        help='a new password for the login user')(f)


def verbose_opt(f):
    return click.option('-v', '--verbose', count=True,
                        help=('Increase verbosity '
                              '(specify multiple times for more)'))(f)


def search_user_opt(f):
    return click.option('--username', '-u',
                        help='the username to search for')(f)


def default_opts(f):
    for option in reversed([
        url_arg,
        login_user_opt,
        login_pw_opt,
        verbose_opt
    ]):
        f = option(f)
    return f
