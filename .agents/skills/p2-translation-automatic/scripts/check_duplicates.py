"""
检查新生成的 key 是否与现有 key 重复。
用法: python check_duplicates.py key1 key2 key3 ...
"""
import json
import sys


def load_keys():
    with open("all_existing_keys.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["keys"]


def check(new_keys):
    existing = load_keys()
    conflicts = []
    ok = []
    for key in new_keys:
        if key in existing:
            conflicts.append((key, existing[key]))
        else:
            ok.append(key)
    return ok, conflicts


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_duplicates.py key1 key2 ...")
        return

    new_keys = sys.argv[1:]
    ok, conflicts = check(new_keys)

    if conflicts:
        print(f"CONFLICT! {len(conflicts)} key(s) already exist:")
        for key, tab in conflicts:
            print(f"  '{key}' already in tab '{tab}'")
    else:
        print(f"All {len(ok)} keys are unique, no conflicts.")

    if ok:
        print(f"\nOK keys ({len(ok)}):")
        for k in ok:
            print(f"  {k}")


if __name__ == "__main__":
    main()
