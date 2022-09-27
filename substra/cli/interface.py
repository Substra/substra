import functools
import json
import logging
import os

import click

from substra import __version__
from substra.cli import printers
from substra.sdk import config as configuration
from substra.sdk import exceptions
from substra.sdk import utils
from substra.sdk.client import Client

DEFAULT_RETRY_TIMEOUT = 300


def get_client(global_conf):
    """Initialize substra client from config file, profile name and tokens file."""
    help_command = "substra config <url> ..."

    try:
        client = Client.from_config_file(
            config_path=global_conf.config,
            profile_name=global_conf.profile,
            tokens_path=global_conf.tokens,
        )

    except FileNotFoundError:
        raise click.ClickException(f"Config file '{global_conf.config}' not found. Please run '{help_command}'.")

    except configuration.ProfileNotFoundError:
        raise click.ClickException(f"Profile '{global_conf.profile}' not found. Please run '{help_command}'.")

    return client


def display(res):
    """Display result."""
    if res is None:
        return
    if isinstance(res, dict) or isinstance(res, list):
        res = json.dumps(res, indent=2)
    print(res)


class GlobalConf:
    def __init__(self):
        self.profile = None
        self.config = None
        self.tokens = None
        self.verbose = None
        self.output_format = None
        self.retry_timeout = DEFAULT_RETRY_TIMEOUT

    def retry(self, func):
        return utils.retry_on_exception(
            exceptions=(exceptions.RequestTimeout),
            timeout=float(self.retry_timeout),
        )(func)


def update_global_conf(ctx, param, value):
    setattr(ctx.obj, param.name, value)


def click_global_conf_profile(f):
    """Add profile option to command."""
    return click.option(
        "--profile",
        expose_value=False,
        callback=update_global_conf,
        default="default",
        help="Profile name to use.",
    )(f)


def click_global_conf_tokens(f):
    """Add tokens option to command."""
    return click.option(
        "--tokens",
        expose_value=False,
        type=click.Path(dir_okay=False, resolve_path=True),
        callback=update_global_conf,
        default=os.path.expanduser(configuration.DEFAULT_TOKENS_PATH),
        help=f"Tokens file path to use (default {configuration.DEFAULT_TOKENS_PATH}).",
    )(f)


def click_global_conf_config(f):
    """Add config option to command."""
    return click.option(
        "--config",
        expose_value=False,
        type=click.Path(exists=True, resolve_path=True),
        callback=update_global_conf,
        default=os.path.expanduser(configuration.DEFAULT_PATH),
        help=f"Config path (default {configuration.DEFAULT_PATH}).",
    )(f)


def click_global_conf_verbose(f):
    """Add verbose option to command."""
    return click.option(
        "--verbose",
        expose_value=False,
        callback=update_global_conf,
        is_flag=True,
        help="Enable verbose mode.",
    )(f)


def set_log_level(ctx, param, value):
    if value:
        logging.basicConfig(level=getattr(logging, value))


def click_global_conf_log_level(f):
    """Add verbose option to command."""
    return click.option(
        "--log-level",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        callback=set_log_level,
        expose_value=False,
        help="Enable logging and set log level",
    )(f)


def click_global_conf_output_format(f):
    """Add output option to command."""
    return click.option(
        "-o",
        "--output",
        "output_format",
        type=click.Choice(["pretty", "yaml", "json"]),
        expose_value=False,
        default="pretty",
        show_default=True,
        callback=update_global_conf,
        help="Set output format                 \
            - pretty: summarised view           \
            - yaml: full view in YAML format    \
            - json: full view in JSON format    \
            ",
    )(f)


def click_global_conf(f):
    f = click_global_conf_verbose(f)
    f = click_global_conf_tokens(f)
    f = click_global_conf_profile(f)
    f = click_global_conf_config(f)
    f = click_global_conf_log_level(f)
    return f


def click_global_conf_with_output_format(f):
    f = click_global_conf_output_format(f)
    f = click_global_conf(f)
    return f


def click_option_expand(f):
    """Add expand option to command."""
    return click.option("--expand", is_flag=True, help="Display associated assets details")(f)


