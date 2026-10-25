"""Smoke test for CLI parser."""
import argparse

from eventstudy.__main__ import build_parser


def test_cli_parser_builds():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    args = parser.parse_args(["init-db"])
    assert args.command == "init-db"
