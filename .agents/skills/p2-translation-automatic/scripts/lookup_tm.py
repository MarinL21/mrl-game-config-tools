"""
翻译记忆查询工具。
精确匹配 + 包含匹配，复用已有翻译保持风格一致。
用法: python lookup_tm.py "中文文本1" "中文文本2" ...
"""
import json
import sys


def load_tm():
    with open("translation_memory.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["entries"]


def lookup(texts):
    tm = load_tm()
    results = {"exact": {}, "partial": {}}

    for text in texts:
        text = text.strip()
        if not text:
            continue

        # Exact match
        if text in tm:
            entry = tm[text]
            results["exact"][text] = {
                "en": entry.get("en", ""),
                "fr": entry.get("fr", ""),
                "de": entry.get("de", ""),
                "jp": entry.get("jp", ""),
                "kr": entry.get("kr", ""),
                "_tab": entry.get("_tab", ""),
                "_id": entry.get("_id", ""),
            }
        else:
            # Partial: find TM entries whose cn is a substring of text, or text is a substring of cn
            partials = []
            for cn, entry in tm.items():
                if len(cn) >= 2 and cn in text and cn != text:
                    partials.append((cn, entry, "text_contains_tm"))
                elif len(text) >= 2 and text in cn and cn != text:
                    partials.append((cn, entry, "tm_contains_text"))
            # Sort by length descending (longer matches first), limit to 5
            partials.sort(key=lambda x: len(x[0]), reverse=True)
            if partials:
                results["partial"][text] = [
                    {
                        "cn": p[0],
                        "en": p[1].get("en", ""),
                        "match_type": p[2],
                        "_tab": p[1].get("_tab", ""),
                        "_id": p[1].get("_id", ""),
                    }
                    for p in partials[:5]
                ]

    return results


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        print('Usage: python lookup_tm.py "text1" "text2" ...')
        return

    texts = sys.argv[1:]
    results = lookup(texts)

    if results["exact"]:
        print("=== EXACT MATCHES (use these translations!) ===")
        for cn, info in results["exact"].items():
            print(f"\n  cn: '{cn}'")
            print(f"  en: '{info['en']}'")
            print(f"  fr: '{info['fr']}'")
            print(f"  de: '{info['de']}'")
            print(f"  jp: '{info['jp']}'")
            print(f"  kr: '{info['kr']}'")
            print(f"  source: {info['_tab']}/{info['_id']}")

    if results["partial"]:
        print("\n=== PARTIAL MATCHES (reference) ===")
        for text, matches in results["partial"].items():
            print(f"\n  looking for: '{text}'")
            for m in matches:
                print(f"    '{m['cn']}' -> en:'{m['en']}' ({m['match_type']}, {m['_tab']}/{m['_id']})")

    if not results["exact"] and not results["partial"]:
        print("No matches found. All texts are new.")


if __name__ == "__main__":
    main()
