#!/usr/bin/env python3
"""Build beats.itihasa.co as a static site from articles/*.json + *.html.
Usage: python3 build.py   -> writes ./site
"""
import json, re, html, pathlib, datetime, shutil, os
PREVIEW = os.environ.get("PREVIEW") == "1"
IDX = "index.html" if PREVIEW else ""

ROOT = pathlib.Path(__file__).parent
ART = ROOT / "articles"
OUT = ROOT / "site"

SITE = {
    "name": "Beats",
    "by": "by Itihasa",
    "url": "https://beats.itihasa.co",
    "email": "stories@itihasa.co",
    "x": "https://x.com/siddharth_ram",
    "linkedin": "https://www.linkedin.com/in/siddharthram",
    "newsletter": "https://www.linkedin.com/newsletters/the-beat-room-season-1-7462043969363927040",
    "beatlib": "https://github.com/boldcapplatform/beatlib",
}

def load_articles():
    arts = []
    # For essays on the same date, show the higher-numbered source first.
    for j in sorted(ART.glob("*.json"), reverse=True):
        if j.name in ("reading.json", "work.json"):
            continue
        d = json.loads(j.read_text())
        if "html_file" in d:
            d["html"] = (ART / d["html_file"]).read_text()
        for k, v in d.get("images", {}).items():
            d["html"] = d["html"].replace("{{%s}}" % k, v)
        d["html"] = d["html"].replace('<figure><img ', '<figure><img loading="lazy" onerror="this.parentElement.remove()" ')
        text = re.sub(r"<[^>]+>", " ", d["html"])
        d["words"] = len(text.split())
        d["minutes"] = max(1, round(d["words"] / 220))
        d["date_obj"] = datetime.date.fromisoformat(d["date"])
        d["date_h"] = d["date_obj"].strftime("%-d %B %Y")
        arts.append(d)
    arts.sort(key=lambda a: a["date_obj"], reverse=True)
    return arts

