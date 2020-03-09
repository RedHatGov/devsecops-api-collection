import click
from .opts import *  # noqa: F403


class AliasedGroup(click.Group):
    """Overloaded click.Group to provide short, aliased names for commands"""
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


epilog = """
NOTE: the number of users and passwords to create must be equal. You can
specify them in any order you wish, but they will be paired up in the order
in which they were received for creation.
"""


@click.group(cls=AliasedGroup, name='main', invoke_without_command=True,
             epilog=epilog)
@click.version_option()
def main():
    """
    CLI to manipulate the APIs of services supported for the DevSecOps workshop
    in order to facilitate manipulating the APIs of instantiated services
    directly from the command line.
    """
    pass


@main.command(name='quay', epilog=epilog)
@opts.default_opts  # noqa: F405
def dso_quay(url, login_username, login_password, usernames, passwords,
             verbose):
    """Manage the Quay API instance whose base endpoint is at URL"""
    from devsecops.quay import quay

    with quay.Quay(
        url, login_username, login_password, verbosity=verbose
    ) as api:
        for username, password in zip(usernames.split(','),
                                      passwords.split(',')):
            new_user = api.add_user(username, password)
            if new_user is not None:
                print(f'{username} added')
            else:
                print(f'{username} already exists')

@main.command(name='sonarqube', epilog=epilog)
@opts.default_opts  # noqa: F405
@opts.new_login_pw_opt
def dso_sonarqube(url, login_username, login_password, usernames, passwords,
                  verbose, new_login_password):
    """Manage the SonarQube API instance whose base endpoint is at URL"""
    pass


@main.command(name='nexus', epilog=epilog)
@opts.default_opts  # noqa: F405
def dso_nexus(url, login_username, login_password, usernames, passwords,
              verbose):
    """Manage the Nexus API instance whose base endpoint is at URL"""
    pass
