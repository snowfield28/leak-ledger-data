#!/usr/bin/env python3
"""全HTMLに GoatCounter の計測タグを足す（すでに入っていれば何もしない）。build_pages.py の最後に呼ばれる。"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = '<script data-goatcounter="https://snow.goatcounter.com/count"\n        async src="//gc.zgo.at/count.js"></script>\n'


VERIFY = '<meta name="google-site-verification" content="pWnu-a6OhQ5ZUiNeg6Qyb8iGfyRPlF1DIUd4ssGKwKQ">\n'


def add_verification():
    """Search Console の所有権確認用タグを、トップページ（index.html）にだけ入れる。"""
    p = os.path.join(ROOT, "index.html")
    s = open(p, encoding="utf-8").read()
    if "google-site-verification" in s or "</head>" not in s:
        return 0
    open(p, "w", encoding="utf-8").write(s.replace("</head>", VERIFY + "</head>", 1))
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
