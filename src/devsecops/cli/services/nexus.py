# SPDX-License-Identifier: BSD-2-Clause
from devsecops.cli import opts
from devsecops.cli import dso_nexus
from devsecops.nexus import nexus

from pprint import pprint
import click
import sys


@dso_nexus.command(name='add-user', epilog=opts.add_users_epilog)
@opts.default_opts
@opts.add_users_opt
def dso_nexus_add_user(url, login_username, login_password, verbose, usernames,
                       passwords):
    """Add users to the Nexus instance specified by URL"""
    exit_code = 0
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
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
                print(f'{username} failed')
    exit(exit_code)


@dso_nexus.command(name='list-users')
@opts.default_opts
def dso_nexus_list_users(url, login_username, login_password, verbose):
    """List all users on the Nexus instance specified by URL"""
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        pprint(api.list_users())


@dso_nexus.command(name='search-user')
@opts.default_opts
@opts.search_user_opt
def dso_nexus_search_user(url, login_username, login_password, verbose,
                          username):
    """Search for users by username on the Nexus instance specified by URL"""
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        pprint(api.search_users(username))


@dso_nexus.command(name='search-repository')
@opts.default_opts
@click.option('--repository-name', '-r', required=True,
              help='the name of the repository to search for')
def dso_nexus_search_repo(url, login_username, login_password, verbose,
                          repository_name):
    """Search for and display information about a repository in the Nexus
    instance specified by URL"""
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        pprint(api.search_repos(repository_name))


@dso_nexus.command(name='list-repositories')
@opts.default_opts
def dso_nexus_list_repos(url, login_username, login_password, verbose):
    """List all of the repositories on the Nexus instance specified by URL"""
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        pprint(api.list_repos())


@dso_nexus.command(name='add-repository')
@opts.default_opts
@click.option('--repository-names', '-r', required=True,
              help=('the name of the repositories to add '
                    '(separate multiples with commas)'))
def dso_nexus_add_repo(url, login_username, login_password, verbose,
                       repository_names):
    """Add new Maven repositories to the Nexus instance specified by URL"""
    exit_code = 0
    errors = {}
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        for repository_name in repository_names.split(','):
            if not api.search_repos(repository_name):
                try:
                    if api.add_repo(repository_name) is not None:
                        print(f'{repository_name} added')
                    else:
                        exit_code += 1
                        print(f'{repository_name} failed')
                except Exception as e:
                    exit_code += 1
                    errors[repository_name] = e.msg
                    print(f'{repository_name} failed')
            else:
                print(f'{repository_name} ok')
    for repo, error in errors.items():
        sys.stderr.write(f'Error adding {repo}:\n{error}\n')
    sys.stderr.flush
    exit(exit_code)