def click_global_conf_retry_timeout(f):
    """Add timeout option to command."""
    return click.option(
        "--timeout",
        "timeout",
        type=click.INT,
        expose_value=False,
        default=DEFAULT_RETRY_TIMEOUT,
        show_default=True,
        callback=update_global_conf,
        help="Max number of seconds the operation will be retried for",
    )(f)


def _format_server_errors(fn, errors):
    action = fn.__name__.replace("_", " ")

    def _format_error_lines(errors_):
        lines_ = []
        for field, field_errors in errors_.items():
            for field_error in field_errors:
                lines_.append(f"{field}: {field_error}")
        return lines_

    lines = []
    if isinstance(errors, dict):
        lines += _format_error_lines(errors)
    elif isinstance(errors, list):
        for error in errors:
            lines += _format_error_lines(error)
    else:
        lines.append(errors)

    pluralized_error = "errors" if len(lines) > 1 else "error"
    return (
        f"Could not {action}, the server returned the following \
        {pluralized_error}:\n- "
        + "\n- ".join(lines)
    )


def error_printer(fn):
    """Command decorator to pretty print a few selected exceptions from sdk."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        if ctx.obj.verbose:
            # disable pretty print of errors if verbose mode is activated
            return fn(*args, **kwargs)

        try:
            return fn(*args, **kwargs)
        except exceptions.BadLoginException:
            raise click.ClickException("Login failed: No active account found with the" " given credentials.")
        except exceptions.InvalidRequest as e:
            try:
                errors = e.errors["message"]
            except KeyError:
                errors = e.errors
            raise click.ClickException(_format_server_errors(fn, errors))
        except exceptions.RequestException as e:
            raise click.ClickException(f"Request failed: {e.__class__.__name__}: {e}")
        except (
            exceptions.ConnectionError,
            exceptions.InvalidResponse,
            exceptions.LoadDataException,
            exceptions.BadConfiguration,
        ) as e:
            raise click.ClickException(str(e))

    return wrapper


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    """Substra Command Line Interface.

    For help using this tool, please open an issue on the Github repository:
    https://github.com/Substra/substra
    """
    ctx.obj = GlobalConf()


@cli.command("config")
@click.argument("url")
@click.option(
    "--config",
    type=click.Path(),
    default=os.path.expanduser(configuration.DEFAULT_PATH),
    help=f"Config path (default {configuration.DEFAULT_PATH}).",
)
@click.option("--profile", default="default", help="Profile name to add")
@click.option("--insecure", "-k", is_flag=True, help="Do not verify SSL certificates")
def add_profile_to_config(url, config, profile, insecure):
    """Add profile to config file."""
    manager = configuration.ConfigManager(config)
    manager.set_profile(name=profile, url=url, insecure=insecure)
    manager.save()


@cli.command("login")
@click_global_conf
@click.pass_context
@error_printer
@click.option("--username", "-u", envvar="SUBSTRA_USERNAME", prompt=True)
@click.option("--password", "-p", envvar="SUBSTRA_PASSWORD", prompt=True, hide_input=True)
def login(ctx, username, password):
    """Login to the Substra platform."""
    client = get_client(ctx.obj)

    token = client.login(username, password)

    # save token to tokens file
    manager = configuration.TokenManager(ctx.obj.tokens)
    manager.set_profile(ctx.obj.profile, token)
    manager.save()

    display(f"Token: {token}")


@cli.group()
@click.pass_context
def organization(ctx):
    """Display organization description."""


@organization.command("info")
@click_global_conf_with_output_format
@click.pass_context
@error_printer
def organization_info(ctx):
    """Display organization info."""
    client = get_client(ctx.obj)
    res = client.organization_info()
    printer = printers.OrganizationInfoPrinter()
    printer.print(res)


@cli.group()
@click.pass_context
def cancel(ctx):
    """Cancel execution of an asset."""
    pass


@cancel.command("compute_plan")
@click.argument("compute_plan_key", type=click.STRING)
@click_global_conf
@click.pass_context
def cancel_compute_plan(ctx, compute_plan_key):
    """Cancel execution of a compute plan."""
    client = get_client(ctx.obj)
    # method must exist in sdk
    client.cancel_compute_plan(compute_plan_key)


if __name__ == "__main__":
    cli()
