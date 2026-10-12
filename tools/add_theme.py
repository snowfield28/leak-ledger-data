#!/usr/bin/env python3
"""全HTMLに、ライト／ダーク／端末に合わせる の切り替えボタンを足す（入っていれば何もしない）。
build_pages.py の最後に呼ばれる。選んだ設定はブラウザの localStorage に保存する（使えなければ保存せず動く）。"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = 'data-v="3"'
TAG = r"""<style id="theme-css" data-v="3">
.theme-bar{display:flex;justify-content:flex-end;margin:0 0 6px}
.top-tools{display:flex;align-items:center;gap:6px}
.lang-link{font:inherit;font-size:12.5px;line-height:1;color:var(--muted);background:var(--surface);border:1px solid var(--line);border-radius:99px;padding:7px 12px;text-decoration:none;white-space:nowrap}
.lang-link:hover{color:var(--ink)}
.lang-link:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.theme-wrap{position:relative;display:inline-block}
.theme-btn{font:inherit;font-size:12.5px;line-height:1;color:var(--muted);background:var(--surface);border:1px solid var(--line);border-radius:99px;padding:7px 12px;cursor:pointer;white-space:nowrap}
.theme-btn:hover{color:var(--ink)}
.theme-btn:focus-visible,.theme-menu button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.theme-menu{position:absolute;right:0;top:calc(100% + 6px);z-index:30;min-width:140px;margin:0;padding:4px;list-style:none;background:var(--surface);color:var(--ink);border:1px solid var(--line);border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.18)}
.theme-menu[hidden]{display:none}
.theme-menu button{display:flex;align-items:center;gap:8px;width:100%;font:inherit;font-size:13.5px;text-align:left;color:inherit;background:none;border:0;border-radius:8px;padding:9px 10px;cursor:pointer}
.theme-menu button:hover{background:var(--accent-soft,rgba(128,128,128,.15))}
.theme-menu button[aria-checked="true"]{font-weight:700}
.theme-menu .ck{margin-left:auto;visibility:hidden}
.theme-menu button[aria-checked="true"] .ck{visibility:visible}
</style>
<script id="theme-js" data-v="3">
(function(){
  var ALT="@@ALT@@",d=document.documentElement,en=(d.lang||"ja").indexOf("en")===0;
  var L=en?{system:"Auto (match device)",light:"Light",dark:"Dark",short:{system:"Auto",light:"Light",dark:"Dark"},aria:"Color theme"}
          :{system:"自動（端末に合わせる）",light:"ライト",dark:"ダーク",short:{system:"自動",light:"ライト",dark:"ダーク"},aria:"表示モード"};
  var I={system:"◐",light:"☀",dark:"☾"},ORDER=["system","light","dark"];
  function get(){try{var t=localStorage.getItem("theme");return t==="light"||t==="dark"?t:"system"}catch(e){return"system"}}
  function apply(t){if(t==="system")d.removeAttribute("data-theme");else d.setAttribute("data-theme",t)}
  var cur=get();apply(cur);
  document.addEventListener("DOMContentLoaded",function(){
    var wrap=document.createElement("div");wrap.className="theme-wrap";
    var b=document.createElement("button");b.type="button";b.className="theme-btn";b.setAttribute("aria-haspopup","menu");b.setAttribute("aria-expanded","false");
    var menu=document.createElement("ul");menu.className="theme-menu";menu.setAttribute("role","menu");menu.hidden=true;
    var items={};
    ORDER.forEach(function(k){
      var li=document.createElement("li");li.setAttribute("role","none");
      var it=document.createElement("button");it.type="button";it.setAttribute("role","menuitemradio");
      it.innerHTML="<span aria-hidden='true'>"+I[k]+"</span><span>"+L[k]+"</span><span class='ck' aria-hidden='true'>✓</span>";
      it.addEventListener("click",function(){choose(k)});
      li.appendChild(it);menu.appendChild(li);items[k]=it;
    });
    function paint(){b.textContent=I[cur]+" "+L.short[cur]+" ▾";b.setAttribute("aria-label",L.aria+": "+L.short[cur]);ORDER.forEach(function(k){items[k].setAttribute("aria-checked",String(k===cur))})}
    function open(){menu.hidden=false;b.setAttribute("aria-expanded","true");items[cur].focus()}
    function close(f){menu.hidden=true;b.setAttribute("aria-expanded","false");if(f)b.focus()}
    function choose(k){cur=k;apply(k);try{if(k==="system")localStorage.removeItem("theme");else localStorage.setItem("theme",k)}catch(e){}paint();close(true)}
    b.addEventListener("click",function(){menu.hidden?open():close(false)});
    document.addEventListener("click",function(e){if(!wrap.contains(e.target))close(false)});
    document.addEventListener("keydown",function(e){
      if(menu.hidden)return;
      if(e.key==="Escape"){close(true);return}
      if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();var i=ORDER.indexOf(document.activeElement===b?cur:ORDER.find(function(k){return items[k]===document.activeElement})||cur);i=(i+(e.key==="ArrowDown"?1:2))%3;items[ORDER[i]].focus()}
    });
    paint();wrap.appendChild(b);wrap.appendChild(menu);
    var grp=document.createElement("div");grp.className="top-tools";
    if(ALT){var a=document.createElement("a");a.className="lang-link";a.href=ALT;a.setAttribute("hreflang",en?"ja":"en");a.lang=en?"ja":"en";a.textContent=en?"\u65E5\u672C\u8A9E":"English";grp.appendChild(a)}
    grp.appendChild(wrap);
    var h=document.querySelector(".head");
    if(h){h.appendChild(grp)}else{var m=document.querySelector("main")||document.body,w=document.createElement("div");w.className="theme-bar";w.appendChild(grp);m.insertBefore(w,m.firstChild)}
  });
})();
</script>
"""


def alt_href(p):
    """この言語のページに対応する、もう一方の言語のページへの相対リンク。"""
    rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
    tgt = rel[3:] if rel.startswith("en/") else "en/" + rel
    if not os.path.exists(os.path.join(ROOT, tgt)):
        return ""
    t = os.path.join(ROOT, tgt)
    if os.path.basename(t) == "index.html":
        r = os.path.relpath(os.path.dirname(t), os.path.dirname(p)).replace(os.sep, "/")
        return "./" if r == "." else r + "/"
    return os.path.relpath(t, os.path.dirname(p)).replace(os.sep, "/")


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
            s = re.sub(r'<style id="theme-css"[^>]*>.*?</style>\n<script id="theme-js"[^>]*>.*?</script>\n', "", s, flags=re.S)
            open(p, "w", encoding="utf-8").write(s.replace("</head>", TAG.replace("@@ALT@@", alt_href(p)) + "</head>", 1))
            n += 1
    return n


if __name__ == "__main__":
    print("theme switch added to", run(), "files")
