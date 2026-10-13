#!/usr/bin/env python3
"""新着の漏えい報道を集め、公式発表の本文まで取得して inbox.json に出す（GitHub Actions で毎日実行）。

流れ:
  1. tools/sources.json の一覧ページから、キーワードに合う記事リンクを集める
  2. 台帳（data/candidates/excluded）の src・official と inbox_seen.json にない記事だけを「新着」とする
  3. 新着記事の本文を取り、記事から公式発表らしい外部リンク（組織サイト・PDFなど）をたどって本文を取得
     - robots.txt で拒否されたもの・本文が極端に短いもの（画像／JavaScript描画）は status で区別して記録
  4. manual/ に置かれた貼り付け（URLや本文）も同じ形で inbox に取り込む
  5. 結果を inbox.json と inbox/texts/*.txt に保存

判断（台帳に載せるか、既存と同じ事案か）はここでは行わない。定期実行のClaudeが inbox を読んで行う。

使い方:
  python3 tools/collect.py            # 通常実行
  python3 tools/collect.py --max-new 10
"""
import argparse
import hashlib
import io
import json
import re
import time
import urllib.robotparser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
TEXT_DIR = ROOT / "inbox" / "texts"
UA = "leak-ledger-bot/1.0 (+https://github.com/snowfield28/leak-ledger-data)"
KEYWORDS = re.compile(r"漏えい|漏洩|流出|不正アクセス|ランサム|紛失|盗難|誤送信|誤送付|誤掲載|持ち出し|個人情報|サイバー攻撃|フィッシング|サポート詐欺")
# 公式発表とはみなさない外部ドメイン（報道・SNS・検索・まとめ）
NON_OFFICIAL = re.compile(
    r"(bit\.ly|goo\.gl|ow\.ly|tinyurl\.com|amzn\.to|iid\.co\.jp|rocket-boys\.co\.jp|netsecurity\.ne\.jp|impress\.co\.jp|itmedia\.co\.jp|nhk\.(or\.jp|jp)|news\.web\.nhk|yahoo\.co\.jp|"
    r"x\.com|twitter\.com|facebook\.com|instagram\.com|youtube\.com|youtu\.be|line\.me|t\.co|google\.[a-z.]+|"
    r"hatenablog|hatenadiary|note\.com|smartscope\.blog|nikkei\.com/article|asahi\.com|mainichi\.jp|yomiuri\.co\.jp|"
    r"sankei\.com|kyodo|jiji\.com|cnet\.com|ascii\.jp|gigazine|amazon\.co\.jp|wikipedia\.org|piyolog)",
    re.I,
)
OFFICIAL_HINT = re.compile(r"公式|お知らせ|おしらせ|発表|プレス|リリース|お詫び|お詫|報告|news|release|notice|\.pdf|ir\.|info", re.I)
MAX_TEXT = 20000
MIN_OK_CHARS = 200
MAX_OFFICIAL_PER_ARTICLE = 5

_session = requests.Session()
_session.headers["User-Agent"] = UA
_robots = {}
_last_hit = {}


def now_jst():
    return datetime.now(timezone.utc) + timedelta(hours=9)


def robots_ok(url):
    p = urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    rp = _robots.get(base)
    if rp is None:
        rp = urllib.robotparser.RobotFileParser()
        try:
            r = _session.get(base + "/robots.txt", timeout=15)
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
            else:
                rp.parse([])  # robots.txt が無ければ許可
        except requests.RequestException:
            rp.parse([])
        _robots[base] = rp
    return rp.can_fetch(UA, url)


def polite_get(url, timeout=25):
    host = urlparse(url).netloc
    wait = 1.0 - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.time()
    return _session.get(url, timeout=timeout)


def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        t.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"[ \t　]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def pdf_text(content):
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(content))
    return "\n".join((p.extract_text() or "") for p in reader.pages[:30]).strip()


