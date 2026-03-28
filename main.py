import argparse
import json

from core.orchestrator import generate_icp_only, run_full_analysis
from utils.formatter import report_to_dict


def main():
    parser = argparse.ArgumentParser(description="Signal Finder CLI")
    parser.add_argument("--url", required=True, help="Company website URL")
    parser.add_argument(
        "--icps",
        default="0,1",
        help="Comma-separated ICP indices to select (default: 0,1)",
    )
    args = parser.parse_args()
    indices = [int(i.strip()) for i in args.icps.split(",")]

    report = run_full_analysis(args.url, indices)
    print(json.dumps(report_to_dict(report), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
