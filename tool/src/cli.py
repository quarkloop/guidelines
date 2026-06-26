"""
cli.py — Command-line dispatch for quarkloop repository tooling.

Single responsibility: parse arguments and dispatch to the appropriate
subcommand module. No business logic — each subcommand lives in its own
file under commands/.
"""

import argparse

from .commands import cmd_init, cmd_doctor, cmd_sync, cmd_list, cmd_check_commits, cmd_badges


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="repo.py",
        description="Quarkloop repository tooling — scaffold, validate, and sync repos.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Register each subcommand from its own module
    cmd_init.add_parser(subparsers)
    cmd_doctor.add_parser(subparsers)
    cmd_sync.add_parser(subparsers)
    cmd_list.add_parser(subparsers)
    cmd_check_commits.add_parser(subparsers)
    cmd_badges.add_parser(subparsers)

    return parser


def main():
    """Parse arguments and dispatch to the appropriate subcommand."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
