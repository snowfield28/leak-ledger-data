#!/usr/bin/env python3
"""全HTMLに、雑誌風の見た目（リポジトリ直下の mag.css）の読み込みタグを足す。build_pages.py の最後に呼ばれる。

- タグは </head> の直前（ほかの <style> より後）に置き、既存CSSを上書きする。
- ページの階層に合わせて相対パスを変える（直下は mag.css、case/ と en/ は ../mag.css、en/case/ は ../../mag.css）。
- mag.css の内容のハッシュを ?v= に付けるので、CSSを直すとタグも自動で更新される。
- すでに入っているタグは外して入れ直す（en/index.html は index.html の複製でパスがずれるため、毎回直す）。
"""
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(ROOT, "mag.css")
OLD = re.compile(r'<link rel="stylesheet" id="mag-css"[^>]*>\n?')


def version():
    return hashlib.md5(open(CSS, "rb").read()).hexdigest()[:8]


def run():
    ver = version()
    n = 0
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "backfill", "tools", "node_modules")]
        for f in fn:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            s = open(p, encoding="utf-8").read()
            if "</head>" not in s:
                continue
            href = os.path.relpath(CSS, dp).replace(os.sep, "/")
            tag = f'<link rel="stylesheet" id="mag-css" href="{href}?v={ver}">\n'
            t = OLD.sub("", s).replace("</head>", tag + "</head>", 1)
            if t != s:
                open(p, "w", encoding="utf-8").write(t)
                n += 1
    return n


if __name__ == "__main__":
    print("magazine style linked in", run(), "files")