CSS = r"""
:root{
  --paper:#FFFFFF; --paper-2:#F4F0F4; --ink:#2A1B2D; --ink-2:#4E3D52; --ink-3:#7F7083;
  --rule:#E5DDE5; --gold:#C9A14A; --gold-ink:#9A7424; --blue:#3A2A4A;
  --measure:38rem; --gutter:clamp(1.25rem,4vw,3.5rem);
  --serif:"Newsreader",Georgia,"Times New Roman",serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --pencil:#6E2E66;
  --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
}
html[data-theme="dark"]{--paper:#17101B;--paper-2:#221929;--ink:#F0E8F0;--ink-2:#CBBFCC;--ink-3:#948796;--rule:#352A39;--gold:#D9B35E;--gold-ink:#E4C274;--blue:#B9A6D0;--pencil:#D4A1CF}
html{color-scheme:light}
html[data-theme="dark"]{color-scheme:dark}
.marg{font-family:var(--mono);font-size:.78rem;letter-spacing:.01em;color:var(--pencil)}
.marg.quiet{color:var(--ink-3)}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--serif);font-size:1.125rem;line-height:1.6;font-optical-sizing:auto;text-rendering:optimizeLegibility}
a{color:inherit;text-decoration-color:var(--gold);text-underline-offset:.18em;text-decoration-thickness:1px}
a:hover{text-decoration-color:currentColor}
a:focus-visible,button:focus-visible{outline:2px solid var(--gold);outline-offset:3px;border-radius:2px}
img{max-width:100%;height:auto;display:block}
::selection{background:var(--gold);color:#2A1B2D}

/* ---------- frame: the whole site reads like one long script page ---------- */
.frame{max-width:72rem;margin:0 auto;padding:0 var(--gutter)}
/* guide: a sticky strip that tells you where you are */
.guide{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:1px solid var(--rule);margin:0 calc(-1*var(--gutter));padding:0 var(--gutter)}
.guide .row{display:flex;align-items:center;justify-content:space-between;gap:1rem;height:3.2rem}
.guide .brand{font-family:var(--serif);font-size:1.15rem;font-weight:500;letter-spacing:-.01em;text-decoration:none;white-space:nowrap}
.guide .brand em{font-style:italic;color:var(--gold-ink);font-weight:400;font-size:.9rem;margin-left:.35rem}
.guide .steps{display:flex;gap:.2rem;overflow-x:auto;scrollbar-width:none;font-family:var(--mono);font-size:.74rem}
.guide .steps::-webkit-scrollbar{display:none}
.guide .steps a{text-decoration:none;color:var(--ink-3);padding:.35rem .55rem;border-radius:2px;white-space:nowrap;position:relative}
.guide .steps a:hover{color:var(--ink)}
.guide .steps a.on{color:var(--pencil)}
.guide .steps a.on::before{content:"";position:absolute;left:.55rem;right:.55rem;bottom:-.05rem;height:1px;background:var(--pencil)}
.guide .toggle{flex:none;margin-left:auto;font-family:var(--mono);font-size:.74rem;color:var(--ink-3);background:none;border:1px solid var(--rule);border-radius:999px;padding:.3rem .7rem;cursor:pointer;white-space:nowrap}
.guide .toggle:hover{color:var(--ink);border-color:var(--ink-3)}
.guide .bar{height:1px;background:var(--pencil);width:0;transition:width .15s linear;margin:0 calc(-1*var(--gutter))}
.guide .here{font-family:var(--mono);font-size:.74rem;color:var(--ink-3);display:none}
.guide .here{display:none}
.guide .swipe-hint{display:none}
@media(max-width:60rem){
  .guide .row{gap:.6rem;height:2.85rem}
  .guide .steps{flex:1;min-width:0;-webkit-overflow-scrolling:touch;scroll-padding-inline:.55rem}
  .guide .swipe-hint{display:block;padding:0 .55rem .4rem;color:var(--ink-3);font:.68rem var(--mono);line-height:1.25}
}
@media (prefers-reduced-motion:reduce){.guide .bar{transition:none}}

/* ---------- hero: one full fold, composed like a plate ---------- */
.hero{display:flex;flex-direction:column;padding:1.6rem 0 0}
.hero-mid{padding:clamp(2.5rem,7vh,5rem) 0 clamp(2rem,5vh,3.5rem)}
.hero-top{display:flex;justify-content:space-between;gap:1rem;padding-bottom:1.1rem;border-bottom:1px solid var(--rule)}
.hero h1 i{font-style:italic;font-weight:300;color:var(--gold-ink)}
.hero-index{border-top:1px solid var(--rule);padding-top:.4rem;display:grid;grid-template-columns:1fr}
@media(min-width:60rem){.hero-index{grid-template-columns:1fr;max-width:46rem}}
.hero-index a{display:grid;grid-template-columns:1.6rem 7.5rem 1fr;gap:0 .6rem;align-items:baseline;padding:.45rem 0;border-bottom:1px solid var(--rule);text-decoration:none}
.hero-index a:hover .t{text-decoration:underline;text-decoration-color:var(--gold)}
.hero-index .n{font-family:var(--mono);font-size:.74rem;color:var(--pencil)}
.hero-index .t{font-size:1.05rem}
.hero-index .d{font-family:var(--sans);font-size:.85rem;color:var(--ink-3);line-height:1.4}
@media(max-width:44rem){.hero-index a{grid-template-columns:1.6rem 1fr}.hero-index .d{grid-column:2}}

/* Size the masthead to its column so the title stays on one line. */
.hero-mid{container-type:inline-size}
.hero h1{
  font-size:min(6.4vw,5.75rem);
  font-size:min(7.65cqi,5.75rem);
  line-height:1.06;
  letter-spacing:-.045em;
  font-weight:400;
  margin:0 0 clamp(.3rem,1vw,.65rem);
  white-space:nowrap;
}
.hero p.lead{font-size:clamp(1.2rem,1.8vw,1.5rem);line-height:1.45;color:var(--ink-2);max-width:40rem;margin:0 0 1.8rem}
.worked-with{border-top:1px solid var(--rule);padding:.85rem 0 .9rem;margin-bottom:.55rem;display:flex;align-items:center;gap:.65rem 1.5rem;flex-wrap:wrap}
.worked-with h2{font:500 .65rem var(--mono);letter-spacing:.11em;text-transform:uppercase;color:var(--ink-3);margin:0;white-space:nowrap}
.worked-with ul{list-style:none;display:flex;align-items:center;flex-wrap:wrap;gap:.75rem clamp(1.15rem,3vw,2.4rem);padding:0;margin:0}
.worked-with img{height:.93rem;width:auto;max-width:6rem;object-fit:contain;filter:brightness(0);opacity:.44}
.worked-with img.worked-pramaana{height:1.3rem;max-width:8rem;opacity:.67}
html[data-theme="dark"] .worked-with img{filter:brightness(0) invert(1)}
@media(max-width:40rem){.worked-with{display:block}.worked-with h2{margin-bottom:.65rem}.worked-with img{height:.82rem;max-width:5.25rem}.worked-with img.worked-pramaana{height:1.12rem;max-width:7rem}}
.hero .clip{display:flex;gap:.9rem;align-items:center;text-decoration:none;max-width:26rem}
.hero button.clip{cursor:pointer;background:none;border:0;padding:0;color:inherit;font:inherit;text-align:left}
.hero .clip-dialog{max-width:calc(100vw - 2rem);padding:.75rem;border:1px solid var(--rule);border-radius:5px;background:var(--paper);color:var(--ink)}
.hero .clip-dialog::backdrop{background:rgba(16,12,18,.78)}
.hero .clip-dialog form{display:flex;justify-content:flex-end;margin:0 0 .5rem}
.hero .clip-dialog button{font:inherit;color:inherit;background:none;border:0;cursor:pointer}
.hero .clip-dialog.landscape .clip-player{width:min(56rem,calc(100vw - 4rem),calc((100dvh - 6rem) * 16 / 9));aspect-ratio:16/9}
.hero .clip-dialog.social .clip-player{width:min(34rem,calc(100vw - 4rem));height:min(38rem,calc(100dvh - 8rem));aspect-ratio:auto}
.hero .clip-dialog .clip-source{display:block;margin-top:.5rem;font-size:.85rem}
.hero .clip-dialog .clip-source[hidden]{display:none}
.hero .clip-player{display:block;width:min(20rem,calc(100vw - 4rem),calc((100dvh - 6rem) * .5625));aspect-ratio:9/16;border:0;border-radius:3px;background:var(--paper-2)}
.hero .clip .ph{flex:0 0 4.4rem;width:4.4rem;aspect-ratio:9/16;border-radius:3px;background:var(--paper-2);overflow:hidden;display:block}
.hero .clip img{width:100%;height:100%;object-fit:cover;display:block}
.hero .clip .tx{display:block;min-width:0}
.hero .clip .tx>span{display:block}
.hero .clip .t{font-size:1.05rem;line-height:1.3;margin:.15rem 0 .1rem}
.hero .clip .by{font-family:var(--sans);font-size:.82rem;color:var(--ink-3)}
.hero .clip:hover .t{text-decoration:underline;text-decoration-color:var(--gold)}
.hero .tee{margin:0;display:grid;gap:.5rem;font-family:var(--sans);font-size:.95rem;line-height:1.5;color:var(--ink-3)}
.hero .tee .wide{display:block;max-width:40rem;padding-bottom:.5rem;border-bottom:1px solid var(--rule)}
.hero .tee .deep{display:block;max-width:22rem;color:var(--ink-2)}
.hero .aside{font-family:var(--sans);font-size:.95rem;line-height:1.55;color:var(--ink-2);border-left:2px solid var(--pencil);padding-left:1.1rem;max-width:26rem}
.hero .marg{display:block;margin-bottom:1.2rem}
.hero .aside p{margin:0 0 .8rem}
.hero .aside a{text-decoration:none;border-bottom:1px solid var(--gold)}

/* ---------- sections ---------- */
section.block{padding:clamp(3rem,7vw,5.5rem) 0;border-top:1px solid var(--rule)}
.guide + section.block{border-top:0}
section.block>.grid{display:grid;grid-template-columns:minmax(0,1fr);gap:1.5rem 3rem}
@media(min-width:60rem){section.block>.grid{grid-template-columns:4fr 8fr}}
.block .side{align-self:start}
@media(min-width:60rem){.block .side{position:sticky;top:1.5rem}}
.block .side .marg{display:block;margin-bottom:.9rem}
@media(max-width:59.99rem){
  .block .side{
    padding:.85rem .85rem .95rem;
    border-block:1px solid var(--rule);
    background:var(--paper-2) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='44' height='26'%3E%3Ctext x='2' y='10' font-family='monospace' font-size='8' fill='%23927082' fill-opacity='.14'%3E%2B%20-%20%2B%3C/text%3E%3C/svg%3E");
  }
  .block .side .marg{margin-bottom:.5rem}
}
.block h2{font-size:clamp(1.6rem,2.6vw,2.2rem);line-height:1.15;letter-spacing:-.015em;font-weight:400;margin:0;text-wrap:balance;max-width:20ch}
@media(max-width:59.99rem){.block .side h2{max-width:none;text-wrap:pretty}}
.block .body{max-width:var(--measure)}
.block .body p{margin:0 0 1.15rem}
.block .body p:last-child{margin-bottom:0}
.beats p{display:grid;grid-template-columns:2.2rem 1fr;gap:0 .6rem;margin:0 0 1.3rem;font-size:1.2rem;line-height:1.5}
.beats p .marg{padding-top:.45rem}
.beats strong{font-weight:500}
.residence-reading{display:block;width:fit-content;margin-top:.55rem;font-family:var(--mono);font-size:.78rem;line-height:1.5;color:var(--ink-2)}

/* ---------- essay index ---------- */
.newsletter-note{font-size:.78rem;line-height:1.5;color:var(--ink-3);max-width:27ch;margin:.65rem 0 0}
.essays{list-style:none;margin:0;padding:0;max-width:none}
.essays li{border-top:1px solid var(--rule);padding:1.6rem 0;display:grid;grid-template-columns:minmax(0,1fr);gap:.4rem 1.6rem}
@media(min-width:44rem){.essays li{grid-template-columns:1fr 9.5rem}}
.essays li:last-child{border-bottom:1px solid var(--rule)}
.essays h3{margin:0 0 .35rem;font-size:clamp(1.35rem,2vw,1.7rem);line-height:1.2;letter-spacing:-.012em;font-weight:400}
.essays h3 a{text-decoration:none}
.essays h3 a:hover{text-decoration:underline}
.essays .dek{margin:0;color:var(--ink-2);max-width:var(--measure)}
.essays .meta{font-family:var(--mono);font-size:.78rem;color:var(--ink-3);line-height:1.6}
.essays .no{font-family:var(--mono);font-size:.78rem;color:var(--pencil);display:block;margin-bottom:.35rem}
.essays .meta .draft{color:var(--pencil)}
@media(min-width:44rem){.essays .meta{text-align:right}}

/* ---------- work / research lists ---------- */
.list{list-style:none;margin:0;padding:0}
.list li{padding:1.1rem 0;border-top:1px solid var(--rule)}
.list li:last-child{border-bottom:1px solid var(--rule)}
.list h3{margin:0 0 .25rem;font-size:1.25rem;font-weight:500;line-height:1.3}
.list h3 a{text-decoration:none}
.list h3 a:hover{text-decoration:underline}
.list p{margin:0;color:var(--ink-2);max-width:var(--measure)}
.list .where{font-family:var(--mono);font-size:.78rem;color:var(--ink-3);display:block;margin-top:.45rem}
.list .status{color:var(--pencil)}
/* work */
.work h3.kind{font-family:var(--mono);font-size:.78rem;font-weight:400;color:var(--pencil);margin:2.2rem 0 .9rem}
.work h3.kind:first-child{margin-top:0}
.vgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(14rem,1fr));gap:1.2rem 1.2rem;list-style:none;margin:0;padding:0}
.vgrid a{text-decoration:none;display:block}
.vgrid .th{aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:3px;background:var(--paper-2);filter:saturate(.9)}
.vgrid .t{display:block;margin:.55rem 0 .1rem;font-size:1.05rem;line-height:1.3}
.vgrid .f{font-family:var(--mono);font-size:.74rem;color:var(--ink-3);line-height:1.5}
.feature{display:grid;grid-template-columns:minmax(0,1fr);gap:1rem 1.6rem;margin:0 0 .5rem}
@media(min-width:44rem){.feature{grid-template-columns:7fr 5fr}}
.feature .th{aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:3px;background:var(--paper-2);color:transparent}
.feature .th.poster{aspect-ratio:auto;height:auto}
.feature h4{margin:0 0 .2rem;font-size:1.35rem;font-weight:500;line-height:1.25}
.feature .sub{margin:0 0 .6rem;font-style:italic;color:var(--ink-2)}
.feature p{margin:0 0 .6rem;color:var(--ink-2)}
.feature .credits{font-family:var(--mono);font-size:.74rem;color:var(--ink-3);line-height:1.7;margin:.6rem 0 0}
.feature .credits span{color:var(--ink-2)}
.events{list-style:none;margin:0;padding:0}
.events li{padding:1.1rem 0;border-top:1px solid var(--rule)}
.events li:last-child{border-bottom:1px solid var(--rule)}
.events h4{margin:0 0 .2rem;font-size:1.2rem;font-weight:500;line-height:1.3}
.events .where{font-family:var(--mono);font-size:.74rem;color:var(--ink-3);display:block;margin-bottom:.5rem}
.events p{margin:0;color:var(--ink-2);max-width:var(--measure)}
.strip{display:grid;grid-template-columns:repeat(6,1fr);gap:.4rem;margin:.8rem 0 .2rem}
.strip img{aspect-ratio:1;object-fit:cover;width:100%;border-radius:2px}
.events .more{font-family:var(--mono);font-size:.78rem;display:inline-block;margin-top:.6rem}
.sites{display:grid;grid-template-columns:repeat(auto-fill,minmax(16rem,1fr));gap:1.4rem;list-style:none;margin:0;padding:0}
.sites img{aspect-ratio:16/10;object-fit:cover;object-position:top;width:100%;border-radius:3px;border:1px solid var(--rule)}
.sites h4{margin:.6rem 0 .2rem;font-size:1.15rem;font-weight:500}
.sites p{margin:0;color:var(--ink-2);font-size:1rem}
/* reading log */
.reading{list-style:none;margin:0;padding:0}
.reading li{display:grid;grid-template-columns:minmax(0,1fr);gap:.3rem 1.4rem;padding:1rem 0;border-top:1px solid var(--rule)}
@media(min-width:44rem){.reading li{grid-template-columns:9rem 1fr}}
.reading li:last-child{border-bottom:1px solid var(--rule)}
.reading .id{font-family:var(--mono);font-size:.78rem;color:var(--ink-3);line-height:1.6;padding-top:.15rem}
.reading h3{margin:0 0 .15rem;font-size:1.1rem;font-weight:500;line-height:1.35}
.reading h3 a{text-decoration:none}
.reading h3 a:hover{text-decoration:underline}
.reading .who{font-family:var(--mono);font-size:.78rem;color:var(--ink-3);margin:0 0 .35rem}
.reading p.note{margin:0;color:var(--ink-2);max-width:var(--measure);font-size:1.05rem}
/* diagram */
.diagram{margin:0 0 2rem;max-width:var(--measure)}
.diagram svg{width:100%;height:auto;display:block}
.diagram .cap{font-family:var(--mono);font-size:.78rem;color:var(--ink-3);margin:.6rem 0 0;line-height:1.6}

/* ---------- contact ---------- */
.contact .body p{font-size:1.2rem}
.contact .ways{display:flex;flex-wrap:wrap;gap:.6rem 1.6rem;font-family:var(--sans);font-size:.95rem;margin-top:1.4rem}
.contact .ways a{text-decoration:none;border-bottom:1px solid var(--gold)}

footer{border-top:1px solid var(--rule);padding:2rem 0 3rem;font-family:var(--sans);font-size:.85rem;color:var(--ink-3);display:flex;flex-wrap:wrap;gap:.5rem 2rem;justify-content:space-between}
footer a{text-decoration:none;color:var(--ink-2)}

/* ---------- essay page ---------- */
.essay-head{padding:clamp(3rem,8vw,6rem) 0 2rem;max-width:46rem}
.essay-head .series{font-family:var(--mono);font-size:.78rem;color:var(--pencil);margin:0 0 1.2rem}
.essay-head h1{font-size:clamp(2rem,5vw,3.6rem);line-height:1.08;letter-spacing:-.02em;font-weight:400;margin:0 0 1rem;text-wrap:balance}
.essay-head .dek{font-size:clamp(1.15rem,1.7vw,1.4rem);line-height:1.45;color:var(--ink-2);margin:0 0 1.4rem;font-style:italic;font-weight:300}
.essay-head .meta{font-family:var(--mono);font-size:.78rem;color:var(--ink-3)}
.cover{max-width:46rem;margin:0 0 2.5rem;border-radius:3px;overflow:hidden}
.cover img{width:100%;aspect-ratio:16/9;object-fit:cover}
.prose{max-width:var(--measure);font-size:1.2rem;line-height:1.62;padding-bottom:3rem}
.prose p{margin:0 0 1.35rem}
.prose h3,.prose h4{font-weight:500;letter-spacing:-.01em;line-height:1.25;margin:2.6rem 0 .9rem}
.prose h3{font-size:1.55rem}
.prose h4{font-size:1.3rem;color:var(--ink-2)}
.prose blockquote{margin:2rem 0;padding:0 0 0 1.2rem;border-left:2px solid var(--gold);font-size:1.3rem;line-height:1.45;font-style:italic;font-weight:300;color:var(--ink)}
.prose ul,.prose ol{padding-left:1.3rem;margin:0 0 1.35rem}
.prose li{margin:0 0 .55rem}
.prose li::marker{color:var(--gold-ink)}
.prose figure{margin:2rem 0}
.prose figure img{border-radius:3px}
.prose figure.video{aspect-ratio:16/9}
.prose figure.video iframe{width:100%;height:100%;border:0;border-radius:3px}
.prose figure.diagram{width:48rem;max-width:calc(100vw - 2*var(--gutter));margin:2.2rem 0}
.prose aside.note{font-family:var(--sans);font-size:.95rem;line-height:1.55;background:var(--paper-2);padding:1rem 1.2rem;border-radius:3px;margin:1.6rem 0;color:var(--ink-2)}
.prose a{text-decoration-color:var(--gold)}
.essay-foot{border-top:1px solid var(--rule);padding:2rem 0 3rem;max-width:46rem;font-family:var(--sans);font-size:.95rem;color:var(--ink-2)}
.essay-foot p{margin:0 0 .6rem}
.essay-foot .next{font-family:var(--serif);font-size:1.35rem;line-height:1.3;margin-top:1.4rem}
.essay-foot .next a{text-decoration:none}
.essay-foot .next a:hover{text-decoration:underline}
"""

