import click
import importlib

from .utils import get_config


@click.group()
@click.pass_context
def cli(ctx, profile=None, account_name=None, region=None):
    ctx.obj = get_config()


@cli.command()
@click.pass_obj
@click.argument('resource_name')
@click.option(
    '--dry-run/--no-dry-run',
    help="Prints parameters that would be updated",
    default=True
)
def tag(obj, resource_name, dry_run):
    module = importlib.import_module('plankton.tagger')
    tagger_class = _get_class_name_from_resource(resource_name)
    try:
        tagger_class = getattr(
            module,
            tagger_class
        )
    except AttributeError:
        print("Resource {} tagger not found".format(tagger_class))
        return

    tagger_instance = tagger_class()
    tagger_instance.set_tags()


def _get_class_name_from_resource(resource_name):

    resource_name = resource_name.replace(
        "_",
        " "
    )
    resource_name = resource_name.title()
    resource_name = resource_name.replace(
        " ",
        ""
    )

    return "AWSTagger{}".format(resource_name)
