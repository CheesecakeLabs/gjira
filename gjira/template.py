#!/usr/bin/env python3

import pathlib
from typing import Callable

from jinja2 import Environment, Template, meta
import aiofiles


async def get_template_lines(path: str = None) -> Template:
    if path is None:
        path = str(pathlib.Path(".").joinpath(".commit.template"))
    async with aiofiles.open(path) as f:
        async for line in f:
            yield line


async def get_template_context(
    path: str = None, replace: Callable = lambda x: x.replace("__", ".")
) -> list:

    env = Environment()
    context = []
    async for line in get_template_lines(path):
        ast = env.parse(line)
        context.extend(meta.find_undeclared_variables(ast))

    # This is needed because find_undeclared_variables cannot find find
    # inner variables
    return [replace(i) for i in context]


async def generate_template(context: dict, path):
    async with aiofiles.open(path) as f:
        return Template(await f.read()).render(**context)
