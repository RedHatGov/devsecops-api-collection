# SPDX-License-Identifier: BSD-2-Clause
import click
import requests

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
