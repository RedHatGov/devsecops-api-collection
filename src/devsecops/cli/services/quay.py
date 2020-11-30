# SPDX-License-Identifier: BSD-2-Clause
from devsecops.cli import opts
from devsecops.cli import dso_quay
from devsecops.quay import quay


@dso_quay.command(name='add-user', epilog=opts.add_users_epilog)
@opts.default_opts
@opts.add_users_opt
def dso_quay_add_user(url, login_username, login_password, verbose, usernames,
                      passwords):
    """Add users to the Quay instance specified by URL"""
    with quay.Quay(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        for username, password in zip(usernames.split(','),
                                      passwords.split(',')):
            new_user = api.add_user(username, password)
            if new_user is not None:
                print(f'{username} added')
            else:
                print(f'{username} ok')


@dso_quay.command(name='add-org')
@opts.default_opts
@opts.add_orgs_opt
def dso_quay_add_org(url, login_username, login_password, verbose,
                     organizations):
    """Add Organizations to the Quay instance specified by URL"""
    with quay.Quay(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        for organization in organizations.split(','):
            new_org = api.add_org(organization)
            if new_org is not None:
                print(f'{organization} added')
            else:
                print(f'{organization} ok')


@dso_quay.command(name='add-app')
@opts.default_opts
@opts.add_app_opt
def dso_quay_add_app(url, login_username, login_password, verbose,
                     organization, app_name, app_description):
    """
    Add an Application to an Organization on the Quay instance specified by URL
    """
    with quay.Quay(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        new_app = api.add_app(organization, app_name, app_description)
        print((f'{app_name} added (client_id: {new_app.json()["client_id"]}, '
               f'client_secret: {new_app.json()["client_secret"]})'))


@dso_quay.command(name='add-repo')
@opts.default_opts
@opts.add_repo_opt
def dso_quay_add_repo(url, login_username, login_password, verbose,
                     organization, repo_name, repo_description):
    """
    Add a Repository to an Organization on the Quay instance specified by URL
    """
    with quay.Quay(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        new_repo = api.add_repo(organization, repo_name, repo_description)
        print(f'{repo_name} ok')


@dso_quay.command(name='add-robot')
@opts.default_opts
@opts.add_robot_opt
def dso_quay_add_robot(url, login_username, login_password, verbose,
                       organization, robot_name, robot_description):
    """
    Add a Robot Account to an Organization on the Quay instance specified by
    URL
    """
    with quay.Quay(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        existing_robot = api.get_robot(organization, robot_name)
        if existing_robot:
            print(f'{robot_name} ok (token: {existing_robot.json()["token"]})')
        else:
            new_robot = api.add_robot(organization, robot_name,
                                      robot_description)
            print(f'{robot_name} added (token: {new_robot.json()["token"]})')
