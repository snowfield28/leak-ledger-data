#!/usr/bin/env python3
"""data.json から検索エンジン向けの静的ページを作る。

作るもの:
  case/<id>.html   事案ごとのページ（1事案1URL）
  case/index.html  全事案の一覧（年月ごと）
  sitemap.xml      全ページの一覧

使い方: リポジトリの直下で `python3 tools/build_pages.py`
data.json を更新したら毎回実行する。
"""
import html, json, os, re, shutil
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://snowfield28.github.io/leak-ledger-data/"
STATIC = ["", "about.html", "privacy.html", "contact.html"]

e = lambda s: html.escape(str(s if s is not None else ""), quote=True)


def jdate(s):
    y, m, d = s.split("-")
    return f"{int(y)}年{int(m)}月{int(d)}日"


def ym(s):
    y, m, _ = s.split("-")
    return f"{int(y)}年{int(m)}月"


CSS = """
:root{--bg:#f3f5f7;--surface:#fff;--ink:#16202b;--muted:#5b6876;--line:#d9dfe5;--accent:#b4530b;--accent-soft:#fbeadb;
 --confirmed:#a3271f;--confirmed-soft:#f8e1de;--possible:#7a5d00;--possible-soft:#f6edcc;--done:#2f6b4f;--done-soft:#dcefe5;
 --f-ui:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic UI","Meiryo",sans-serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0f151c;--surface:#16202a;--ink:#e4eaf0;--muted:#97a5b3;--line:#2a3744;
 --accent:#f0954a;--accent-soft:#3a2615;--confirmed:#f28b82;--confirmed-soft:#3b1f1d;--possible:#e3c25a;--possible-soft:#332b12;--done:#86d3ac;--done-soft:#1b3328;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f151c;--surface:#16202a;--ink:#e4eaf0;--muted:#97a5b3;--line:#2a3744;--accent:#f0954a;--accent-soft:#3a2615;
 --confirmed:#f28b82;--confirmed-soft:#3b1f1d;--possible:#e3c25a;--possible-soft:#332b12;--done:#86d3ac;--done-soft:#1b3328;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-ui);line-height:1.75;padding:12px 16px 48px}
main{max-width:760px;margin:0 auto}
a{color:var(--accent)}
.crumb{font-size:13px;margin:4px 0 14px;display:flex;flex-wrap:wrap;gap:4px 8px;color:var(--muted)}
h1{font-size:22px;line-height:1.45;margin:0 0 8px}
.pills{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}
.pill{font-size:12px;padding:2px 9px;border-radius:99px;white-space:nowrap}
.pill.c{background:var(--confirmed-soft);color:var(--confirmed)}.pill.p{background:var(--possible-soft);color:var(--possible)}
.pill.closed{background:var(--done-soft);color:var(--done)}.pill.ongoing{border:1px solid var(--line);color:var(--muted)}
section{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin-bottom:12px}
h2{font-size:15px;margin:0 0 8px}
p,li{font-size:15px;margin:0 0 6px}
ul{padding-left:1.2em;margin:0}
dl{display:grid;grid-template-columns:auto 1fr;margin:0;font-size:14px}
dt{color:var(--muted);padding:7px 14px 7px 0;border-top:1px solid var(--line);white-space:nowrap}
dd{margin:0;padding:7px 0;border-top:1px solid var(--line);min-width:0}
dt:first-of-type,dd:first-of-type{border-top:none}
.items{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
.items span{font-size:13px;background:var(--confirmed-soft);color:var(--confirmed);border-radius:8px;padding:3px 9px;font-weight:600}
.note{font-size:13px;color:var(--muted)}
.lk{display:block;padding:9px 12px;border:1px solid var(--line);border-radius:10px;margin-bottom:6px;text-decoration:none;color:var(--ink);font-size:14px;word-break:break-all}
.lk.off{border-color:var(--accent);background:var(--accent-soft)}
.lk small{display:block;color:var(--muted);font-size:12px}
.btn{display:inline-block;background:var(--ink);color:var(--bg);text-decoration:none;font-weight:700;border-radius:10px;padding:10px 16px;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:8px 6px;border-top:1px solid var(--line);vertical-align:top}
th{font-size:12px;color:var(--muted);font-weight:600}
td.r,th.r{text-align:right;white-space:nowrap}
nav.foot{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;margin-top:20px}
nav.foot a{color:var(--muted)}
@media (min-width:900px){body{padding:24px 32px 64px}h1{font-size:28px}.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}.two section{margin-bottom:0}.two{margin-bottom:12px}}
"""

