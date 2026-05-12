#!/usr/bin/env python3
"""
Patch gdconfig tsv rows from a Google Sheet export.

Usage:
  patch_tsv.py --sheet-json /tmp/sheet.json \
               --tsv /Users/marinl/gdconfig/fo/config/iap_template.tsv \
               --ids 2013101095,2013101096 \
               --mode update

Behavior:
  - Reads sheet JSON (the raw `gws sheets spreadsheets values get --format json` output).
  - Aligns sheet header with tsv header; silently drops sheet columns absent from tsv.
  - Aborts if tsv has columns absent from sheet (schema regression — ambiguous).
  - update: replace existing rows matching --ids, preserving original line order.
  - insert: insert new rows sorted by numeric id, positioned after the last existing
    row whose id < new id (or at top of data if none smaller).
  - delete: remove rows matching --ids.
  - Prints a diff summary per touched row before writing.
"""
import argparse
import json
import sys
from pathlib import Path


def find_id_col(header: list[str]) -> int:
    """ID 列定位：优先 A_INT_id，否则 col 0（兼容老表）。"""
    if "A_INT_id" in header:
        return header.index("A_INT_id")
    return 0


def load_sheet(path: Path) -> tuple[list[str], dict[str, list[str]], int]:
    data = json.loads(path.read_text())
    rows = data["values"]
    header = rows[0]
    id_col = find_id_col(header)
    indexed: dict[str, list[str]] = {}
    for r in rows[1:]:
        if not r:
            continue
        padded = r + [""] * (len(header) - len(r))
        if id_col < len(padded) and padded[id_col]:
            indexed[padded[id_col]] = padded
    return header, indexed, id_col


def load_tsv(path: Path) -> tuple[list[str], list[list[str]], bool, int, str]:
    raw_bytes = path.read_bytes()
    sep = "\r\n" if b"\r\n" in raw_bytes else "\n"
    trailing_newline = raw_bytes.endswith(sep.encode())
    raw = raw_bytes.decode("utf-8")
    lines = raw.splitlines()
    header = lines[0].split("\t")
    body = [line.split("\t") for line in lines[1:]]
    id_col = find_id_col(header)
    return header, body, trailing_newline, id_col, sep


def align_columns(sheet_hdr: list[str], tsv_hdr: list[str]) -> list[int]:
    """Return index into sheet_hdr for each tsv_hdr column. Aborts on missing."""
    idx = []
    missing = []
    for col in tsv_hdr:
        if col in sheet_hdr:
            idx.append(sheet_hdr.index(col))
        else:
            missing.append(col)
    if missing:
        sys.exit(
            f"[abort] tsv has columns not in sheet: {missing}\n"
            f"        sheet header: {sheet_hdr}\n"
            f"        tsv header:   {tsv_hdr}"
        )
    dropped = [c for c in sheet_hdr if c not in tsv_hdr]
    if dropped:
        print(f"[info] dropping sheet columns absent from tsv: {dropped}", file=sys.stderr)
    return idx


def project(sheet_row: list[str], col_map: list[int]) -> list[str]:
    return [sheet_row[i] for i in col_map]


def diff_row(old: list[str], new: list[str], header: list[str]) -> list[tuple[int, str, str, str]]:
    return [
        (i, header[i], old[i], new[i])
        for i in range(len(header))
        if i < len(old) and i < len(new) and old[i] != new[i]
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet-json", required=True, type=Path)
    ap.add_argument("--tsv", required=True, type=Path)
    ap.add_argument("--ids", required=True, help="comma-separated ids")
    ap.add_argument("--mode", required=True, choices=["update", "insert", "delete"])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    ids = [x.strip() for x in args.ids.split(",") if x.strip()]
    if not ids:
        sys.exit("[abort] --ids empty")

    sheet_hdr, sheet_rows, sheet_id_col = load_sheet(args.sheet_json)
    tsv_hdr, tsv_body, trailing_newline, tsv_id_col, line_sep = load_tsv(args.tsv)
    col_map = align_columns(sheet_hdr, tsv_hdr)

    existing_ids = {row[tsv_id_col]: i for i, row in enumerate(tsv_body) if tsv_id_col < len(row)}

    if args.mode == "update":
        missing = [i for i in ids if i not in existing_ids]
        if missing:
            sys.exit(f"[abort] update mode: these ids not in tsv: {missing}")
        missing_sheet = [i for i in ids if i not in sheet_rows]
        if missing_sheet:
            sys.exit(f"[abort] these ids not in sheet: {missing_sheet}")
        touched = 0
        for tid in ids:
            old = tsv_body[existing_ids[tid]]
            new = project(sheet_rows[tid], col_map)
            diffs = diff_row(old, new, tsv_hdr)
            if not diffs:
                print(f"[same] {tid}: no change")
                continue
            print(f"[diff] {tid}: {len(diffs)} col(s) changed")
            for i, name, o, n in diffs:
                show_o = o if len(o) <= 80 else o[:77] + "..."
                show_n = n if len(n) <= 80 else n[:77] + "..."
                print(f"    col {i+1} {name}: {show_o!r} -> {show_n!r}")
            tsv_body[existing_ids[tid]] = new
            touched += 1
        print(f"[summary] update {touched}/{len(ids)} rows")

    elif args.mode == "insert":
        dup = [i for i in ids if i in existing_ids]
        if dup:
            sys.exit(f"[abort] insert mode: these ids already in tsv: {dup}")
        missing_sheet = [i for i in ids if i not in sheet_rows]
        if missing_sheet:
            sys.exit(f"[abort] these ids not in sheet: {missing_sheet}")
        for tid in sorted(ids, key=int):
            new = project(sheet_rows[tid], col_map)
            insert_at = 0
            tid_int = int(tid)
            for i, row in enumerate(tsv_body):
                try:
                    if int(row[tsv_id_col]) < tid_int:
                        insert_at = i + 1
                except ValueError:
                    pass
            tsv_body.insert(insert_at, new)
            after = tsv_body[insert_at - 1][tsv_id_col] if insert_at > 0 and tsv_id_col < len(tsv_body[insert_at - 1]) else 'header'
            print(f"[insert] {tid} at line {insert_at + 2} (after {after})")
        print(f"[summary] inserted {len(ids)} rows")

    elif args.mode == "delete":
        missing = [i for i in ids if i not in existing_ids]
        if missing:
            sys.exit(f"[abort] delete mode: these ids not in tsv: {missing}")
        for tid in sorted(ids, key=lambda x: existing_ids[x], reverse=True):
            idx = existing_ids[tid]
            print(f"[delete] {tid} at line {idx + 2}")
            del tsv_body[idx]
            # rebuild index after each delete
            existing_ids = {row[0]: i for i, row in enumerate(tsv_body)}
        print(f"[summary] deleted {len(ids)} rows")

    if args.dry_run:
        print("[dry-run] no file written")
        return

    out_lines = ["\t".join(tsv_hdr)]
    for row in tsv_body:
        out_lines.append("\t".join(row))
    out = line_sep.join(out_lines) + (line_sep if trailing_newline else "")
    args.tsv.write_text(out, encoding="utf-8")
    print(f"[written] {args.tsv} (trailing newline: {trailing_newline})")


if __name__ == "__main__":
    main()
