#!/usr/bin/env python3

# Author: Ben Mezger <me@benmezger.nl>
# Created at <2020-10-07 Wed 19:55>

import asyncio
from functools import wraps

def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper
