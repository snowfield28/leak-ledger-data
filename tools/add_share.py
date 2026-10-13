#!/usr/bin/env python3
"""全HTMLに共有ボタン（X・LINE・Facebook・はてブ・リンクをコピー・端末の共有）を足す。入っていれば何もしない。
外部の共有スクリプトは読み込まず、各サービスの共有URLへのリンクだけにする（読み込み時に第三者へ通信しない）。
事案ページは見出しの下、トップと他のページは末尾に置く。build_pages.py の最後に呼ばれる。"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = 'id="share-js" data-v="1"'
TAG = r"""<style id="share-css" data-v="1">
.share{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:8px 0 14px;font-size:13px}
.share.end{justify-content:center;margin:20px 0 0}
.share .lb{color:var(--muted);margin-right:2px}
.share a,.share button{font:inherit;font-size:12.5px;line-height:1;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:99px;padding:7px 12px;text-decoration:none;cursor:pointer;white-space:nowrap}
.share a:hover,.share button:hover{border-color:var(--accent);color:var(--accent)}
.share a:focus-visible,.share button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
</style>
<script id="share-js" data-v="1">
document.addEventListener("DOMContentLoaded",function(){
  var d=document,en=(d.documentElement.lang||"ja").indexOf("en")===0;
  var m=d.querySelector('meta[property="og:url"]'),u=encodeURIComponent((m&&m.content)||location.href.split("#")[0]);
  var raw=decodeURIComponent(u),t=encodeURIComponent(d.title);
  var S=en?[["X","https://twitter.com/intent/tweet?url="+u+"&text="+t],["Facebook","https://www.facebook.com/sharer/sharer.php?u="+u]]
          :[["X","https://twitter.com/intent/tweet?url="+u+"&text="+t],["LINE","https://social-plugins.line.me/lineit/share?url="+u],["Facebook","https://www.facebook.com/sharer/sharer.php?u="+u],["はてブ","https://b.hatena.ne.jp/add?mode=confirm&url="+u+"&title="+t]];
  var box=d.createElement("div");box.className="share";box.setAttribute("role","group");box.setAttribute("aria-label",en?"Share":"共有");
  var lb=d.createElement("span");lb.className="lb";lb.textContent=en?"Share:":"共有:";box.appendChild(lb);
  S.forEach(function(s){var a=d.createElement("a");a.href=s[1];a.target="_blank";a.rel="noopener noreferrer";a.textContent=s[0];a.setAttribute("aria-label",s[0]+(en?" (opens in a new tab)":"で共有（新しいタブで開く）"));box.appendChild(a)});
  var c=d.createElement("button");c.type="button";c.textContent=en?"Copy link":"リンクをコピー";
  c.addEventListener("click",function(){
    function ok(){c.textContent=en?"Copied":"コピーしました";setTimeout(function(){c.textContent=en?"Copy link":"リンクをコピー"},1800)}
    function fb(){var i=d.createElement("input");i.value=raw;d.body.appendChild(i);i.select();try{d.execCommand("copy");ok()}catch(e){}d.body.removeChild(i)}
    if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(raw).then(ok,fb)}else{fb()}
  });
  box.appendChild(c);
  if(navigator.share){var n=d.createElement("button");n.type="button";n.textContent=en?"Share…":"その他…";
    n.addEventListener("click",function(){navigator.share({title:d.title,url:raw}).catch(function(){})});box.appendChild(n)}
  var h=d.querySelector("main h1")||d.querySelector("body > h1");
  var isCase=/\/case\/(?!index\.html)[^\/]+\.html$/.test(location.pathname)&&h;
  if(isCase){h.parentNode.insertBefore(box,h.nextSibling)}
  else{box.className+=" end";(d.querySelector("main")||d.body).appendChild(box)}
});
</script>
"""


def run():
    n = 0
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in (".git", "backfill", "tools", "node_modules")]
        for f in fn:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            s = open(p, encoding="utf-8").read()
            if MARK in s or "</head>" not in s:
                continue
            open(p, "w", encoding="utf-8").write(s.replace("</head>", TAG + "</head>", 1))
            n += 1
    return n


if __name__ == "__main__":
    print("share buttons added to", run(), "files")
