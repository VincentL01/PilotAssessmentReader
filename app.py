import argparse
from src.process.ingest import ingest
from src.process.run import run_query, export_direct

def main():
    parser = argparse.ArgumentParser(description="Schema-agnostic Pilot Training Retriever (LangChain + LangGraph + FAISS)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest", help="Ingest folders of .json records into FAISS")
    p_ing.add_argument("folders", nargs="+", help="Folders (e.g., ./virginair ./airtransat)")

    p_query = sub.add_parser("query", help="Run the LangGraph NL workflow (dynamic extraction, optional Parquet export)")
    p_query.add_argument("prompt", help="e.g., 'Give me all the detail information ... -> to a .parquet file'")
    p_query.add_argument("--out", help="Optional output .parquet path")

    p_exp = sub.add_parser("export", help="Direct export by filters (no NL parsing)")
    p_exp.add_argument("--airline", required=True)
    p_exp.add_argument("--training-type", required=True)
    p_exp.add_argument("--out", required=True)

    args = parser.parse_args()
    if args.cmd == "ingest":
        ingest(args.folders)
    elif args.cmd == "query":
        run_query(args.prompt, args.out)
    elif args.cmd == "export":
        export_direct(args.airline, args.training_type, args.out)

if __name__ == "__main__":
    main()