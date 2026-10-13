#!/usr/bin/env python3
"""全HTMLに、共有時に出る画像（ogp.png）の指定を足す。入っていれば何もしない。build_pages.py の最後に呼ばれる。"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = "https://snowfield28.github.io/leak-ledger-data/ogp.png"
TAG = (f'<meta property="og:image" content="{IMG}">\n<meta property="og:image:width" content="1200">\n'
       f'<meta property="og:image:height" content="630">\n<meta name="twitter:card" content="summary_large_image">\n'
       f'<meta name="twitter:image" content="{IMG}">\n')


def run():
    n = 0
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "backfill", "tools", "node_modules")]
        for f in fn:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            s = open(p, encoding="utf-8").read()
            if "og:image" in s or "</head>" not in s:
                continue
            open(p, "w", encoding="utf-8").write(s.replace("</head>", TAG + "</head>", 1))
            n += 1
    return n


if __name__ == "__main__":
    print("og:image added to", run(), "files")
