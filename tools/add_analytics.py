#!/usr/bin/env python3
"""全HTMLに GoatCounter の計測タグを足す（すでに入っていれば何もしない）。build_pages.py の最後に呼ばれる。"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = '<script data-goatcounter="https://snow.goatcounter.com/count"\n        async src="//gc.zgo.at/count.js"></script>\n'


VERIFY = '<meta name="google-site-verification" content="Y-b7XfgSWxYdmYGcW0NcX9K-fwld9aktyLhifqb7-5g">\n<meta name="msvalidate.01" content="73462A96654CDE9A16167193A35A254E">\n'


def add_verification():
    """Search Console の所有権確認用タグを、トップページ（index.html）にだけ入れる。"""
    p = os.path.join(ROOT, "index.html")
    s = open(p, encoding="utf-8").read()
    if "</head>" not in s:
        return 0
    add = "".join(l + "\n" for l in VERIFY.splitlines() if l.split('name="')[1].split('"')[0] not in s)
    if not add:
        return 0
    open(p, "w", encoding="utf-8").write(s.replace("</head>", add + "</head>", 1))
    return 1


def run():
    n = add_verification()
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "backfill", "tools", "node_modules")]
        for f in fn:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            s = open(p, encoding="utf-8").read()
            if "goatcounter" in s or "</head>" not in s:
                continue
            open(p, "w", encoding="utf-8").write(s.replace("</head>", TAG + "</head>", 1))
            n += 1
    return n


if __name__ == "__main__":
    print("analytics tag added to", run(), "files")