SCRIPT = r"""<script>
(function(){
  var root=document.documentElement, btn=document.getElementById('theme');
  var clipDialog=document.getElementById('clip-dialog');
  if(clipDialog){
    var clipPlayer=clipDialog.querySelector('iframe');
    var clipSource=clipDialog.querySelector('.clip-source');
    document.querySelectorAll('[data-youtube], [data-x-post]').forEach(function(trigger){
      trigger.addEventListener('click',function(event){
        if(event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        var title=trigger.dataset.videoTitle;
        clipDialog.setAttribute('aria-label',title);
        clipPlayer.title=title;
        clipDialog.classList.toggle('landscape',trigger.dataset.videoFormat==='landscape');
        var post=trigger.dataset.xPost;
        clipDialog.classList.toggle('social',Boolean(post));
        clipSource.hidden=!post;
        if(post) clipSource.href=trigger.href;
        clipDialog.showModal();
        clipPlayer.src=post
          ? 'https://platform.twitter.com/embed/Tweet.html?dnt=true&id='+encodeURIComponent(post)
          : 'https://www.youtube-nocookie.com/embed/'+encodeURIComponent(trigger.dataset.youtube)+'?playsinline=1&autoplay=1'+(trigger.dataset.videoStart ? '&start='+encodeURIComponent(trigger.dataset.videoStart) : '');
      });
    });
    clipDialog.addEventListener('close',function(){
      clipPlayer.removeAttribute('src');
    });
  }
  var saved=null; try{saved=localStorage.getItem('theme')}catch(e){}
  function apply(t){ if(t==='dark'){root.setAttribute('data-theme','dark'); if(btn) btn.textContent='light';} else {root.removeAttribute('data-theme'); if(btn) btn.textContent='dark';} }
  if(saved) apply(saved); else if(btn) btn.textContent=root.getAttribute('data-theme')==='dark'?'light':'dark';
  if(btn) btn.addEventListener('click',function(){ var t=root.getAttribute('data-theme')==='dark'?'light':'dark'; apply(t); try{localStorage.setItem('theme',t)}catch(e){} });
  var bar=document.getElementById('bar'), here=document.getElementById('here');
  var links=[].slice.call(document.querySelectorAll('.guide .steps a'));
  var secs=links.map(function(a){return document.getElementById(a.getAttribute('data-s'))}).filter(Boolean);
  function update(){
    var h=document.documentElement, p=(h.scrollTop)/(h.scrollHeight-h.clientHeight); if(bar) bar.style.width=(Math.max(0,Math.min(1,p))*100)+'%';
    var y=window.scrollY+window.innerHeight*0.35, cur=null;
    secs.forEach(function(s){ if(s.offsetTop<=y) cur=s; });
    links.forEach(function(a){ var on=cur&&a.getAttribute('data-s')===cur.id; a.classList.toggle('on',!!on); if(on&&here) here.textContent=a.textContent; });
    if(!cur&&here) here.textContent='';
  }
  window.addEventListener('scroll',update,{passive:true}); window.addEventListener('resize',update); update();
})();
</script>
"""

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<link rel="icon" href="{root}assets/favicon.ico" sizes="any">
<meta property="og:site_name" content="Beats: Narratives &amp; Models">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{ogtype}">
{ogimg}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@siddharth_ram">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..600;1,6..72,300..600&family=IBM+Plex+Mono:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}style.css">
</head>
<body>
<div class="frame">
{guide}"""

FOOT = """
<footer>
  <span>Beats: Narratives &amp; Models is Siddharth Ram's site, published by Beats by Itihasa.</span>
  <span><a href="{x}">X</a> &nbsp; <a href="{linkedin}">LinkedIn</a> &nbsp; <a href="{newsletter}">The Beat Room</a> &nbsp; <a href="mailto:{email}">{email}</a></span>
