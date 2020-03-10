# SPDX-License-Identifier: BSD-2-Clause
from devsecops.cli import opts
from devsecops.cli import dso_sonarqube
from devsecops.sonarqube import sonarqube


@dso_sonarqube.command(name='add-user', epilog=opts.add_users_epilog)
@opts.default_opts
@opts.add_users_opt
@opts.new_login_pw_opt
def dso_sonarqube_add_user(url, login_username, login_password, verbose,
                           usernames, passwords, new_login_password):
    opts.check_online(url)
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
    from pprint import pprint

    opts.check_online(url)

    with sonarqube.SonarQube(
        url, login_username, login_password, verbosity=verbose,
        new_password=new_login_password
    ) as api:
        pprint(api.search_users(username))
