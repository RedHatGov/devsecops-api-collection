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


@click.group(name='main', invoke_without_command=True, epilog=epilog)
@click.option('-v', '--verbose', count=True,
              help='Increase verbosity (specify multiple times for more)')
@click.version_option()
def main(verbose):
    """
    CLI to manipulate the APIs of services supported for the DevSecOps workshop
    in order to facilitate manipulating the APIs of instantiated services
    directly from the command line.
    """
    pass


@main.command(cls=AliasedGroup, name='quay')
@opts.default_opts  # noqa: F405
def dso_quay(url, login_username, login_password, usernames, passwords):
    """Manage the Quay API instance"""
    from devsecops.quay import quay
    from pprint import pprint

    with quay.Quay(url, login_username, login_password) as api:
        for username, password in zip(usernames.split(','),
                                      passwords.split(',')):
            pprint(api.add_user(username, password))

@main.command(cls=AliasedGroup, name='sonarqube')
@opts.default_opts  # noqa: F405
@opts.new_login_pw_opt
def dso_sonarqube(url, login_username, login_password, usernames, passwords):
    """Manage the SonarQube API instance"""
    pass


@main.command(cls=AliasedGroup, name='nexus')
@opts.default_opts  # noqa: F405
def dso_nexus(url, login_username, login_password, usernames, passwords):
    """Manage the Nexus API instance"""
    pass