</footer>
</div>
{script}
</body>
</html>
"""

def esc(s): return html.escape(s, quote=True)

GUIDE = """<header class="guide" id="guide">
  <div class="row">
    <nav class="steps" aria-label="Sections">
      <a href="{root}{idx}#essays" data-s="essays">1 Essays</a>
      <a href="{root}{idx}#work" data-s="work">2 Work</a>
      <a href="{root}{idx}#frontier" data-s="frontier">3 Lens</a>
      <a href="{root}{idx}#residence" data-s="residence">4 Residence</a>
      <a href="{root}{idx}#research" data-s="research">5 Research</a>
      <a href="{root}{idx}#reading" data-s="reading">6 Reading</a>
      <a href="{root}{idx}#about" data-s="about">7 About</a>
    </nav>
    <span class="here" id="here"></span>
    <button class="toggle" id="theme" type="button" aria-label="Switch between light and dark">dark</button>
  </div>
  <span class="swipe-hint">Swipe tabs &harr;</span>
  <div class="bar" id="bar"></div>
</header>
"""

def guide_html(root):
    return GUIDE.format(root=root, idx=IDX)

def head(title, desc, url, root, ogimg="", ogtype="website", with_guide=True):
    share_image = SITE["url"] + "/assets/beats-share.jpg"
    image = esc(ogimg or share_image)
    og = f'<meta property="og:image" content="{image}">\n<meta name="twitter:image" content="{image}">'
    if not ogimg:
        og += '\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">'
        og += '\n<meta property="og:image:alt" content="Beats: Narratives &amp; Models by Itihasa">'
    return HEAD.format(title=esc(title), desc=esc(desc), url=esc(url), root=root, ogimg=og, ogtype=ogtype, idx=IDX, guide=(guide_html(root) if with_guide else ""))

def foot():
    return FOOT.format(script=SCRIPT, **SITE)

def build_index(arts):
    total = len(arts)
    essays = "\n".join(f"""
    <li>
      <div>
        <span class="no">No. {total - i:02d}</span>
        <h3><a href="essays/{a['slug']}/{IDX}">{esc(a['title'])}</a></h3>
        <p class="dek">{esc(a['dek'])}</p>
      </div>
      <div class="meta">{a['date_h']}<br>{a['minutes']} minute read{'<br><span class="draft">working draft</span>' if a.get('draft') else ''}</div>
    </li>""" for i, a in enumerate(arts))

    W = json.loads((ART / "work.json").read_text())
    md = W["microdoc"]
    credits = "<br>".join(f"{esc(k)} <span>{esc(v)}</span>" for k, v in md["credits"])
    def video_card(v):
        start = int(v.get("start", 0))
        timestamp = f"&amp;t={start}s" if start else ""
        start_attr = f' data-video-start="{start}"' if start else ""
        if v.get("x_post"):
            post_url = v["x_post"]
            post_id = post_url.rsplit("/", 1)[-1]
            source = f'href="{esc(post_url)}" data-x-post="{esc(post_id)}"'
        else:
            source = f'href="https://www.youtube.com/watch?v={esc(v["yt"])}{timestamp}"{start_attr} data-youtube="{esc(v["yt"])}"'
        return f"""
        <li><a {source} data-video-title="{esc(v['title'])}" data-video-format="landscape" aria-haspopup="dialog" aria-controls="clip-dialog"><img class="th" src="https://img.youtube.com/vi/{v['yt']}/hqdefault.jpg" alt="" loading="lazy"><span class="t">{esc(v['title'])}</span><span class="f">{esc(v['for'])}, {v['year']}</span></a></li>"""
    videos = "\n".join(video_card(v) for v in W["videos"])
    def ev(e):
        strip = ('<div class="strip">' + "".join(f'<img src="{esc(u)}" alt="" loading="lazy">' for u in e["photos"]) + '</div>') if e.get("photos") else ""
        more = f'<a class="more" href="{esc(e["link"])}">{esc(e["linktext"])}</a>' if e.get("link") else ""
        return f"""
        <li><h4>{esc(e['title'])}</h4><span class="where">{esc(e['where'])}</span><p>{esc(e['desc'])}</p>{strip}{more}</li>"""
    events = "\n".join(ev(e) for e in W["events"])
    shows = "\n".join(f"""
        <li><h4>{esc(x['title'])}</h4><span class="where">{esc(x['where'])}</span><p>{esc(x['desc'])}</p></li>""" for x in W["shows"])
    def site(w):
        img = f'<img src="{esc(w["img"])}" alt="" loading="lazy">'
        if w.get("url"): img = f'<a href="{esc(w["url"])}">{img}</a>'
        title = f'<a href="{esc(w["url"])}" style="text-decoration:none">{esc(w["title"])}</a>' if w.get("url") else esc(w["title"])
        return f"""
        <li>{img}<h4>{title}</h4><p>{esc(w['desc'])}</p></li>"""
    sites = "\n".join(site(w) for w in W["websites"])
    readings = json.loads((ART / "reading.json").read_text())
    reading = "\n".join(f"""
    <li>
      <div class="id">{esc(r['id'])}</div>
      <div>
        <h3><a href="{esc(r['url'])}">{esc(r['title'])}</a></h3>
        <p class="who">{esc(r['who'])}</p>
        <p class="note">{esc(r['note'])}</p>
      </div>
    </li>""" for r in readings)
    body = f"""
