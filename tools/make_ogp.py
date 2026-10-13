#!/usr/bin/env python3
"""共有時に表示される画像 ogp.png（1200×630）を作る。件数は data.json から。
Chromium（Playwright）で HTML を画像にする。ロゴや他社の画像は使わず、図形と文字だけで描く。
使い方: python3 tools/make_ogp.py   （台帳の件数が大きく変わったときに実行。毎日は不要）"""
import json, os
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data.json"), encoding="utf-8"))
n = len(D["cases"]); upd = D["updated"].replace("-", ".")
ci = sum(1 for c in D["cases"] if c["st"] == "c")
HTML = f"""<!doctype html><meta charset=utf-8><style>
*{{box-sizing:border-box}}body{{margin:0;width:1200px;height:630px;font-family:"Noto Sans CJK JP","Hiragino Sans",sans-serif;background:#0f151c;color:#e4eaf0;position:relative;overflow:hidden}}
.bg{{position:absolute;inset:0;background:radial-gradient(900px 500px at 85% 20%,#24384a 0,transparent 60%),linear-gradient(135deg,#0f151c,#16202a)}}
.in{{position:absolute;left:72px;top:64px;right:72px;bottom:56px;display:flex;flex-direction:column}}
.k{{font-size:26px;color:#f0954a;font-weight:700;letter-spacing:.08em}}
h1{{font-size:84px;margin:14px 0 0;line-height:1.12;font-weight:900}}
p{{font-size:32px;line-height:1.5;color:#b8c4d0;margin:22px 0 0;max-width:1000px;font-size:30px}}
.st{{margin-top:auto;display:flex;gap:18px}}
.t{{background:#16202a;border:2px solid #2a3744;border-radius:20px;padding:16px 30px}}
.t b{{display:block;font-size:56px;line-height:1.1;font-variant-numeric:tabular-nums}}.t span{{font-size:22px;color:#97a5b3}}
svg{{position:absolute;right:80px;top:300px;width:250px}}
.u{{position:absolute;right:72px;bottom:60px;font-size:22px;color:#97a5b3}}
</style><div class=bg></div>
<svg viewBox="0 0 120 96" fill="none" stroke="#7fa6c9" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="10" width="64" height="76" rx="8" fill="#16202a"/><path d="M20 28h40M20 42h40M20 56h26"/><path d="M84 30l22 8v18c0 16-10 26-22 31-12-5-22-15-22-31V38z" fill="#3a2615" stroke="#f0954a"/><path d="M75 58l7 7 13-14" stroke="#f0954a"/></svg>
<div class=in><div class=k>DATA BREACH LEDGER</div><h1>国内情報漏えい台帳</h1>
<p>公式発表と照合した、国内の情報漏えいの記録</p>
<div class=st><div class=t><b>{n}</b><span>事案を掲載</span></div><div class=t><b>{ci}</b><span>漏えいを確認</span></div></div></div>
<div class=u>{upd} 更新</div>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.set_content(HTML); pg.wait_for_timeout(300)
    pg.screenshot(path=os.path.join(ROOT, "ogp.png")); b.close()
print("ogp.png", n, ci)