FOOT = """<nav class="foot" aria-label="サイト情報"><a href="{r}">台帳</a><a href="{r}case/">全事案一覧</a><a href="{r}about.html">このサイトについて</a><a href="{r}privacy.html">プライバシーポリシー</a><a href="{r}contact.html">お問い合わせ・訂正依頼</a></nav>"""


def head(title, desc, url, typ="article"):
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="{typ}">
<meta property="og:url" content="{e(url)}">
<meta property="og:site_name" content="国内情報漏えい台帳">
<style>{CSS}</style>
</head>
<body><main>
"""


def case_page(c, D):
    L, CL, WL = D["itemLabels"], D["causeLabels"], D.get("whoLabels", {})
    url = f"{SITE}case/{c['id']}.html"
    cause = CL.get(c.get("cause", "cyber"), "")
    if c.get("cause", "cyber") == "cyber" and c.get("types"):
        cause += "（" + "・".join(c["types"]) + "）"
    title = f"{c['co']}の個人情報漏えい（{ym(c['date'])}）｜国内情報漏えい台帳"
    desc = f"{c['co']}の情報漏えい事案。件数：{c['label']}。原因：{cause}。流出した情報：{c['itemsText']}"
    desc = desc[:150] + ("…" if len(desc) > 150 else "")
    who = "、".join(WL.get(k, k) for k in c.get("who", [])) or "—"
    items = "".join(f"<span>{e(L[k])}</span>" for k in c.get("items", []) if k in L)
    resp = [s.strip() for s in (c.get("resp") or "").split("。") if s.strip()]
    k = c.get("contact") or {}
    ct = []
    for t in k.get("tels", []):
        ct.append(f'<a class="lk" href="tel:{e(t["tel"].replace("-", ""))}"><b>{e(t["tel"])}</b>{"<small>" + e(t["hours"]) + "</small>" if t.get("hours") else ""}</a>')
    for m in k.get("mails", []):
        ct.append(f'<a class="lk" href="mailto:{e(m)}">{e(m)}<small>メール</small></a>')
    for n, u in k.get("forms", []):
        ct.append(f'<a class="lk" href="{e(u)}" rel="noopener">{e(n)}<small>フォーム</small></a>')
    if k.get("note"):
        ct.append(f'<p class="note">{e(k["note"])}</p>')
    if not ct:
        ct.append('<p class="note">公式発表に窓口の記載なし</p>')
    if k.get("src"):
        ct.append(f'<p class="note">出典：<a href="{e(k["src"])}" rel="noopener">公式発表</a>に記載の窓口。受付期間が終わっていることがあるため、連絡の前に公式発表を確認してください。</p>')
    off = "".join(f'<a class="lk off" href="{e(u)}" rel="noopener">{e(n)}<small>{e(u)}</small></a>' for n, u in c.get("official", []))
    src = "".join(f'<a class="lk" href="{e(u)}" rel="noopener">{e(n)}</a>' for n, u in c.get("src", []))
    status = "調査完了" if c.get("status") == "closed" else "調査中"
    rows = [("件数", c["label"]), ("日付", f"{jdate(c['date'])}（発生・検知または初回公表）")]
    if c.get("last"):
        rows.append(("最新の続報", jdate(c["last"])))
    rows += [("業種", c.get("ind", "—")), ("原因", cause), ("誰の情報", who)]
    if c.get("claim"):
        rows.append(("犯行声明", c["claim"]))
    if c.get("verified"):
        rows.append(("最終確認日", f"{jdate(c['verified'])}（公式発表と照合）"))
    dl = "".join(f"<dt>{e(a)}</dt><dd>{e(b)}</dd>" for a, b in rows)
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": f"{c['co']}の個人情報漏えい（{ym(c['date'])}）",
          "datePublished": c["date"], "dateModified": c.get("last") or c.get("verified") or c["date"],
          "inLanguage": "ja", "url": url, "publisher": {"@type": "Organization", "name": "国内情報漏えい台帳"}}
    return head(title, desc, url) + f"""<nav class="crumb" aria-label="パンくず"><a href="../">台帳</a><span>›</span><a href="./">全事案一覧</a><span>›</span><span>{e(c['co'])}</span></nav>
