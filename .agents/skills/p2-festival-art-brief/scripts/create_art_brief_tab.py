#!/usr/bin/env python3
"""Create a P2 festival art-brief tab in the localization master sheet.

Output matches the layout used by existing festival tabs in
`1pPlo0ccRBmlQj9OFWnGXhQg1wLiihfQfSxEsoKA0hLA`:

  | A 模块名 | B 功能说明 | C 功能描述 | D 文案需求 | E 往年图片 | F 文案(本地化) | G 美需描述 | H 参考图 |

Usage:
    python3 create_art_brief_tab.py spec.json [--dry-run] [--allow-append]

    --allow-append  skip the `insertAfterTabTitle` requirement and append the
                    new tab at the end. Only use for throwaway smoke tests;
                    never for real festival art briefs.

spec.json schema:
{
  "spreadsheetId":       "1pPlo0ccRBmlQj9OFWnGXhQg1wLiihfQfSxEsoKA0hLA",
  "newTabTitle":         "2027 3月上线-科技节（蒸汽朋克）",
  "insertAfterTabTitle": "2026 3月上线-科技节套装",   // REQUIRED — see note below
  "rows": [
    {
      "moduleGroup":  "套装LV.1",
      "moduleName":   "低级城堡",
      "functionDesc": "低级城堡，套装最初始的组件…",
      "copyNeed":     "名称&描述",
      "copy":         "名称：齿轮堡\n描述：蒸汽齿轮驱动的钢铁城堡。",
      "artBrief":     "主体：…\n底座：…\n动态：…\n避坑：…",
      "refs": [
        // Search-keyword mode (rendered as a Google Images search link).
        {"label": "主图",    "searchQuery": "steampunk gear castle concept art"},
        // Direct-URL mode (rendered as a hyperlink to that URL — image direct
        // link or landing page both work; Sheets never loads the image).
        {"label": "底座参考", "url": "https://cdna.artstation.com/xxx.jpg"}
      ]
    }
  ]
}

Behavior:
  1. Adds a new sheet with 8 columns, frozen header row, and standard column widths.
  2. Inserts it right after `insertAfterTabTitle`. This field is REQUIRED: the master
     sheet is organized year-desc + month-asc (2026 各月 → 2025 各月 → ...), so new
     festival art-brief tabs must slot in after the same-year (N-1) month's festival
     tab. e.g. a 10-月万圣节 brief goes after "2026 9月上线-音乐节-主城+行军特效补包";
     a 2-月情人节 brief goes after "2026 1月上线-春节"; a 1-月春节 brief goes after
     the prior year's 12-月圣诞节. When in doubt, list the existing tabs via gws and
     eyeball the right anchor.
  3. Column E (往年图片) is intentionally left blank — user drops historical screenshots here.
  4. Column H (参考图) is rich-text: one blue hyperlinked label per ref
     (①主图 / ②底座 / ③动态 / ④配色 …). Art clicks any label to jump to
     the Google Images search (or direct URL) for that ref.
  5. Never calls the network — links are constructed locally, the script is offline-only.
  6. Prints the new tab URL on stdout.
"""

import json
import subprocess
import sys
import urllib.parse
from pathlib import Path


HEADER = ["", "模块名", "功能说明", "文案需求", "往年图片",
          "文案（本地化）", "美需描述", "参考图"]

HEADER_BG = {"red": 0.8509804, "green": 0.91764706, "blue": 0.827451}
BRIEF_BG  = {"red": 0.91764706, "green": 0.81960785, "blue": 0.8627451}
LINK_BLUE = {"red": 0.067, "green": 0.4, "blue": 0.8}

COL_WIDTHS   = {0: 110, 1: 140, 2: 320, 3: 110, 4: 180, 5: 260, 6: 380, 7: 240}
DATA_ROW_PX  = 180
N_COLUMNS    = 8

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/{sid}/edit#gid={gid}"


def gws(*args, params=None, body=None, dry_run=False):
    cmd = ["gws"] + list(args)
    if params is not None:
        cmd += ["--params", json.dumps(params, ensure_ascii=False)]
    if body is not None:
        cmd += ["--json", json.dumps(body, ensure_ascii=False)]
    if dry_run:
        print("DRY-RUN:", " ".join(cmd), file=sys.stderr)
        return {}
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"gws {' '.join(args)} failed (exit {result.returncode})")
    out = result.stdout
    if out.startswith("Using keyring backend:"):
        out = out.split("\n", 1)[1] if "\n" in out else ""
    out = out.strip()
    return json.loads(out) if out.startswith(("{", "[")) else out


def circled(i: int) -> str:
    return chr(0x2460 + i) if 0 <= i <= 19 else f"[{i+1}]"


def resolve_ref_url(ref: dict) -> str:
    if ref.get("url"):
        return ref["url"]
    if ref.get("searchQuery"):
        return f"https://www.google.com/search?q={urllib.parse.quote(ref['searchQuery'])}&tbm=isch"
    return ""


