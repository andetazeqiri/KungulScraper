#!/usr/bin/env python3
"""Convert pipe-delimited products TXT to CSV."""
import csv
from pathlib import Path

INPUT = Path("products_inkey_all.txt")
OUTPUT = Path("products_inkey_all.csv")

def main():
    if not INPUT.exists():
        raise SystemExit(f"Input file not found: {INPUT}")
    rows = []
    with INPUT.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            parts = line.split("|")
            if i == 0:
                header = parts
                continue
            if len(parts) != len(header):
                # pad or trim to header length to avoid CSV inconsistencies
                if len(parts) < len(header):
                    parts = parts + [""] * (len(header) - len(parts))
                else:
                    parts = parts[:len(header)]
            rows.append(parts)
    
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT}")

if __name__ == "__main__":
    main()
