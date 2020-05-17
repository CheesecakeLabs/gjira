#!/usr/bin/env python3

import io
import os
import pathlib
import subprocess

from jira import JIRA

DEFAULT_MSG = "Jira issue: {}\nJira story {}"


def get_branch_name() -> str:
    return subprocess.check_output(
        ("git", "rev-parse", "--abbrev-ref", "HEAD",),
    ).decode("UTF-8")


def get_jira_from_env() -> dict:
    return {
        "server": os.environ.get("jiraserver"),
        "basic_auth": (os.environ.get("jirauser"), os.environ.get("jiratoken")),
    }


def get_issue(jira: JIRA, id: str):
    return jira.issue(id)


def get_issue_parent(issue) -> str:
    if hasattr(issue.fields, "parent"):
        return issue.fields.parent.key
    return ""


def update_commit_message(filename: str, fmt: str) -> list:
    with open(filename, "r+") as fd:
        pos = 0
        lines = []
        for i, line in enumerate(fd):
            lines.append(line)
            if line.startswith("#") and not pos:  # have we already found a #?
                pos = i
                break

        if len(lines) > 1:
            if lines[pos - 1].count("\n") > 1:
                fmt = f"{fmt}\n"
            else:
                fmt = f"\n{fmt}\n"
        else:
            fmt = f"\n{fmt}\n"

        # add fmt to the corresponding position and read any unread line
        lines = lines[:pos] + [fmt] + lines[pos:] + fd.readlines()

        # Write lines back to file
        fd.seek(0)
        for line in lines:
            fd.write(line)

        return lines
