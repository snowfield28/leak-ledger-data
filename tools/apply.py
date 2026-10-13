#!/usr/bin/env python3
"""パッチJSONを data.json / candidates.json / excluded.json に反映し、検証して、個別ページを作り直す。

パッチの形式:
  {"add":[case...], "candidates":[case...], "excluded":[{...}], "updates":[{"id":"..","set":{..}}],
   "inbox_done":["記事URL", ...]}      # inbox_done は inbox.json から外す記事URL（任意）

  add         台帳に追加（candidates / excluded に同じidがあれば外す）
  candidates  保留に追加。同じidが保留にあれば上書きマージ（位置は保つ）
  excluded    対象外に追加（candidates / data に同じidがあれば candidates から外す）
  updates     data.json の既存事案のキーを丸ごと置き換える（official・src は完全なリストで渡す）

使い方:
  python3 tools/apply.py patch.json            # 反映 → 検証 → ページ生成
  python3 tools/apply.py patch.json --dry-run  # 件数だけ表示、ファイルは書かない
  python3 tools/apply.py patch.json --no-build # ページ生成を省く
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from validate import validate  # noqa: E402


def jst_today():
    return (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y-%m-%d")


def dump(name, obj):
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("patch", nargs="+")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    D = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
    C = json.loads((ROOT / "candidates.json").read_text(encoding="utf-8"))
    E = json.loads((ROOT / "excluded.json").read_text(encoding="utf-8"))
    today = jst_today()
    log = {"add": 0, "candidates": 0, "excluded": 0, "updates": 0}
    inbox_done = set()

    for pf in args.patch:
        patch = json.loads(Path(pf).read_text(encoding="utf-8"))
        data_ids = {c["id"] for c in D["cases"]}

        for x in patch.get("add", []):
            x = dict(x)
            x.pop("pendingReason", None)
            x.pop("auto", None)
            if x["id"] in data_ids:
                sys.exit(f"add: {x['id']} は既に data.json にある（updates を使う）")
            C["cases"] = [c for c in C["cases"] if c["id"] != x["id"]]
            E["cases"] = [c for c in E["cases"] if c["id"] != x["id"]]
            x.setdefault("verified", today)
            D["cases"].append(x)
            data_ids.add(x["id"])
            log["add"] += 1

        for x in patch.get("candidates", []):
            if x["id"] in data_ids:
                sys.exit(f"candidates: {x['id']} は既に data.json にある")
            hit = [c for c in C["cases"] if c["id"] == x["id"]]
            if hit:
                hit[0].update(x)
            else:
                C["cases"].append(x)
            log["candidates"] += 1

        for x in patch.get("excluded", []):
            C["cases"] = [c for c in C["cases"] if c["id"] != x["id"]]
            E["cases"] = [c for c in E["cases"] if c["id"] != x["id"]]
            x.setdefault("checked", today)
            E["cases"].append(x)
            log["excluded"] += 1

        for u in patch.get("updates", []):
            hit = [c for c in D["cases"] if c["id"] == u["id"]]
            if not hit:
                sys.exit(f"updates: {u['id']} が data.json にない")
            hit[0].update(u["set"])
            hit[0].setdefault("verified", today)
            log["updates"] += 1

        inbox_done.update(patch.get("inbox_done", []))

    D["updated"] = today
    D["pendingCount"] = len(C["cases"])
    C["updated"] = today

    # 書く前に、メモリ上のデータで検証できるよう一時的に書き出して検証する
    backup = {n: (ROOT / n).read_text(encoding="utf-8") for n in ("data.json", "candidates.json", "excluded.json")}
    dump("data.json", D)
    dump("candidates.json", C)
    dump("excluded.json", E)
    errors, warnings, counts = validate()
    print("反映: ", log, "→ data/candidates/excluded = %d/%d/%d" % counts)
    if errors or args.dry_run:
        for n, t in backup.items():
            (ROOT / n).write_text(t, encoding="utf-8")
        if errors:
            print("検証エラーのため元に戻しました:")
            for e in errors:
                print(" ", e)
            sys.exit(1)
        print("dry-run: ファイルは変更していません")
        return

    inbox_path = ROOT / "inbox.json"
    if inbox_done and inbox_path.exists():
        inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
        before = len(inbox.get("items", []))
        inbox["items"] = [i for i in inbox.get("items", []) if i["article_url"] not in inbox_done]
        dump("inbox.json", inbox)
        print("inbox: %d → %d 件" % (before, len(inbox["items"])))

    if not args.no_build:
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_pages.py")], cwd=ROOT, check=True)
    print("完了")


if __name__ == "__main__":
    main()
