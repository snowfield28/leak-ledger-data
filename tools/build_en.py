#!/usr/bin/env python3
"""index.html（日本語トップ）から en/index.html（英語トップ）を作る。
index.html を作り直したら（build.py）、続けて `python3 tools/build_en.py` を実行する。
事案ごとの文章（概要・調査の状況など）は翻訳せず、公式発表の日本語のまま表示する。"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n_en as EN

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://snowfield28.github.io/leak-ledger-data/"
t = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()


def R(a, b, count=1):
    global t
    assert a in t, "missing: " + a[:70]
    t = t.replace(a, b) if count == 0 else t.replace(a, b, count)


# ---- head ----
i = t.index("<title>"); j = t.index("</head>")
head = f'''<title>Japan Data Breach Ledger | Personal data leak incidents in Japan</title>
<meta name="description" content="A ledger of personal data breaches at Japanese companies, public bodies, universities and hospitals, checked against each organization's official announcement. Updated daily.">
<meta property="og:title" content="Japan Data Breach Ledger">
<meta property="og:description" content="Personal data breach incidents in Japan, checked against official announcements. Updated daily.">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}en/">
<link rel="canonical" href="{SITE}en/">
<link rel="alternate" hreflang="ja" href="{SITE}">
<link rel="alternate" hreflang="en" href="{SITE}en/">
<link rel="alternate" hreflang="x-default" href="{SITE}">
'''
# keep charset/viewport + style block between head start and title
pre = t[:i]; post = t[j:]
t = pre + head + post[0:0] + t[i:][t[i:].index("<style"):] if False else pre + head + t[t.index("<style"):]
R('<html lang="ja">', '<html lang="en">')

# ---- static text ----
pairs = [
 ('<h1>国内情報漏えい台帳</h1>', '<h1>Japan Data Breach Ledger</h1>'),
 ('流出件数の大きい事案 <small>可能性を含む・対数目盛</small>', 'Largest incidents by records <small>incl. possible leaks · log scale</small>'),
 ('<span style="left:0">1万</span><span style="left:28.57%">10万</span><span style="left:57.14%">100万</span><span style="left:85.71%">1,000万</span>',
  '<span style="left:0">10K</span><span style="left:28.57%">100K</span><span style="left:57.14%">1M</span><span style="left:85.71%">10M</span>'),
 ('原因別の事案数 <small>タップで絞り込み</small>', 'Incidents by cause <small>tap to filter</small>'),
 ('誰の情報が流出したか <small>タップで絞り込み・1事案に複数あり</small>', 'Whose data was exposed <small>tap to filter · an incident can have several</small>'),
 ('公式発表に書かれた対象者で分類しています。取引先の担当者の氏名や連絡先も、法律上は個人情報です。', 'Classified by the affected people named in the official announcement. Names and contact details of business contacts also count as personal information under Japanese law.'),
 ('業種別の事案数 <small>タップで絞り込み</small>', 'Incidents by industry <small>tap to filter</small>'),
 ('流出した情報 <small>タップで絞り込み</small>', 'Data exposed <small>tap to filter</small>'),
 ('傾向の分析 <small>下の絞り込みと連動</small>', 'Trends <small>follows the filters below</small>'),
 ('件数は各組織の公表値で、人数と件数が混在します。件数が未公表の事案は、合計・中央値・規模の集計から外しています。事案数は公式発表と照合できたものだけを数えています。',
  'Record counts are the figures each organization published; people and records may be mixed. Incidents without a published count are left out of totals, medians and size breakdowns. Only incidents matched to an official announcement are counted.'),
 ('placeholder="企業名・キーワードで検索" aria-label="企業名・キーワードで検索"', 'placeholder="Search by organization or keyword" aria-label="Search by organization or keyword"'),
 ('aria-label="原因"', 'aria-label="Cause"'),
 ('<option value="">すべての原因</option>', '<option value="">All causes</option>'),
 ('<optgroup label="サイバー攻撃"><option value="c:cyber">サイバー攻撃（すべて）</option><option value="t:ランサムウェア">ランサムウェア</option><option value="t:不正アクセス">不正アクセス</option><option value="t:委託先経由">委託先経由</option></optgroup>',
  '<optgroup label="Cyber attack"><option value="c:cyber">Cyber attack (all)</option><option value="t:Ransomware">Ransomware</option><option value="t:Unauthorized access">Unauthorized access</option><option value="t:Via contractor">Via contractor</option></optgroup>'),
 ('<option value="c:loss">紛失・盗難</option><option value="c:mis">誤送信・誤掲載</option><option value="c:insider">内部不正</option><option value="c:config">設定ミス・不具合</option>',
  '<option value="c:loss">Loss / theft</option><option value="c:mis">Misdelivery / mis-posting</option><option value="c:insider">Insider misconduct</option><option value="c:config">Misconfiguration / bug</option>'),
 ('aria-label="誰の情報"><option value="">誰の情報：すべて</option>', 'aria-label="Whose data"><option value="">Whose data: all</option>'),
 ('aria-label="業種"><option value="">すべての業種</option>', 'aria-label="Industry"><option value="">All industries</option>'),
 ('aria-label="期間"', 'aria-label="Period"'),
 ('<option value="">すべての期間</option><option value="7">直近1週間</option><option value="30">直近1か月</option><option value="91">直近3か月</option><option value="730" selected>直近24か月</option>',
  '<option value="">All time</option><option value="7">Last 7 days</option><option value="30">Last 30 days</option><option value="91">Last 3 months</option><option value="730" selected>Last 24 months</option>'),
 ('<option value="y2026">2026年</option><option value="y2025">2025年</option><option value="pre2025">2024年以前</option><option value="custom">期間を指定…</option>',
  '<option value="y2026">2026</option><option value="y2025">2025</option><option value="pre2025">2024 and earlier</option><option value="custom">Custom range…</option>'),
 ('aria-label="開始日"', 'aria-label="From"'), ('<span>〜</span>', '<span>–</span>'), ('aria-label="終了日"', 'aria-label="To"'),
 ('>絞り込みを解除<', '>Clear filters<'),
 ('aria-label="事案の一覧"', 'aria-label="Incident list"'),
 ('<th>企業・日付</th><th class="w">原因</th><th class="w">誰の情報</th><th class="w">流出した情報</th><th class="r">件数</th><th class="r">状況</th>',
  '<th>Organization · date</th><th class="w">Cause</th><th class="w">Whose data</th><th class="w">Data exposed</th><th class="r">Records</th><th class="r">Status</th>'),
 ('網羅的に収録しているのは2025年10月以降の事案です（それより前は一部のみ）。期間は、発生日か最新の続報の日付で判定します。業種は企業の主な事業をもとにした台帳独自の分類です。件数は企業の公表値で、人数と件数が混在し、重複を含む場合があります。「調査完了」は調査結果や最終報が公表された事案です。流出した情報で複数選ぶと、すべてを含む事案に絞り込みます。分類は出典に書かれた項目だけを元にしています。',
  'Coverage is comprehensive from October 2025 onward; earlier incidents are only partly included. The period filter uses the incident date or the date of the latest update. Industries are this ledger\'s own classification based on each organization\'s main business. Counts are the organizations\' published figures; people and records may be mixed and duplicates may be included. "Closed" means the investigation result or a final report has been published. Selecting several data types narrows to incidents that include all of them. Classification relies only on items stated in the sources. Incident descriptions are shown in Japanese, as written in the official announcements.'),
 # js
 ('.toLocaleString("ja-JP")+"億"', '.toLocaleString("en-US")+"B"'),
 ('const short=co=>co.split("（")[0].split("／")[0];', 'const short=co=>co.split("（")[0].split("／")[0];\nconst LAB=d=>d.n?fmt(d.n)+" records":"Not disclosed";'),
]
for a, b in pairs:
    R(a, b)

# fmt: replace entire definition
k = t.index("const fmt=n=>"); l = t.index("\n", k)
t = t[:k] + 'const fmt=n=>n==null?"—":n>=1e9?(Math.round(n/1e8)/10).toLocaleString("en-US")+"B":n>=1e6?(Math.round(n/1e5)/10).toLocaleString("en-US")+"M":n>=1e3?(Math.round(n/1e2)/10).toLocaleString("en-US")+"K":n.toLocaleString("en-US");' + t[l:]

more = [
 ('tg("st","c","漏えい確認")+tg("st","p","漏えいの可能性")', 'tg("st","c","Leak confirmed")+tg("st","p","Possible leak")'),
 ('tg("res","ongoing","調査中")+tg("res","closed","調査完了")', 'tg("res","ongoing","Ongoing")+tg("res","closed","Closed")'),
 ('chip("新しい順",S.sort==="date","sort:date")+chip("件数順",S.sort==="size","sort:size")', 'chip("Newest first",S.sort==="date","sort:date")+chip("Most records",S.sort==="size","sort:size")'),
 ('[["ind","業種別の比較"],["mat","業種×原因"],["month","月別の推移"],["size","件数の規模"]]', '[["ind","By industry"],["mat","Industry × cause"],["month","By month"],["size","Size of incidents"]]'),
 ("'<div class=\"empty\">該当する事案はありません</div>'", "'<div class=\"empty\">No matching incidents</div>'"),
 ('<th>業種</th>${H("c","事案数")}${H("n","流出件数の合計")}${H("med","1件あたり中央値")}<th class="w2">最大の事案</th><th class="r w2">漏えい確認</th><th class="r w2">サイバー攻撃</th>',
  '<th>Industry</th>${H("c","Incidents")}${H("n","Total records")}${H("med","Median")}<th class="w2">Largest incident</th><th class="r w2">Confirmed</th><th class="r w2">Cyber</th>'),
 ('見出しをタップで並べ替え、業種をタップでその業種に絞り込みます。中央値は件数が公表された事案だけで計算しています。', 'Tap a heading to sort, or an industry to filter. Medians use only incidents with a published count.'),
 ('<th>業種</th>${cs.map', '<th>Industry</th>${cs.map'),
 ('<th class="r">計</th>', '<th class="r">Total</th>'),
 ('色が濃いほど事案が多い組み合わせです。', 'Darker cells mean more incidents.'),
 ('aria-label="月別の事案数"', 'aria-label="Incidents per month"'),
 ('title="${k}：${v.c}件／流出件数${fmt(v.n)}"', 'title="${k}: ${v.c} incidents / ${fmt(v.n)} records"'),
 ('${Number(k.slice(5))}月', '${["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][Number(k.slice(5))]}'),
 ('事案の日付（発生・検知または初回公表）の月で数えています。2025年10月より前は一部のみの収録のため、少なく見えます。', 'Counted by the month of the incident date (occurrence, detection or first announcement). Months before October 2025 look low because only some incidents are included.'),
 ('[["〜1千",0,1e3],["1千〜1万",1e3,1e4],["1万〜10万",1e4,1e5],["10万〜100万",1e5,1e6],["100万〜",1e6,Infinity]]', '[["<1K",0,1e3],["1K–10K",1e3,1e4],["10K–100K",1e4,1e5],["100K–1M",1e5,1e6],["1M+",1e6,Infinity]]'),
 ('border:1px dashed var(--line)"></i>未公表</span>', 'border:1px dashed var(--line)"></i>Not disclosed</span>'),
 ('title="未公表：${u}件"', 'title="Not disclosed: ${u}"'),
 ('title="${B[i][0]}：${c}件"', 'title="${B[i][0]}: ${c}"'),
 ('業種ごとに、1事案あたりの流出件数の規模で事案を色分けしています。', 'Incidents in each industry are colored by the number of records per incident.'),
 ('<span>事案</span>', '<span>Incidents</span>'), ('<span>流出件数の合計</span>', '<span>Total records</span>'), ('<span>調査中・続報待ち</span>', '<span>Ongoing / awaiting updates</span>'),
 ("'<div class=\"empty\">件数が公表された事案はありません</div>'", "'<div class=\"empty\">No incidents with a published count</div>'"),
 ('aria-label="${esc(d.co)} ${esc(d.label)}"', 'aria-label="${esc(d.co)} ${LAB(d)}"'),
 ('`${rows.length} / ${DB.cases.length} 件を表示`', '`Showing ${rows.length} of ${DB.cases.length} incidents`'),
 ('<span class="m-only">・${', '<span class="m-only"> · ${'),
 ('>${md(d.date)}・${esc(d.ind||"")}', '>${md(d.date)} · ${esc(d.ind||"")}'),
 ("d.types.join(\"・\")", "d.types.join(\" · \")"),
 ("'<span class=\"cd\">要確認</span>'", "'<span class=\"cd\">Unverified</span>'"),
 ('${d.n?fmt(d.n):"調査中"}', '${d.n?fmt(d.n):"Not disclosed"}'),
 ('${d.st==="c"?"漏えい確認":"可能性"}</span><span class="pill ${esc(d.status)}">${d.status==="closed"?"調査完了":"調査中"}</span>${d.auto?\'<span class="pill auto">未確認</span>\':""}',
  '${d.st==="c"?"Confirmed":"Possible"}</span><span class="pill ${esc(d.status)}">${d.status==="closed"?"Closed":"Ongoing"}</span>${d.auto?\'<span class="pill auto">Unverified</span>\':""}'),
 ('colspan="6" class="empty">条件に合う事案はありません', 'colspan="6" class="empty">No incidents match these filters'),
 ('<span>電話</span>', '<span>Phone</span>'), ('<span>メール</span>', '<span>Email</span>'), ('<span>フォーム ↗</span>', '<span>Form ↗</span>'),
 ('esc(k.note||"公式発表に窓口の記載なし")', 'esc(k.note||"No contact point stated in the official announcement")'),
 ('出典：<a href="${esc(src)}" target="_blank" rel="noopener">公式発表</a>に記載の窓口', 'Source: contact point stated in the <a href="${esc(src)}" target="_blank" rel="noopener">official announcement</a>'),
 ('<span class="vh">${on?"含む":"記載なし"}</span>', '<span class="vh">${on?"included":"not stated"}</span>'),
 ('aria-label="閉じる"', 'aria-label="Close"'),
 ('${d.st==="c"?"漏えい確認":"漏えいの可能性"}</span>', '${d.st==="c"?"Leak confirmed":"Possible leak"}</span>'),
 ('自動追加・未確認', 'Auto-added · unverified'),
 ('<dt>件数</dt><dd><b>${esc(d.label)}</b></dd>', '<dt>Records</dt><dd><b>${LAB(d)}</b></dd>'),
 ('<dt>最終確認日</dt><dd>${md(d.verified)}（公式発表と照合）</dd>', '<dt>Last verified</dt><dd>${md(d.verified)} (checked against the official announcement)</dd>'),
 ('<dt>日付</dt><dd>${md(d.date)}（発生・検知または初回公表）</dd>', '<dt>Date</dt><dd>${md(d.date)} (occurrence, detection or first announcement)</dd>'),
 ('<dt>業種</dt>', '<dt>Industry</dt>'), ('<dt>原因</dt>', '<dt>Cause</dt>'), ('<dt>誰の情報</dt>', '<dt>Whose data</dt>'),
 ('"（"+d.types.join("・")+"）"', '" ("+d.types.join(" · ")+")"'),
 ('.join("、")||"—"', '.join(", ")||"—"'),
 ('<dt>犯行声明</dt><dd>${esc(d.claim)}</dd>', '<dt>Claim of responsibility (Japanese)</dt><dd lang="ja">${esc(d.claim)}</dd>'),
 ('<h4>流出した情報</h4>', '<h4>Data exposed</h4>'),
 ('<b>含まれない：</b>${esc(d.notIncl)}', '<b>Not included (Japanese):</b> <span lang="ja">${esc(d.notIncl)}</span>'),
 ('<h4>概要</h4><p class="txt">', '<h4>Summary (in Japanese, from the official release)</h4><p class="txt" lang="ja">'),
 ('<h4>調査の状況</h4><p class="txt">', '<h4>Investigation status (Japanese)</h4><p class="txt" lang="ja">'),
 ('<h4>会社の対応</h4>', '<h4>Organization\'s response (Japanese)</h4>'),
 ('<ul class="resp">', '<ul class="resp" lang="ja">'),
 ("'<p class=\"note\">未確認</p>'", "'<p class=\"note\">Unverified</p>'"),
 ('<h4>お問い合わせ先</h4>', '<h4>Contact points</h4>'),
 ('<h4>一次情報（公式発表）</h4>', '<h4>Official announcement</h4>'),
 ('<h4>報道</h4>', '<h4>Press coverage</h4>'),
 ('</svg>この事案を共有', '</svg>Share this incident'),
 ('`【${d.co}】${d.label}（${d.st==="c"?"漏えい確認":"漏えいの可能性"}・${SL[d.status]||""}）\\n${d.sum}`+(d.official&&d.official[0]?`\\n公式発表：${d.official[0][1]}`:"")+`\\n${PAGE}case/${id}.html`',
  '`${d.co} — ${LAB(d)} (${d.st==="c"?"leak confirmed":"possible leak"}, ${SL[d.status]||""})`+(d.official&&d.official[0]?`\\nOfficial announcement: ${d.official[0][1]}`:"")+`\\n${PAGE}en/case/${id}.html`'),
 ('title:d.co+"の情報漏えい",text', 'title:d.co+" data breach",text'),
 ('toast("共有用の文章とリンクをコピーしました"),()=>toast("コピーできませんでした"));else toast("コピーできませんでした")', 'toast("Copied text and link"),()=>toast("Could not copy"));else toast("Could not copy")'),
 ('<option value="">誰の情報：すべて</option>\'+Object', '<option value="">Whose data: all</option>\'+Object'),
 ('<option value="">すべての業種</option>\'+(DB', '<option value="">All industries</option>\'+(DB'),
 ('DB.updated+" 更新"', '"Updated "+DB.updated'),
 ('`掲載しているのは、報道や一覧で見つけた事案のうち、組織自身の公式発表を開いて内容が一致したものだけです。公式発表と照合できていない候補が${DB.pendingCount||0}件あり、毎日の更新で再確認しています。`',
  '`Only incidents whose official announcement was opened and matched are listed. ${DB.pendingCount||0} further candidates could not yet be matched to an official announcement and are re-checked in each daily update.`'),
 ('データを読み込めませんでした。時間をおいて再読み込みしてください。', 'Could not load the data. Please try again later.'),
 ('fetch("data.json?t="', 'fetch("../data.json?t="'),
 ('DB=await r.json();', 'DB=toEN(await r.json());'),
 ('const PAGE="https://snowfield28.github.io/leak-ledger-data/";', 'const PAGE="https://snowfield28.github.io/leak-ledger-data/";\nconst ENM=%s;\nfunction toEN(D){const m=(o,k)=>(o&&(ENM[k]))?o:o;\n  const tr=(k,v)=>(ENM[k]||{})[v]||v;\n  D.industries=(D.industries||[]).map(v=>tr("IND",v));\n  for(const [n,k] of [["itemLabels","ITEM"],["statusLabels","STATUS"],["causeLabels","CAUSE"],["whoLabels","WHO"]]){if(D[n])for(const key of Object.keys(D[n]))D[n][key]=tr(k,key)==key?D[n][key]:tr(k,key)}\n  D.cases.forEach(d=>{d.ind=tr("IND",d.ind);d.types=(d.types||[]).map(v=>tr("TYPE",v))});\n  return D}' % json.dumps({"IND": EN.IND, "TYPE": EN.TYPE, "CAUSE": EN.CAUSE, "ITEM": EN.ITEM, "WHO": EN.WHO, "STATUS": EN.STATUS}, ensure_ascii=False)),
]
for a, b in more:
    R(a, b)

t=t.replace('<div class="empty">該当する事案はありません</div>','<div class="empty">No matching incidents</div>').replace('<p class="note">未確認</p>','<p class="note">Unverified</p>')
# bars: "N件" -> plain/aria
t = re.sub(r'(<span class="bval">\$\{[^}]*\})件', r'\1', t)
t = t.replace('}件"', '} incidents"').replace('}件<', '}<').replace('${c}件', '${c}')
# footer nav
t = re.sub(r'<nav class="foot" aria-label="サイト情報".*?</nav>',
  '<nav class="foot" aria-label="Site information" style="display:flex;flex-wrap:wrap;gap:6px 16px"><a href="case/">All incidents</a><a href="about.html">About</a><a href="privacy.html">Privacy policy</a><a href="contact.html">Contact / corrections</a><a href="../" hreflang="ja" lang="ja">日本語</a></nav>', t, flags=re.S)

os.makedirs(os.path.join(ROOT, "en"), exist_ok=True)
open(os.path.join(ROOT, "en", "index.html"), "w", encoding="utf-8").write(t)
left = sorted(set(re.findall(r'[぀-ヿ一-鿿]+', t)))
print("written en/index.html; leftover Japanese:", left)
