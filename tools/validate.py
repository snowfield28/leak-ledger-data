#!/usr/bin/env python3
"""data.json / candidates.json / excluded.json の検証。問題があれば終了コード1。

使い方: python3 tools/validate.py
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CYBER_TYPES = {"ランサムウェア", "不正アクセス", "委託先経由"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def validate():
    D, C, E = load("data.json"), load("candidates.json"), load("excluded.json")
    errs = []
    warns = []
    item_labels, who_labels = D["itemLabels"], D["whoLabels"]
    industries, cause_labels = D["industries"], D["causeLabels"]
    status_labels = D["statusLabels"]

    ids = [x["id"] for x in D["cases"] + C["cases"] + E["cases"]]
    for i, n in Counter(ids).items():
        if n > 1:
            errs.append(f"[重複ID] {i} が3ファイル合わせて{n}回")
    for i in ids:
        if not re.fullmatch(r"[a-z0-9-]+", i):
            errs.append(f"[ID形式] {i}")

    for fname, cases, is_data in (("data", D["cases"], True), ("candidates", C["cases"], False)):
        for x in cases:
            i = x["id"]
            tag = f"[{fname}:{i}]"
            for k in x.get("items", []):
                if k not in item_labels:
                    errs.append(f"{tag} items に未定義キー {k}")
            for w in x.get("who", []) or []:
                if w not in who_labels:
                    errs.append(f"{tag} who に未定義の値 {w}")
            if "ind" in x and x["ind"] not in industries:
                errs.append(f"{tag} ind が industries にない: {x['ind']}")
            if x.get("status") and x["status"] not in status_labels:
                errs.append(f"{tag} status が不正: {x['status']}")
            for k in ("date", "announced", "occurred", "last", "verified"):
                if k in x and x[k] != "" and not DATE_RE.match(str(x[k])):
                    errs.append(f"{tag} {k} の日付形式が不正: {x[k]}")
            if "announced" in x and x.get("date") != x["announced"]:
                errs.append(f"{tag} date({x.get('date')}) が announced({x['announced']}) と違う")
            if "occurred" in x and "announced" in x and x["occurred"] > x["announced"]:
                errs.append(f"{tag} occurred({x['occurred']}) が announced({x['announced']}) より後")
            if is_data:
                for k in ("date", "co", "cause", "types", "n", "label", "st", "sum", "status", "official", "verified", "contact", "who", "ind"):
                    if k not in x or x[k] in (None, "", []) and k not in ("n",):
                        if not (k == "n" and k in x):
                            errs.append(f"{tag} 必須項目 {k} がない")
                if x.get("cause") not in cause_labels:
                    errs.append(f"{tag} cause が不正: {x.get('cause')}")
                elif x["cause"] == "cyber":
                    if not set(x.get("types", [])) <= CYBER_TYPES:
                        errs.append(f"{tag} cyber の types が不正: {x.get('types')}")
                else:
                    if x.get("types") != [cause_labels[x["cause"]]]:
                        warns.append(f"{tag} types は ['{cause_labels[x['cause']]}'] のはず: {x.get('types')}")
                for name, url in x.get("official", []):
                    if not re.search(r"20\d\d[/年]\d{1,2}", name):
                        warns.append(f"{tag} official の名前に発表日（2026/10/8形式）がない: {name}")
                if x.get("st") not in ("c", "p"):
                    errs.append(f"{tag} st が不正: {x.get('st')}")
            else:
                if not x.get("pendingReason"):
                    errs.append(f"{tag} pendingReason がない")
                if "cause" in x and x["cause"] not in cause_labels:
                    errs.append(f"{tag} cause が不正: {x['cause']}")

    for x in E["cases"]:
        for k in ("id", "co", "date", "reason", "official", "checked"):
            if not x.get(k):
                errs.append(f"[excluded:{x.get('id')}] {k} がない")

    if D.get("pendingCount") != len(C["cases"]):
        errs.append(f"pendingCount({D.get('pendingCount')}) が candidates の件数({len(C['cases'])})と違う")
    return errs, warns, (len(D["cases"]), len(C["cases"]), len(E["cases"]))


if __name__ == "__main__":
    errors, warnings, counts = validate()
    print("data/candidates/excluded = %d/%d/%d" % counts)
    if warnings:
        print("警告 %d 件（終了コードには影響しない）" % len(warnings))
        for w in warnings[:15]:
            print(" ", w)
        if len(warnings) > 15:
            print("  ...ほか %d 件" % (len(warnings) - 15))
    if errors:
        print("エラー %d 件" % len(errors))
        for e in errors:
            print(" ", e)
        sys.exit(1)
    print("OK")
