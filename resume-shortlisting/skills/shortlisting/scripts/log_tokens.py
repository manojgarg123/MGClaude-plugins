#!/usr/bin/env python3
"""
log_tokens.py — Append a token-usage record for one shortlisting run.

Usage:
  python log_tokens.py \
    --log-file   "<Tracker folder>/token_usage.json" \
    --run-id     "<YYYY-MM-DD_HH-MM-SS>"  \
    --position   "<role title>" \
    --new-resumes <int>  \
    --input-files  "<file1>,<file2>,..."  \
    --output-text  "<combined output text>"

The script counts input tokens from the listed files + output tokens from the
provided text, then appends a JSON record to the log file.

Token counting uses tiktoken if available, otherwise falls back to len(text)//4
(≈ chars-per-token for English text, accurate to ~10%).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


# ── Token counter ──────────────────────────────────────────────────────────────

def count_tokens(text: str) -> int:
    """Count tokens in text. Uses tiktoken if available, else char-based estimate."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")   # same family as Claude
        return len(enc.encode(text))
    except ImportError:
        # Fallback: ~4 chars per token is a reasonable approximation for English
        return max(1, len(text) // 4)


def count_file_tokens(path: str) -> int:
    """Read a file and count its tokens. Returns 0 if file unreadable."""
    try:
        # For text files, read directly
        ext = os.path.splitext(path)[1].lower()
        if ext in (".json", ".md", ".txt", ".py", ".html", ".csv"):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return count_tokens(f.read())
        # For PDFs/DOCX, use extract_text if available
        script_dir = os.path.dirname(os.path.abspath(__file__))
        extract_script = os.path.join(script_dir, "extract_text.py")
        if os.path.exists(extract_script) and ext in (".pdf", ".docx", ".doc"):
            import subprocess
            result = subprocess.run(
                ["python3", extract_script, path],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return count_tokens(result.stdout)
        # Binary / unknown: estimate from file size (very rough)
        return os.path.getsize(path) // 6
    except Exception:
        return 0


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Log token usage for a shortlisting run")
    parser.add_argument("--log-file",    required=True, help="Path to token_usage.json")
    parser.add_argument("--run-id",      default=None,  help="Run identifier (default: current timestamp)")
    parser.add_argument("--position",    default="N/A", help="Role title")
    parser.add_argument("--new-resumes", type=int, default=0, help="Number of new resumes scored this run")
    parser.add_argument("--input-files", default="",    help="Comma-separated list of input file paths to count")
    parser.add_argument("--output-text", default="",    help="All output text generated this run (for output token count)")
    args = parser.parse_args()

    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

    # Count input tokens from files
    input_file_tokens = 0
    file_breakdown = {}
    if args.input_files.strip():
        for path in args.input_files.split(","):
            path = path.strip()
            if path:
                t = count_file_tokens(path)
                file_breakdown[os.path.basename(path)] = t
                input_file_tokens += t

    # Count output tokens from text
    output_tokens = count_tokens(args.output_text) if args.output_text.strip() else 0

    record = {
        "run_id":              run_id,
        "timestamp":           datetime.now(timezone.utc).isoformat(),
        "position":            args.position,
        "new_resumes_scored":  args.new_resumes,
        "input_tokens": {
            "total":     input_file_tokens,
            "breakdown": file_breakdown,
        },
        "output_tokens_est":   output_tokens,
        "total_tokens_est":    input_file_tokens + output_tokens,
        "note": (
            "Counts are estimates: input = tiktoken/char-based on file contents; "
            "output = tiktoken/char-based on generated text. "
            "Does not include system prompt or tool-call overhead."
        ),
    }

    # Load existing log or start fresh
    os.makedirs(os.path.dirname(os.path.abspath(args.log_file)), exist_ok=True)
    if os.path.exists(args.log_file):
        try:
            with open(args.log_file, "r", encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            log = {"runs": []}
    else:
        log = {"runs": []}

    log["runs"].append(record)

    # Recompute running totals
    log["total_runs"]          = len(log["runs"])
    log["cumulative_input_tokens"]  = sum(r["input_tokens"]["total"] for r in log["runs"])
    log["cumulative_output_tokens"] = sum(r["output_tokens_est"]      for r in log["runs"])
    log["cumulative_total_tokens"]  = sum(r["total_tokens_est"]        for r in log["runs"])
    log["last_updated"]        = record["timestamp"]

    with open(args.log_file, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

    # Print summary to stdout
    print(f"✓ Token log updated: {args.log_file}")
    print(f"  Run: {run_id}")
    print(f"  Input tokens (files):   {input_file_tokens:,}")
    print(f"  Output tokens (est.):   {output_tokens:,}")
    print(f"  Total this run (est.):  {input_file_tokens + output_tokens:,}")
    print(f"  Cumulative total:       {log['cumulative_total_tokens']:,}")


if __name__ == "__main__":
    main()
