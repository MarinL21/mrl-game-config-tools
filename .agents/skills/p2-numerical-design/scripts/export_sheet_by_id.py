# -*- coding: utf-8 -*-
"""
从 Google Sheet 按 sheetId 导出数据（依赖本机 gws 认证）。
默认输出到本 skill 的 `data/`（道具锚点价值等数值索引）。

用法：
  python export_sheet_by_id.py <spreadsheetId> <sheetId> <startRow> <endRow> <colCount> [outDir]

示例（道具锚点价值页）：
  python export_sheet_by_id.py 11_Lt3X-HPcuS9U9VQKbYMHDJkB7ROwXw5Xpgi5uMkwk 1791665336 0 4000 25
"""
import csv
import json
import pathlib
import shutil
import subprocess
import sys


def _default_out_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent / "data"


def batch_get(gw: str, spreadsheet_id: str, sheet_id: int, r0: int, r1: int, c1: int):
    params = json.dumps({"spreadsheetId": spreadsheet_id})
    body = json.dumps(
        {
            "dataFilters": [
                {
                    "gridRange": {
                        "sheetId": sheet_id,
                        "startRowIndex": r0,
                        "endRowIndex": r1,
                        "startColumnIndex": 0,
                        "endColumnIndex": c1,
                    }
                }
            ]
        }
    )
    r = subprocess.run(
        [gw, "sheets", "spreadsheets", "values", "batchGetByDataFilter", "--params", params, "--json", body],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if r.returncode != 0:
        sys.stderr.write(r.stderr or "")
        sys.exit(r.returncode)
    data = json.loads(r.stdout)
    return data["valueRanges"][0]["valueRange"].get("values") or []


def main():
    gw = shutil.which("gws") or shutil.which("gws.cmd")
    if not gw:
        sys.exit("gws not found")

    if len(sys.argv) < 6:
        print(__doc__)
        sys.exit(2)

    spreadsheet_id = sys.argv[1]
    sheet_id = int(sys.argv[2])
    r0 = int(sys.argv[3])
    r1 = int(sys.argv[4])
    cols = int(sys.argv[5])
    out_dir = pathlib.Path(sys.argv[6]) if len(sys.argv) > 6 else _default_out_dir()

    rows = batch_get(gw, spreadsheet_id, sheet_id, r0, r1, cols)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"sheet_{sheet_id}"

    json_path = out_dir / f"{stem}_full.json"
    csv_path = out_dir / f"{stem}_full.csv"
    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        for row in rows:
            w.writerow(row + [""] * (cols - len(row)))

    print(json_path)
    print(csv_path)
    print("rows", len(rows))


if __name__ == "__main__":
    main()
