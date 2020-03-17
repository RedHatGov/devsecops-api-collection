# SPDX-License-Identifier: BSD-2-Clause
import click


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


@click.group(cls=AliasedGroup, name='main')
@click.version_option()
def main():
    """
    CLI to manipulate the APIs of services supported for the DevSecOps workshop
    in order to facilitate manipulating the APIs of instantiated services
    directly from the command line.
    """
    pass


@main.group(cls=AliasedGroup, name='quay')
def dso_quay():
    """Manage a Quay API instance"""
    pass


@main.group(cls=AliasedGroup, name='nexus')
def dso_nexus():
    """Manage a Nexus API instance"""
    pass


@main.group(cls=AliasedGroup, name='sonarqube')
def dso_sonarqube():
    """Manage a SonarQube API instance"""
    pass


from devsecops.cli.services import quay, nexus, sonarqube  # noqa E402,F401
