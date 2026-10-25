"""CLI entry point for eventstudy."""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eventstudy", description="Event study CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init-db", help="Initialize the database")
    subparsers.add_parser("fetch-prices", help="Fetch benchmark prices")
    subparsers.add_parser("migrate-legacy", help="Migrate legacy events")
    subparsers.add_parser("run-study", help="Run the event study")
    return parser

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    print(f"{args.command}: not implemented")

if __name__ == "__main__":
    main()
