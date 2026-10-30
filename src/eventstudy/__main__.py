"""CLI entry point for eventstudy."""
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eventstudy", description="Event study CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init-db", help="Initialize the database")
    subparsers.add_parser("fetch-prices", help="Fetch benchmark prices")
    subparsers.add_parser("migrate-legacy", help="Migrate legacy events")
    subparsers.add_parser("run-study", help="Run the event study")
    subparsers.add_parser("pattern-detect", help="Detect event patterns")
    pr = subparsers.add_parser("predict", help="Predict from event type")
    pr.add_argument("--type", required=True, dest="etype")
    pr.add_argument("--horizon", type=int, default=5)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "init-db":
        from eventstudy.db import init_db

        init_db()
        print("init-db: done")
    elif args.command == "fetch-prices":
        from eventstudy.config import BENCHMARK_TICKER
        from eventstudy.prices import fetch_and_store

        n = fetch_and_store(BENCHMARK_TICKER)
        print(f"fetch-prices: {n} rows")
    elif args.command == "migrate-legacy":
        from eventstudy.migrate_legacy import migrate

        n = migrate()
        print(f"migrate-legacy: {n} events")
    elif args.command == "run-study":
        from eventstudy.study import run_study

        summary = run_study()
        for row in summary:
            print(row)
    elif args.command == "pattern-detect":
        from eventstudy.db import get_connection
        from eventstudy.patterns import compute_patterns, save_patterns

        con = get_connection()
        try:
            pats = compute_patterns(con)
        finally:
            con.close()
        print(f"patterns: {len(pats)}")
        print(f"saved: {save_patterns(pats)}")
    elif args.command == "predict":
        from eventstudy.predict import predict_event

        print(predict_event(args.etype, args.horizon))
    else:
        print(f"{args.command}: not implemented")


if __name__ == "__main__":
    main()
