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
    opts.check_online(url)

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
