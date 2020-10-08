from typing import Union
import asyncio
import re
import subprocess
import sys

from gjira.output import write_error


async def get_branch_name() -> str:
    proc = await asyncio.create_subprocess_shell(
        " ".join(("git", "rev-parse", "--abbrev-ref", "HEAD")),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return stdout.decode("UTF-8")


async def get_branch_id(regex):
    compiled_re = re.compile(regex)
    branch = await get_branch_name()

    if not compiled_re.findall(branch):
        write_error(
            f"Bad branch name '{branch}'. Expected format of '{regex}'. Skipping."
        )
        sys.exit(0)

    return compiled_re.findall(branch)[0]


def validate_branch_name(branch: str, regex: str) -> Union[list, None]:
    compiled_re = re.compile(regex)
    if not compiled_re.match(branch):
        return None
    return compiled_re.findall(branch)
