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


@dso_nexus.command(name='add-proxy-repository')
@opts.default_opts
@click.option('--repository-name', '-r', required=True,
              help=('the name of the repositories to add '))
@click.option('--remote-repo-url', '-r', required=True,
              help=('the URL of the remote repo to proxy'))
def dso_nexus_add_proxy_repo(url, login_username, login_password, verbose,
                             repository_name, remote_repo_url):
    """Add a Maven proxy repositories to the Nexus instance specified by URL"""
    exit_code = 0
    errors = {}
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        if not api.search_repos(repository_name):
            try:
                if api.add_proxy_repo(repository_name,
                                      remote_repo_url) is not None:
                    print(f'proxy {repository_name} added')
                else:
                    exit_code += 1
                    print(f'proxy {repository_name} failed')
            except Exception as e:
                exit_code += 1
                errors[repository_name] = e.msg
                print(f'proxy {repository_name} failed')
        else:
            print(f'proxy {repository_name} ok')
    for repo, error in errors.items():
        sys.stderr.write(f'Error adding {repo}:\n{error}\n')
    sys.stderr.flush
    exit(exit_code)


@dso_nexus.command(name='add-raw-repository')
@opts.default_opts
@click.option('--repository-names', '-r', required=True,
              help=('the name of the repositories to add '
                    '(separate multiples with commas)'))
def dso_nexus_add_raw_repo(url, login_username, login_password, verbose,
                       repository_names):
    """Add new raw repositories to the Nexus instance specified by URL"""
    exit_code = 0
    errors = {}
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        for repository_name in repository_names.split(','):
            if not api.search_repos(repository_name):
                try:
                    if api.add_raw_repo(repository_name) is not None:
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


@dso_nexus.command(name='update-repository')
@opts.default_opts
@click.option('--repository-names', '-r', required=True,
              help=('the name of the repositories to add '
                    '(separate multiples with commas)'))
@click.option('--write-policy', '-p', required=True,
              help=('the desired writePolicy '
                    '(ALLOW, DENY, ALLOW_ONCE'))
def dso_nexus_update_repo(url, login_username, login_password, verbose,
                       repository_names, write_policy):
    """Update writePolicy for Maven repositories specified by URL"""
    exit_code = 0
    errors = {}
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        for repository_name in repository_names.split(','):
            if not api.search_repos(repository_name):
                exit_code += 1
                print(f'{repository_name} does not exist')
            else:
                try:
                    if api.update_repo(repository_name, write_policy) is not None:
                        print(f'{repository_name} updated with writePolicy {write_policy}')
                    else:
                        exit_code += 1
                        print(f'{repository_name} update failed')
                except Exception as e:
                    exit_code += 1
                    errors[repository_name] = e.msg
                    print(f'{repository_name} update failed')
    for repo, error in errors.items():
        sys.stderr.write(f'Error updating {repo}:\n{error}\n')
    sys.stderr.flush
    exit(exit_code)


@dso_nexus.command(name='update-group-repo')
@opts.default_opts
@click.option('--group-repository-name', '-r', required=True,
              help=('the name of the group repository to update '))
@click.option('--member-repository-names', '-r', required=True,
              help=('the name of the repositories to group '
                    '(separate multiples with commas)'))
def dso_nexus_update_group_repo(url, login_username, login_password, verbose,
                                group_repository_name,
                                member_repository_names):
    """Update group repo with the list of member repositories"""
    exit_code = 0
    errors = {}
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        if api.search_repos(group_repository_name):
            try:
                if api.update_group_repo(
                    group_repository_name, member_repository_names.split(',')
                ) is not None:
                    print(f'group repo {group_repository_name} added')
                else:
                    exit_code += 1
                    print(f'group repo {group_repository_name} failed')
            except Exception as e:
                exit_code += 1
                errors[group_repository_name] = e.msg
                print(f'group repo {group_repository_name} failed')
        else:
            print(f'group repo {group_repository_name} doesn\'t exist')
    for repo, error in errors.items():
        sys.stderr.write(f'Error updating group repo {repo}:\n{error}\n')
    sys.stderr.flush
    exit(exit_code)


@dso_nexus.command(name='add-script')
@opts.default_opts
@click.option('--script-name', '-n', required=True,
              help=('the name of the script to add'))
@click.option('--script-content', '-c', required=True,
              help=('the script\'s content'))
@click.option('--script-type', '-t', required=True,
              help=('the script\'s type'))
def dso_nexus_add_script(url, login_username, login_password, verbose,
                         script_name, script_content, script_type):
    """Add new Scripts to the Nexus instance specified by URL"""
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        try:
            api.add_script(script_name, script_content, script_type)
        except Exception:
            print(f'{script_name} failed')
            exit(1)


@dso_nexus.command(name='run-script')
@opts.default_opts
@click.option('--script-name', '-n', required=True,
              help=('the name of the script to run'))
@click.option('--body', '-b', required=False,
              help=('the body of parameters to pass to the script'))
def dso_nexus_run_script(url, login_username, login_password, verbose,
                         script_name, body):
    """Run the specified Script in the Nexus instance specified by URL"""
    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        try:
            api.run_script(script_name, body)
        except Exception:
            print(f'{script_name} failed')
            exit(1)
