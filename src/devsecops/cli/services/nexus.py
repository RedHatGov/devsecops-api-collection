# SPDX-License-Identifier: BSD-2-Clause
from devsecops.cli import opts
from devsecops.cli import dso_nexus
from devsecops.nexus import nexus

@dso_nexus.command(name='add-user', epilog=opts.add_users_epilog)
@opts.default_opts
@opts.add_users_opt
def dso_nexus_add_user(url, login_username, login_password, verbose, usernames,
                       passwords):
    opts.check_online(url)

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
                print(f'{username}: failed')
    exit(exit_code)

@dso_nexus.command(name='list-users')
@opts.default_opts
def dso_nexus_list_users(url, login_username, login_password, verbose):
    from pprint import pprint

    opts.check_online(url)

    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        pprint(api.list_users())

@dso_nexus.command(name='search-user')
@opts.default_opts
@opts.search_user_opt
def dso_nexus_search_user(url, login_username, login_password, verbose,
                          username):
    from pprint import pprint

    opts.check_online(url)

    with nexus.Nexus(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        pprint(api.search_users(username))