<main>
<section class="hero">
  <div class="hero-top">
    <span class="marg quiet">Beats by Itihasa &middot; a storytelling research lab</span>
  </div>
  <div class="hero-mid">
    <h1>Beats: Narratives <i>&amp;</i> Models</h1>
    <p class="lead">Storytelling in Residence to Frontier Research &amp; Startups</p>
    <button class="clip" type="button" data-youtube="Mjz8Z2I0w_g" data-video-title="What's the story of your company? — Ben Horowitz" aria-haspopup="dialog" aria-controls="clip-dialog">
      <span class="ph"><img src="assets/horowitz.jpg" alt="" loading="lazy"></span>
      <span class="tx"><span class="marg quiet">Watch, one minute</span><span class="t">What's the story of your company?</span><span class="by">Ben Horowitz</span></span>
    </button>
    <dialog class="clip-dialog" id="clip-dialog" aria-label="What's the story of your company?">
      <form method="dialog"><button type="submit" autofocus>Close</button></form>
      <iframe class="clip-player" title="What's the story of your company? — Ben Horowitz" referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>
      <a class="clip-source" target="_blank" rel="noopener" hidden>Open original post on X</a>
    </dialog>
  </div>
</section>
<section class="worked-with" aria-labelledby="worked-with-title">
  <h2 id="worked-with-title">Previously Worked With</h2>
  <ul>
    <li><img class="worked-pramaana" src="assets/worked-pramaana.svg" alt="Pramaana Labs"></li>
    <li><img src="assets/worked-accel.svg" alt="Accel"></li>
    <li><img src="assets/worked-boldcap.png" alt="BoldCap"></li>
    <li><img src="assets/worked-polygon.svg" alt="Polygon"></li>
    <li><img src="assets/worked-hyphenate.svg" alt="Hyphenate"></li>
    <li><img src="assets/worked-unboxingblr.svg" alt="UnboxingBLR"></li>
  </ul>
