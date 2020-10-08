from typing import Iterable, Union
import pathlib
import sys
import click

from jira import JIRA
from gjira.template import generate_template, get_template_context

from .gjira import get_issue, get_jira_from_env, is_gjira_in_file, update_commit_message

from .git import get_branch_id, get_branch_name, validate_branch_name
from .coro import coro
from gjira.output import write_error


@click.command("append-jira")
@click.option("--board", "-b", required=True, type=str)
@click.option("--regex", "-r", required=True, type=str)
@click.option(
    "--ignore-files",
    "-i",
    default=",".join(
        (
            "MERGE_MSG",
            "SQUASH_MSG",
        )
    ),
    show_default=True,
)
@click.option(
    "--template",
    "-t",
    type=click.Path(exists=True, writable=True, readable=True, resolve_path=True),
    default=str(pathlib.Path(".").joinpath(".commit.template")),
)
@click.option(
    "--max-retries",
    "-m",
    type=int,
    default=1,
    help="Number of HTTP retries. Default is 1",
)
@click.argument("filename")
@coro
async def cmd_update_commit_msg(
    filename: str,
    board: str,
    regex: str,
    template: str,
    max_retries: int,
    ignore_files: Union[Iterable, str],
):
    if isinstance(ignore_files, str):
        ignore_files = ignore_files.split(",")

    if filename in ignore_files:
        print(f"File '{filename}'. Skipping.")
        sys.exit(0)

    if await is_gjira_in_file(filename):
        write_error("Duplicated. Skipping")
        sys.exit(0)

    task_id = await get_branch_id(regex)
    options = get_jira_from_env()

    try:
        jira = JIRA(**options, max_retries=max_retries)
    except Exception as e:
        write_error(f"Error: Connection error. Aborting", with_env=True)
        write_error(f"Python trackback {e}\n")
        sys.exit(1)

    attributes = await get_template_context(template)
    issue = await get_issue(jira, task_id, attributes)

    if not issue.keys() or not issue.values():
        write_error(f"Issue '{task_id}' does not meet template criteria. Skipping")
        sys.exit(0)

    content = await generate_template(issue, template)
    await update_commit_message(filename, content)


@click.command("check-branch")
@click.option(
    "--regex",
    "-r",
    required=True,
    type=str,
    help="Regex of a branch format to validate",
)
@click.option("--branch", "-b", type=str)
@coro
async def cmd_validate_branch_name(regex: str, branch: str):
    valid = validate_branch_name(branch or await get_branch_name(), regex)
    if valid is None:
        write_error(
            f"Branch '{branch or get_branch_name()}' name requires the format of '{regex}'. Aborting."
        )
        sys.exit(1)

    sys.exit(0)


@click.group()
def cli():
    pass


cli.add_command(cmd_validate_branch_name)
cli.add_command(cmd_update_commit_msg)
