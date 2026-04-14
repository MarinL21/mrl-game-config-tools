"""
术语规范库查询工具 - 优先级最高，命中即用，无需再检索。
用法:
  查询:   python glossary_lookup.py "阶段" "运输车" "宴会券"
  添加:   python glossary_lookup.py --add "阶段" en=Stage fr=Niveau source=EVENT/xxx note="说明"
  列表:   python glossary_lookup.py --list
"""
import json
import sys
import os
from datetime import date

GLOSSARY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glossary.json")

LANG_ORDER = ["en", "fr", "de", "po", "zh", "id", "th", "sp", "ru", "tr", "vi", "it", "pl", "ar", "jp", "kr"]


def load_glossary():
    if not os.path.exists(GLOSSARY_FILE):
        return {"_meta": {"total_terms": 0}, "terms": {}}
    with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_glossary(data):
    data["_meta"]["total_terms"] = len(data["terms"])
    data["_meta"]["updated"] = str(date.today())
    with open(GLOSSARY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def lookup(terms):
    glossary = load_glossary()
    all_terms = glossary.get("terms", {})

    found = {}
    not_found = []

    for term in terms:
        term = term.strip()
        if not term:
            continue

        if term in all_terms:
            found[term] = all_terms[term]
        else:
            for cn, entry in all_terms.items():
                if term in cn or cn in term:
                    found[term] = {**entry, "_matched_via": cn}
                    break
            else:
                not_found.append(term)

    return found, not_found


def add_term(cn, translations):
    glossary = load_glossary()
    entry = {}
    for kv in translations:
        if "=" in kv:
            k, v = kv.split("=", 1)
            entry[k] = v
    glossary["terms"][cn] = entry
    save_glossary(glossary)
    print(f"Added '{cn}' to glossary ({len(entry)} fields)")


def list_all():
    glossary = load_glossary()
    terms = glossary.get("terms", {})
    print(f"Glossary: {len(terms)} terms (updated: {glossary['_meta'].get('updated', '?')})\n")
    print(f"{'CN':<20} {'EN':<30} {'Source'}")
    print("-" * 75)
    for cn, entry in sorted(terms.items()):
        en = entry.get("en", "?")
        source = entry.get("source", "?")
        print(f"  {cn:<18} {en:<28} {source}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    if len(sys.argv) < 2:
        print('Usage: python glossary_lookup.py "term1" "term2" ...')
        print('       python glossary_lookup.py --add "cn" en=xxx fr=xxx ...')
        print('       python glossary_lookup.py --list')
        return

    if sys.argv[1] == "--list":
        list_all()
        return

    if sys.argv[1] == "--add":
        if len(sys.argv) < 4:
            print("Usage: --add <cn_term> key=value key=value ...")
            return
        add_term(sys.argv[2], sys.argv[3:])
        return

    terms = sys.argv[1:]
    found, not_found = lookup(terms)

    if found:
        print("✅ GLOSSARY MATCHES (use these, no further search needed):\n")
        for term, entry in found.items():
            matched_via = entry.pop("_matched_via", None)
            source = entry.get("source", "")
            note = entry.get("note", "")

            if matched_via:
                print(f"  '{term}' (matched via glossary entry '{matched_via}'):")
            else:
                print(f"  '{term}':")

            for lang in LANG_ORDER:
                if lang in entry:
                    print(f"    {lang:>4}: {entry[lang]}")

            if source:
                print(f"    src: {source}")
            if note:
                print(f"    note: {note}")
            print()

    if not_found:
        print(f"❌ NOT IN GLOSSARY ({len(not_found)}) — run search_terms.py for these:")
        for t in not_found:
            print(f"  {t}")


if __name__ == "__main__":
    main()