</section>
{guide_html("")}
<section class="block" id="essays">
  <div class="grid">
    <div class="side"><span class="marg">§1 Essays</span>
    <h2>The Beat Room is where I write it down, one essay at a time.</h2>
    <p class="newsletter-note">The Beat Room is my newsletter on storytelling, AI and venture. Newest first. It also goes out on <a href="{SITE['newsletter']}">LinkedIn</a>.</p></div>
    <div>
      <ul class="essays">{essays}
      </ul>
    </div>
  </div>
</section>

<section class="block" id="work">
  <div class="grid">
    <div class="side"><span class="marg">§2 Work</span>
    <h2>This is the work I have done across the Frontier &amp; Beyond</h2></div>
    <div class="work">
      <h3 class="kind">Micro documentary</h3>
      <div class="feature">
        <a href="{esc(md['url'])}"><img class="th poster" src="assets/pramaana-poster.jpg" alt="{esc(md['title'])} poster" width="1785" height="2526" loading="lazy"></a>
        <div>
          <h4><a href="{esc(md['url'])}" style="text-decoration:none">{esc(md['title'])}</a></h4>
          <p class="sub">{esc(md['sub'])}. {esc(md['length'])}, {md['year']}.</p>
          <p>{esc(md['desc'])}</p>
          <div class="credits">{credits}</div>
        </div>
      </div>
      <h3 class="kind">Videos</h3>
      <ul class="vgrid">{videos}
      </ul>
      <h3 class="kind">Events and rooms</h3>
      <ul class="events">{events}
      </ul>
      <h3 class="kind">Websites and brands</h3>
      <ul class="sites">{sites}
      </ul>
      <h3 class="kind">Shows</h3>
      <ul class="events">{shows}
      </ul>
      <h3 class="kind">Research work</h3>
      <p style="margin:0;color:var(--ink-2);max-width:var(--measure)">BeatLib, the retelling benchmark, Beatcode and the rest of the RLNR program are in <a href="#research">the research section</a>, with their status.</p>
    </div>
  </div>