def fetch_text(url):
    """(status, text, final_url)。status: ok / thin / robots / error:<理由>"""
    if not robots_ok(url):
        return "robots", "", url
    try:
        r = polite_get(url)
    except requests.RequestException as e:
        return f"error:{type(e).__name__}", "", url
    if r.status_code != 200:
        return f"error:http{r.status_code}", "", url
    ctype = r.headers.get("content-type", "").lower()
    try:
        if "pdf" in ctype or url.lower().split("?")[0].endswith(".pdf"):
            text = pdf_text(r.content)
        elif "html" in ctype or "text" in ctype:
            r.encoding = r.apparent_encoding if not r.encoding or r.encoding.lower() == "iso-8859-1" else r.encoding
            text = clean_text(r.text)
        elif ctype.startswith("image/"):
            return "image", "", r.url
        else:
            return f"error:ctype", "", r.url
    except Exception as e:  # PDF破損など
        return f"error:{type(e).__name__}", "", r.url
    return ("ok" if len(text) >= MIN_OK_CHARS else "thin"), text, r.url


def list_links(html, base_url):
    """一覧ページから (title, url) を返す。キーワードに合うものだけ。"""
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        title = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
        if len(title) < 8 or not KEYWORDS.search(title):
            continue
        url = urldefrag(urljoin(base_url, a["href"]))[0]
        if url in seen or not url.startswith("http"):
            continue
        seen.add(url)
        out.append((title, url))
    return out


def official_links(html, base_url, article_host):
    """記事本文から、公式発表らしい外部リンクを優先順に返す。"""
    soup = BeautifulSoup(html, "html.parser")
    scored, seen = [], set()
    for a in soup.find_all("a", href=True):
        url = urldefrag(urljoin(base_url, a["href"]))[0]
        if not url.startswith("http") or url in seen:
            continue
        host = urlparse(url).netloc
        if host == article_host or NON_OFFICIAL.search(url):
            continue
        seen.add(url)
        text = a.get_text(" ", strip=True)
        score = 2 if url.lower().split("?")[0].endswith(".pdf") else 0
        if OFFICIAL_HINT.search(text) or OFFICIAL_HINT.search(url):
            score += 1
        scored.append((-score, len(scored), url))
    scored.sort()
    return [u for _, _, u in scored[:MAX_OFFICIAL_PER_ARTICLE]]


def save_text(url, text):
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    name = hashlib.sha1(url.encode()).hexdigest()[:12] + ".txt"
    (TEXT_DIR / name).write_text(f"URL: {url}\n\n{text[:MAX_TEXT]}", encoding="utf-8")
    return f"inbox/texts/{name}"


def known_urls():
    urls = set()
    for f in ("data.json", "candidates.json"):
        for c in json.loads((ROOT / f).read_text(encoding="utf-8"))["cases"]:
            for k in ("src", "official"):
                for pair in c.get(k, []) or []:
                    if isinstance(pair, list) and len(pair) > 1:
                        urls.add(pair[1].rstrip("/"))
    for c in json.loads((ROOT / "excluded.json").read_text(encoding="utf-8"))["cases"]:
        urls.update(u.rstrip("/") for u in c.get("official", []))
    return urls


def source_urls(src):
    """{yyyy}/{mm} を当月と前月に展開する。"""
    n = now_jst()
    prev = (n.replace(day=1) - timedelta(days=1))
    if "{yyyy}" not in src["url"]:
        return [src["url"]]
    return [src["url"].format(yyyy=d.year, mm=f"{d.month:02d}") for d in (n, prev)]