def build_values_and_rich(rows: list) -> tuple[list, list]:
    grid = [HEADER]
    rich_h_specs = []
    for row_i, r in enumerate(rows):
        refs = r.get("refs") or []
        grid.append([
            r.get("moduleGroup", ""),
            r.get("moduleName", ""),
            r.get("functionDesc", ""),
            r.get("copyNeed", ""),
            "",                          # E 往年图片 — leave blank
            r.get("copy", ""),
            (r.get("artBrief") or "").rstrip(),
            "",                          # H — filled via rich-text below
        ])
        if not refs:
            continue
        labels = [f"{circled(i)} {(ref.get('label') or '参考').strip()}"
                  for i, ref in enumerate(refs)]
        urls = [resolve_ref_url(ref) for ref in refs]
        text = "\n".join(labels)
        runs = []
        cursor = 0
        for label, url in zip(labels, urls):
            if url:
                runs.append({
                    "startIndex": cursor,
                    "format": {
                        "link": {"uri": url},
                        "foregroundColor": LINK_BLUE,
                        "underline": True,
                    },
                })
            cursor += len(label) + 1     # +1 for the "\n" separator
        rich_h_specs.append({
            "rowIndex": row_i + 1,       # +1 for header
            "text": text,
            "runs": runs,
        })
    return grid, rich_h_specs


def rich_h_requests(sheet_id: int, specs: list) -> list:
    reqs = []
    for spec in specs:
        reqs.append({
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": spec["rowIndex"],
                    "endRowIndex": spec["rowIndex"] + 1,
                    "startColumnIndex": 7,
                    "endColumnIndex": 8,
                },
                "rows": [{
                    "values": [{
                        "userEnteredValue": {"stringValue": spec["text"]},
                        "textFormatRuns": spec["runs"],
                    }],
                }],
                "fields": "userEnteredValue,textFormatRuns",
            }
        })
    return reqs


def format_requests(sheet_id: int, n_rows: int) -> list:
    reqs = [
        {"repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {
                "backgroundColor": HEADER_BG,
                "textFormat": {"bold": True},
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "MIDDLE",
                "wrapStrategy": "WRAP",
            }},
            "fields": ("userEnteredFormat(backgroundColor,textFormat,"
                       "horizontalAlignment,verticalAlignment,wrapStrategy)"),
        }},
        {"repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 1,
                      "startColumnIndex": 6, "endColumnIndex": 7},
            "cell": {"userEnteredFormat": {"backgroundColor": BRIEF_BG}},
            "fields": "userEnteredFormat.backgroundColor",
        }},
        {"repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 1},
            "cell": {"userEnteredFormat": {
                "wrapStrategy": "WRAP",
                "verticalAlignment": "TOP",
            }},
            "fields": "userEnteredFormat(wrapStrategy,verticalAlignment)",
        }},
        {"updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "ROWS",
                      "startIndex": 1, "endIndex": n_rows},
            "properties": {"pixelSize": DATA_ROW_PX},
            "fields": "pixelSize",
        }},
    ]
    for col, px in COL_WIDTHS.items():
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                      "startIndex": col, "endIndex": col + 1},
            "properties": {"pixelSize": px},
            "fields": "pixelSize",
        }})
    return reqs


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    allow_append = "--allow-append" in args
    args = [a for a in args if a not in ("--dry-run", "--allow-append")]
    if not args:
        sys.exit("usage: create_art_brief_tab.py spec.json [--dry-run] [--allow-append]")

    spec = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    sid   = spec["spreadsheetId"]
    title = spec["newTabTitle"]
    rows  = spec["rows"]
    insert_after = spec.get("insertAfterTabTitle")
    if not insert_after and not allow_append:
        sys.exit(
            "spec.insertAfterTabTitle is required.\n"
            "Festival art-brief tabs must slot into the master sheet in calendar order "
            "(year-desc + month-asc), not be appended to the end. "
            "Set insertAfterTabTitle to the same-year (N-1) month's festival tab name, "
            "e.g. a 10-月万圣节 brief anchors to '2026 9月上线-音乐节-主城+行军特效补包'. "
            "For intentional throwaway tabs only, pass --allow-append."
        )
    n_rows = len(rows) + 1

    probe = gws("sheets", "spreadsheets", "get",
                params={"spreadsheetId": sid,
                        "fields": "sheets.properties(title,index,sheetId)"})
    titles = [s["properties"]["title"] for s in probe["sheets"]]
    if title in titles:
        sys.exit(f"tab '{title}' already exists — choose a different newTabTitle")

    add_props = {
        "title": title,
        "gridProperties": {
            "rowCount": max(n_rows + 20, 100),
            "columnCount": N_COLUMNS,
            "frozenRowCount": 1,
        },
    }
    if insert_after:
        matches = [s for s in probe["sheets"]
                   if s["properties"]["title"] == insert_after]
        if not matches:
            sys.exit(f"insertAfterTabTitle '{insert_after}' not found")
        add_props["index"] = matches[0]["properties"]["index"] + 1

    resp = gws("sheets", "spreadsheets", "batchUpdate",
               params={"spreadsheetId": sid},
               body={"requests": [{"addSheet": {"properties": add_props}}]},
               dry_run=dry_run)
    sheet_id = 0 if dry_run else resp["replies"][0]["addSheet"]["properties"]["sheetId"]

    values, rich_h_specs = build_values_and_rich(rows)
    gws("sheets", "spreadsheets", "values", "update",
        params={"spreadsheetId": sid,
                "range": f"'{title}'!A1",
                "valueInputOption": "USER_ENTERED"},
        body={"values": values},
        dry_run=dry_run)

    fmt_reqs = format_requests(sheet_id, n_rows) + rich_h_requests(sheet_id, rich_h_specs)
    gws("sheets", "spreadsheets", "batchUpdate",
        params={"spreadsheetId": sid},
        body={"requests": fmt_reqs},
        dry_run=dry_run)

    print(SPREADSHEET_URL.format(sid=sid, gid=sheet_id))


if __name__ == "__main__":
    main()
