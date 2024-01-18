import os
import configparser
import click
# from .auth_helpers import auth0_get_token, auth0_get_domain

DEFAULT_CONFIG_FILES = [
    'gobctl.cfg',
    os.path.expanduser('~/gobctl.cfg'),
    os.path.expanduser('~/.config/gobctl/config.ini')
]


def configure(ctx, param, filename):
    config = configparser.ConfigParser()
    files_parsed = config.read(filename)

    click.echo(f'Reading config from: {files_parsed}')

    ctx.default_map = {}
    for section in config.sections():
        command_path = section.split('.')
        if command_path[0] != 'options':
            continue
        defaults = ctx.default_map
        for cmdname in command_path[1:]:
            defaults = defaults.setdefault(cmdname, {})
        defaults.update(config[section])


# @click.group(context_settings=config_dict)
@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '-c', '--config',
    type=click.Path(dir_okay=False),
    default=DEFAULT_CONFIG_FILES,
    callback=configure,
    is_eager=True,
    expose_value=False,
    help='Read option defaults from the specified INI file',
    show_default=True,
    multiple=True,
)
@click.option('-v', '--verbose', is_flag=True)
@click.option('-u', '--url', default='localhost', help='Gobannus URL (default: "localhost")')
@click.option('--api-base-path', default='/api', help='Gobannus API base path (default: "/api")')
@click.version_option()
def cli(ctx, verbose, url, api_base_path):
    """gobctl is a command line interface (CLI) for Gobannus."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['url'] = url
    ctx.obj['api-base-path'] = api_base_path
    # ctx.obj['auth0_domain'] = auth0_get_domain()
    # ctx.obj['auth0_token'] = auth0_get_token()

    if verbose:
        click.echo('Verbose mode is on...')
        click.echo()
        click.echo(f'  Gobannus URL: {url}')
        click.echo(f'  Gobannus API base path: {api_base_path}')
        click.echo(f'  Auth0 domain: {ctx.obj["auth0_domain"]}')
        click.echo(f'  Auth0 access token: {"set" if ctx.obj["auth0_token"] is not None else "not set"}')
        click.echo()