</section>

<section class="block" id="frontier">
  <div class="grid">
    <div class="side"><span class="marg">§3 The lens</span>
    <h2>Civilisations are built on innovations and narratives.</h2></div>
    <div class="body beats">
      <p><span class="marg">01</span><span>Innovation changes what is possible. Narrative changes what people believe. The greatest problems in the world get solved where the two meet.</span></p>
      <p><span class="marg">02</span><span>Religions were the first media companies. A text, a programme of practice, and a community bound by one story, carried across centuries by believers who became evangelists. No distribution deal has ever matched it.</span></p>
      <p><span class="marg">03</span><span>A frontier lab or startup is a mission in search of believers. My work is to give a mission its text, its practice and its community, so the people who understand it become the people who carry it.</span></p>
    </div>
  </div>
</section>

<section class="block" id="residence">
  <div class="grid">
    <div class="side"><span class="marg">§4 Residence</span>
    <h2>As a Storyteller-in-Residence, I work with your firm in three ways.</h2></div>
    <div class="body beats">
      <p><span class="marg">01</span><span><strong>Writing Room.</strong> Your team and I form a writing room to engineer the firm's narratives and push them out, directly or through PR. I own it and I drive it.</span></p>
      <p><span class="marg">02</span><span><strong>Programs.</strong> I structure programs that build a community of practice around your firm, so the people who should believe in the work have a place to gather around it.</span></p>
      <p><span class="marg">03</span><span><strong>New Media.</strong> If you want to go beyond narratives and build a media house of your own, I put it together: newsletters, podcasts, documentaries, shows and events.</span></p>
      <p><span class="marg">&nbsp;</span><span>I take a few residencies a year, usually by introduction. <a class="residence-reading" href="essays/what-is-a-storytelling-intelligence-lab/{IDX}">Read more about What Is a Storytelling Intelligence Lab &rarr;</a></span></p>
    </div>
  </div>
</section>

<section class="block" id="research">
  <div class="grid">
    <div class="side"><span class="marg">§5 Research</span>
    <h2>I am learning by research, and this is what I am working through right now.</h2></div>
    <div>
      <p style="margin:0 0 1.4rem;max-width:var(--measure);color:var(--ink-2)">This is personal research, not a lab programme. I am a storyteller learning how models are trained to write, and the question I keep returning to is whether story structure can be checked the way code is checked. I call that idea RLNR, reinforcement learning from narrative rewards, and these are the threads I am pulling on.</p>
      <figure class="diagram">
        <svg viewBox="0 0 640 252" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The RLNR loop: a brief becomes a story, the story is checked by a verifier and a judge, the combined reward trains the model, and the model writes the next story.">
          <defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
          <g fill="none" stroke="currentColor" stroke-width="1.2" color="var(--ink-2)">
            <rect x="20" y="80" width="130" height="60" rx="3"/>
            <rect x="255" y="20" width="130" height="60" rx="3"/>
            <rect x="255" y="150" width="130" height="60" rx="3"/>
            <rect x="490" y="80" width="130" height="60" rx="3"/>
            <path d="M150 100 C200 100 200 50 255 50" marker-end="url(#ah)"/>
            <path d="M150 120 C200 120 200 180 255 180" marker-end="url(#ah)"/>
            <path d="M385 50 C440 50 440 100 490 100" marker-end="url(#ah)"/>
            <path d="M385 180 C440 180 440 120 490 120" marker-end="url(#ah)"/>
            <path d="M555 140 L555 222 L60 222 L60 142" marker-end="url(#ah)" stroke-dasharray="4 4"/>
          </g>
          <g font-family="Newsreader, Georgia, serif" font-size="15" fill="currentColor" color="var(--ink)" text-anchor="middle">
            <text x="85" y="106">The model writes</text><text x="85" y="126">a story</text>
            <text x="320" y="46">A verifier checks</text><text x="320" y="66">the structure</text>
            <text x="320" y="176">A judge reads</text><text x="320" y="196">for taste</text>
            <text x="555" y="106">The two become</text><text x="555" y="126">one reward</text>
          </g>
          <g font-family="IBM Plex Mono, monospace" font-size="10.5" fill="currentColor" color="var(--pencil)" text-anchor="end">
            <text x="246" y="40">beats, value shifts, commitments</text>
            <text x="246" y="206">surprise, specificity, voice</text>
          </g>
          <g font-family="IBM Plex Mono, monospace" font-size="10.5" fill="currentColor" color="var(--ink-3)" text-anchor="middle">
            <text x="320" y="244">the reward trains the next draft</text>
          </g>
        </svg>
        <p class="cap">Fig. 1. The RLNR loop as I currently understand it. The verifier's share is the part a storyteller can make checkable, so that is where I am looking.</p>
      </figure>
      <ul class="list">
        <li>
          <h3>Retelling fidelity as a benchmark</h3>
          <p>A story that works survives retelling. I am testing this by having models retell a story and checking which beats, value shifts and claims survive, against a beat graph I draw by hand first.</p>
          <span class="where"><span class="status">trying now</span> &middot; a hand-run experiment, no GPUs needed</span>
        </li>
        <li>
          <h3>Beatcode</h3>
          <p>Reinforcement learning on storytelling by making a model write a real story language, ink, so that compile success, branch reachability and declared value shifts become verifiable rewards alongside a judge. The question is whether you can code a story rather than generate one.</p>
          <span class="where"><span class="status">sketching</span> &middot; a small open model, modest compute</span>
        </li>
        <li>
          <h3>Story as spec for agents</h3>
          <p>The Storytelling Engineering question, made testable: do agents that receive a narrative brief keep the intent across handoffs better than agents that receive a specification? If they do, storytelling is an alignment tool, not a marketing one.</p>
          <span class="where"><span class="status">thinking about</span> &middot; the question labs would care about</span>
        </li>
        <li>
          <h3><a href="{SITE['beatlib']}">BeatLib benchmarks</a></h3>
          <p>A skill has no benchmark of its own, so I measure the lift it gives a fixed base model on a fixed rubric, on briefs it has never seen. Constraint satisfaction today; a slop floor, a faithfulness check and a calibrated judge next.</p>
          <span class="where"><span class="status">ongoing</span> &middot; in the open on GitHub</span>
        </li>
        <li>
          <h3>Autoformalising rule books</h3>
          <p>What happens when a story rule book, the Ramayana or a constitution is formalised well enough for a machine to check a draft against it. This is where formal methods and story meet, and where the Natya Shastra's rasa becomes a typed vocabulary instead of a metaphor.</p>
          <span class="where"><span class="status">exploring</span></span>
        </li>
      </ul>
    </div>
  </div>
