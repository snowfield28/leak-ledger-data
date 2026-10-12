#!/usr/bin/env python3
"""全HTMLに、ライト／ダーク／端末に合わせる の切り替えボタンを足す（入っていれば何もしない）。
build_pages.py の最後に呼ばれる。選んだ設定はブラウザの localStorage に保存する（使えなければ保存せず動く）。"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = 'id="theme-js"'
TAG = r'''<style id="theme-css">
.theme-bar{display:flex;justify-content:flex-end;margin:0 0 6px}
.theme-btn{font:inherit;font-size:12.5px;line-height:1;color:var(--muted);background:var(--surface);border:1px solid var(--line);border-radius:99px;padding:7px 12px;cursor:pointer;white-space:nowrap}
.theme-btn:hover{color:var(--ink)}
.theme-btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
</style>
<script id="theme-js">
(function(){
  var d=document.documentElement,en=(d.lang||"ja").indexOf("en")===0;
  var L=en?{system:"Auto",light:"Light",dark:"Dark",aria:"Color theme: "}:{system:"自動",light:"ライト",dark:"ダーク",aria:"表示モード："};
  var I={system:"◐",light:"☀",dark:"☾"},ORDER=["system","light","dark"];
  function get(){try{var t=localStorage.getItem("theme");return t==="light"||t==="dark"?t:"system"}catch(e){return"system"}}
  function apply(t){if(t==="system")d.removeAttribute("data-theme");else d.setAttribute("data-theme",t)}
  var cur=get();apply(cur);
  document.addEventListener("DOMContentLoaded",function(){
    var b=document.createElement("button");b.type="button";b.className="theme-btn";
    function paint(){b.textContent=I[cur]+" "+L[cur];b.setAttribute("aria-label",L.aria+L[cur])}
    b.addEventListener("click",function(){cur=ORDER[(ORDER.indexOf(cur)+1)%3];apply(cur);try{if(cur==="system")localStorage.removeItem("theme");else localStorage.setItem("theme",cur)}catch(e){}paint()});
    paint();
    var h=document.querySelector(".head");
    if(h){h.appendChild(b)}else{var m=document.querySelector("main")||document.body,w=document.createElement("div");w.className="theme-bar";w.appendChild(b);m.insertBefore(w,m.firstChild)}
  });
})();
</script>
'''


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
    print("theme switch added to", run(), "files")
