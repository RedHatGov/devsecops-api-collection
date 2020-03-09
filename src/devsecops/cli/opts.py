import click

def url_arg(f):
    return click.argument('url', metavar='URL',
                          help=('the base URL of service, '
                                'not including anything after the TLD'))(f)

def login_user_opt(f):
    return click.option('--login-username', '-U', required=True,
                        help='the username with which to log in')(f)

def login_pw_opt(f):
    return click.option('--login-password', '-P', required=True,
                        help='the password for the login user')(f)

def add_users_opt(f):
    for option in reversed([
        click.option('--usernames', '-u',
                     help=('usernames to add to the service '
                           '(separate multiples with commas)')),
        click.option('--passwords', '-p', action='append',
                     help=('a password for the last username provided '
                           '(separate multiples with commas)'))
    ]):
        f = option(f)
    return f

def new_login_pw_opt(f):
    return click.option('--new-login-password', '-N', required=False,
                        help='a new password for the login user')(f)

def default_opts(f):
    for option in reversed([
        url_arg,
        login_user_opt,
        login_pw_opt,
        add_users_opt
    ]):
        f = option(f)
    return f