</section>

<section class="block" id="reading">
  <div class="grid">
    <div class="side"><span class="marg">§6 Reading</span>
    <h2>These are the papers I am reading, with the note I took on each.</h2></div>
    <div>
      <p style="margin:0 0 1.4rem;max-width:var(--measure);color:var(--ink-2)">First sweep, November 2026, added to monthly. The note is mine, not the abstract.</p>
      <ul class="reading">{reading}
      </ul>
    </div>
  </div>
</section>

<section class="block" id="about">
  <div class="grid">
    <div class="side"><span class="marg">§7 About</span>
    <h2>I am a failed founder and a failed filmmaker, and blending the two became my job.</h2></div>
    <div class="body">
      <p>Beats is part of Itihasa Collective, an incubator for storytellers working in film and advertising.</p>
      <p>I live in two worlds. One is frontier AI, which I see every week through the fund. The other is culture: cinema, the internet, my own family. Beats is about the gap between them.</p>
      <p>Where AI is going is knowable if you pay attention. Where people are going is the mystery, and that is what I chase.</p>
      <p>I write in the first person and I am not neutral. I work in venture and I am betting my own time on this.</p>
      <p>I take a few residencies a year, usually by introduction. If you are building something at the frontier and want to talk, write to <a href="mailto:{SITE['email']}">{SITE['email']}</a>, or find me on <a href="{SITE['x']}">X</a> and <a href="{SITE['linkedin']}">LinkedIn</a>.</p>
    </div>
  </div>
</section>

</main>
"""
    desc = "Essays, films and research by Siddharth Ram on storytelling, AI and how new ideas earn belief."
    return head("Beats: Narratives & Models", desc, SITE["url"] + "/", "", with_guide=False) + body + foot()

def build_essay(a, arts):
    i = arts.index(a)
    nxt = arts[(i + 1) % len(arts)]
    url = f"{SITE['url']}/essays/{a['slug']}/"
    body = f"""
<main>
<article>
  <header class="essay-head">
    <p class="series">The Beat Room, Season 1{', draft' if a.get('draft') else ''}</p>
    <h1>{esc(a['title'])}</h1>
    <p class="dek">{esc(a['dek'])}</p>
    <p class="meta">Siddharth Ram. {a['date_h']}. {a['minutes']} minute read.</p>
  </header>
  {('<figure class="cover"><img src="%s" alt="" onerror="this.parentElement.remove()"></figure>' % esc(a['cover'])) if a.get('cover') else ''}
  <div class="prose">
{a['html']}
  </div>
  <footer class="essay-foot">
    <p>{('This essay first went out in <a href="%s">The Beat Room on LinkedIn</a>. ' % esc(a['source'])) if a.get('source') else 'This essay is a working draft for The Beat Room. '}If it was useful, <a href="{SITE['newsletter']}">subscribe there</a> or write to <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p>
    <p class="next">Read next: <a href="../{nxt['slug']}/{IDX}">{esc(nxt['title'])}</a></p>
  </footer>
</article>
</main>
"""
    return head(a["title"] + " | Beats: Narratives & Models", a["dek"], url, "../../", a["cover"], "article") + body + foot()

def build_404():
    body = """
<main>
  <section class="essay-head">
    <p class="series">Beats: Narratives &amp; Models</p>
    <h1>Page not found</h1>
    <p class="dek">The page you are looking for could not be found.</p>
    <p><a href="/">Return to the home page</a></p>
  </section>
</main>
"""
    return head("Page not found | Beats", "Page not found.",
                SITE["url"] + "/404.html", "/") + body + foot()

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    arts = load_articles()
    (OUT / "style.css").write_text(CSS.strip() + "\n")
    shutil.copytree(ROOT / "site-assets", OUT / "assets")
    (OUT / "index.html").write_text(build_index(arts))
    (OUT / "404.html").write_text(build_404())
    for a in arts:
        d = OUT / "essays" / a["slug"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(build_essay(a, arts))
    print(f"built {len(arts)} essays ->", OUT)

if __name__ == "__main__":
    main()