<h1>{e(c['co'])}の個人情報漏えい</h1>
<div class="pills"><span class="pill {e(c.get('st'))}">{'漏えい確認' if c.get('st') == 'c' else '漏えいの可能性'}</span><span class="pill {e(c.get('status'))}">{status}</span></div>
<section><h2>事案の概要</h2><dl>{dl}</dl></section>
<section><h2>流出した情報</h2><div class="items">{items or '<span>項目は公表資料で要確認</span>'}</div><p>{e(c.get('itemsText'))}</p>{'<p class="note">含まれない情報：' + e(c['notIncl']) + '</p>' if c.get('notIncl') else ''}</section>
<section><h2>何が起きたか</h2><p>{e(c.get('sum'))}</p></section>
<div class="two">
<section><h2>調査の状況</h2><p>{e(c.get('statusText') or '—')}</p></section>
<section><h2>組織の対応</h2>{'<ul>' + ''.join(f'<li>{e(r)}。</li>' for r in resp) + '</ul>' if resp else '<p class="note">未確認</p>'}</section>
</div>
<section><h2>お問い合わせ先</h2>{''.join(ct)}</section>
<section><h2>一次情報（公式発表）</h2>{off or '<p class="note">未確認</p>'}</section>
{'<section><h2>報道</h2>' + src + '</section>' if src else ''}
<p><a class="btn" href="../#{e(c['id'])}">台帳でほかの事案と比べる</a></p>
<p class="note">この台帳は、報道や一覧で見つけた事案のうち、組織自身の公式発表を開いて内容が一致したものだけを載せています。概要は公式発表と報道から事実を取り出して書いたもので、正確な内容は公式発表で確認してください。誤りは<a href="../contact.html">お問い合わせ・訂正依頼</a>からお知らせください。</p>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{FOOT.format(r='../')}
</main></body>
</html>
"""


def index_page(cases, D):
    url = f"{SITE}case/"
    by = defaultdict(list)
    for c in cases:
        by[c["date"][:7]].append(c)
    parts = []
    for k in sorted(by, reverse=True):
        y, m = k.split("-")
        rows = "".join(
            f'<tr><td><a href="{e(c["id"])}.html">{e(c["co"])}</a><br><span class="note">{int(c["date"][5:7])}月{int(c["date"][8:])}日・{e(c.get("ind", ""))}・{e(D["causeLabels"].get(c.get("cause", "cyber"), ""))}</span></td><td class="r">{e(c["label"])}</td></tr>'
            for c in sorted(by[k], key=lambda c: c["date"], reverse=True))
        parts.append(f'<section><h2>{int(y)}年{int(m)}月（{len(by[k])}件）</h2><table><thead><tr><th>組織</th><th class="r">件数</th></tr></thead><tbody>{rows}</tbody></table></section>')
    title = "全事案一覧｜国内情報漏えい台帳"
    desc = f"国内の企業・公共機関・大学・病院などの個人情報漏えい事案{len(cases)}件の一覧。すべて組織の公式発表と照合済み。"
    return head(title, desc, url, "website") + f"""<nav class="crumb" aria-label="パンくず"><a href="../">台帳</a><span>›</span><span>全事案一覧</span></nav>
<h1>全事案一覧</h1>
<p class="note">公式発表と照合した{len(cases)}件を、発生・公表の年月ごとに並べています（{e(D.get('updated', ''))} 更新）。絞り込みやグラフは<a href="../">台帳</a>で使えます。</p>
{''.join(parts)}
{FOOT.format(r='../')}
</main></body>
</html>
"""


def main():
    D = json.load(open(os.path.join(ROOT, "data.json"), encoding="utf-8"))
    cases = D["cases"]
    for c in cases:
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]*", c["id"]), c["id"]
    out = os.path.join(ROOT, "case")
    if os.path.isdir(out):
        shutil.rmtree(out)  # 削除・改名された事案の古いページを残さない
    os.makedirs(out)
    for c in cases:
        open(os.path.join(out, c["id"] + ".html"), "w", encoding="utf-8").write(case_page(c, D))
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(index_page(cases, D))
    upd = D.get("updated", "")
    urls = [(SITE + p, upd) for p in STATIC] + [(SITE + "case/", upd)]
    urls += [(f"{SITE}case/{c['id']}.html", c.get("last") or c.get("verified") or c["date"]) for c in cases]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{e(u)}</loc>{f'<lastmod>{d}</lastmod>' if d else ''}</url>" for u, d in urls]
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")
    print(f"case pages: {len(cases)}, sitemap urls: {len(urls)}")


if __name__ == "__main__":
    main()