def load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def ingest_manual(items, today):
    """manual/*.md|txt を inbox に取り込み、manual/done/ へ移す。
    書式: 先頭に `URL: https://...` `TITLE: ...`（任意）、空行のあとに公式発表の本文を貼る。"""
    mdir = ROOT / "manual"
    if not mdir.exists():
        return 0
    n = 0
    for f in sorted(list(mdir.glob("*.md")) + list(mdir.glob("*.txt"))):
        if f.name.lower() == "readme.md":
            continue
        raw = f.read_text(encoding="utf-8")
        head, _, body = raw.partition("\n\n")
        meta = dict(re.findall(r"^(URL|TITLE):\s*(.+)$", head, re.M))
        if not meta:  # 見出し行がなければ全体を本文とみなす
            body = raw
        url = meta.get("URL") or f"manual:{f.name}"
        official = [{"url": url, "status": "manual", "chars": len(body), "text_file": save_text(url, body)}]
        items.append({"article_url": url, "title": meta.get("TITLE", f.stem), "source": "manual", "found": today,
                      "article_text_file": None, "official": official})
        (mdir / "done").mkdir(exist_ok=True)
        f.rename(mdir / "done" / f.name)
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-new", type=int, default=40)
    args = ap.parse_args()

    today = now_jst().strftime("%Y-%m-%d")
    sources = json.loads((ROOT / "tools" / "sources.json").read_text(encoding="utf-8"))["sources"]
    inbox = load_json(ROOT / "inbox.json", {"items": []})
    seen_data = load_json(ROOT / "inbox_seen.json", {"urls": []})
    seen = set(seen_data["urls"])
    known = known_urls()
    queued = {i["article_url"] for i in inbox["items"]}

    candidates = []  # (source_name, title, url)
    report = {"sources_ok": 0, "sources_failed": []}
    for src in sources:
        for url in source_urls(src):
            if not robots_ok(url):
                report["sources_failed"].append(f"{src['name']}: robots拒否 {url}")
                continue
            try:
                r = polite_get(url)
                r.raise_for_status()
                r.encoding = r.apparent_encoding if not r.encoding or r.encoding.lower() == "iso-8859-1" else r.encoding
            except requests.RequestException as e:
                code = getattr(getattr(e, "response", None), "status_code", "")
                report["sources_failed"].append(f"{src['name']}: {type(e).__name__} {code} {url}")
                continue
            report["sources_ok"] += 1
            for title, link in list_links(r.text, url):
                candidates.append((src["name"], title, link))

    new = []
    for name, title, link in candidates:
        key = link.rstrip("/")
        if key in known or link in seen or link in queued or any(link == n[2] for n in new):
            continue
        new.append((name, title, link))
    print(f"一覧から {len(candidates)} 件、うち新着 {len(new)} 件（上限 {args.max_new}）")

    for name, title, link in new[: args.max_new]:
        item = {"article_url": link, "title": title, "source": name, "found": today, "article_text_file": None, "official": []}
        try:
            if robots_ok(link):
                r = polite_get(link)
                r.encoding = r.apparent_encoding if not r.encoding or r.encoding.lower() == "iso-8859-1" else r.encoding
                if r.status_code == 200:
                    item["article_text_file"] = save_text(link, clean_text(r.text))
                    for ou in official_links(r.text, link, urlparse(link).netloc):
                        st, text, final = fetch_text(ou)
                        rec = {"url": ou, "status": st, "chars": len(text)}
                        if final != ou:
                            rec["final_url"] = final
                        if text:
                            rec["text_file"] = save_text(ou, text)
                        item["official"].append(rec)
            else:
                item["article_error"] = "robots"
        except requests.RequestException as e:
            item["article_error"] = type(e).__name__
        inbox["items"].append(item)
        seen.add(link)

    # 取りこぼし防止: 上限で切った分は seen に入れず次回に回す
    manual_n = ingest_manual(inbox["items"], today)

    inbox["generated"] = now_jst().strftime("%Y-%m-%d %H:%M JST")
    inbox["last_report"] = report
    (ROOT / "inbox.json").write_text(json.dumps(inbox, ensure_ascii=False, indent=1), encoding="utf-8")
    seen_data["urls"] = sorted(seen)[-5000:]
    (ROOT / "inbox_seen.json").write_text(json.dumps(seen_data, ensure_ascii=False, indent=1), encoding="utf-8")

    # inbox から参照されなくなった本文を削除
    used = set()
    for i in inbox["items"]:
        if i.get("article_text_file"):
            used.add(i["article_text_file"])
        used.update(o["text_file"] for o in i["official"] if o.get("text_file"))
    if TEXT_DIR.exists():
        for f in TEXT_DIR.glob("*.txt"):
            if f"inbox/texts/{f.name}" not in used:
                f.unlink()

    print(f"inbox: {len(inbox['items'])} 件（うち今回の貼り付け取り込み {manual_n} 件）。取得失敗の一覧ページ: {len(report['sources_failed'])}")
    for s in report["sources_failed"]:
        print("  失敗:", s)


if __name__ == "__main__":
    main()
