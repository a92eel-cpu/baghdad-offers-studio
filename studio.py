"""استوديو «عروض بغداد» — قوالب 50/50 بمناطق أمان إنستغرام.

الاستخدام:
  python3 studio.py offer.json OUTDIR [--formats post,story,carousel,reel]
offer.json:
  merchant, category, area, title, old_price, new_price, discount_pct, valid_until (نص عربي), receipt_no,
  handle (حساب إنستغرام بدون @), logo (مسار), media: [مسارات صور أو فيديو واحد], items: [{name, old_price, new_price, media}]
"""
import json, sys, html, pathlib, asyncio, subprocess, shutil, wave, argparse
import numpy as np
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).parent.resolve()
F = (ROOT / "fonts").as_uri()
MARK = (ROOT / "mark.svg").read_text()
FPS = 30

def faces():
    out = ""
    for fam, d, ws in [("Alex", "alexandria", [700, 800, 900]), ("Taj", "tajawal", [400, 500, 700, 800])]:
        for w in ws:
            out += (f"@font-face{{font-family:{fam};font-weight:{w};src:url({F}/{d}-arabic-{w}-normal.woff2);"
                    "unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF,U+200C-200E}\n"
                    f"@font-face{{font-family:{fam};font-weight:{w};src:url({F}/{d}-latin-{w}-normal.woff2);"
                    "unicode-range:U+0000-00FF,U+2000-206F}\n")
    return out

CSS = faces() + """
:root{--ink:#15112B;--ink-2:#2A2350;--lime:#D4FF3A;--paper:#F5F0E4;--coral:#E8364A;--muted:#6A6480}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:transparent}
body{font-family:Taj,sans-serif;direction:rtl;color:var(--ink);-webkit-font-smoothing:antialiased}
.cv{position:relative;overflow:hidden}
.ground{position:absolute;inset:0;background:var(--ink);
  background-image:radial-gradient(circle at 1px 1px,rgba(212,255,58,.13) 1.6px,transparent 2px);background-size:36px 36px}
.media{position:absolute;left:0;right:0;top:0;overflow:hidden;background:var(--ink-2)}
.media img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.seam{position:absolute;left:0;right:0;height:10px;background:var(--lime)}
/* شارة العميل */
.client{position:absolute;display:flex;align-items:center;gap:16px;background:var(--paper);border-radius:999px;padding:8px 26px 8px 8px}
.client .lg{width:76px;height:76px;border-radius:50%;background:#fff center/cover no-repeat;box-shadow:0 0 0 3px var(--ink)}
.client .nm{font-family:Alex;font-weight:900;font-size:30px;line-height:1.1;color:var(--ink);max-width:520px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.client .hd{font-weight:700;font-size:20px;color:var(--muted);direction:ltr;text-align:right}
/* شارتنا */
.ours{position:absolute;display:flex;align-items:center;gap:10px;background:var(--ink);border-radius:999px;padding:6px 18px 6px 6px}
.ours svg{width:54px;height:54px}
.ours span{font-family:Alex;font-weight:900;font-size:22px;color:var(--paper)}
/* الوصل */
.rc{position:absolute;background:var(--paper);--z:18px;
  -webkit-mask:conic-gradient(from -45deg at bottom,#0000,#000 1deg 89deg,#0000 90deg) 50% 100%/calc(2*var(--z)) 51% repeat-x,
               conic-gradient(from 135deg at top,#0000,#000 1deg 89deg,#0000 90deg) 50% 0/calc(2*var(--z)) 51% repeat-x;
  padding:44px 48px 52px}
.rc .no{display:flex;justify-content:space-between;font-weight:700;font-size:21px;color:var(--muted)}
.rc .ti{font-family:Alex;font-weight:900;font-size:52px;line-height:1.35;margin-top:10px;text-wrap:pretty;padding-left:130px}
.rc .dash{border-top:4px dashed rgba(21,17,43,.25);margin:20px -6px}
.rc .pr{display:flex;align-items:center;justify-content:space-between;gap:20px}
.rc .lbl{font-weight:700;font-size:26px;white-space:nowrap}
.rc .old{font-family:Alex;font-weight:800;font-size:38px;color:var(--muted);position:relative;white-space:nowrap}
.rc .old i{position:absolute;left:-4px;right:-4px;top:52%;height:6px;background:var(--coral);display:block;transform-origin:right center}
.rc .new{font-family:Alex;font-weight:900;font-size:100px;line-height:1;white-space:nowrap;display:flex;align-items:baseline;gap:10px}
.rc .new small{font-size:34px}
.rc .meta{display:flex;flex-wrap:wrap;gap:8px 24px;font-size:23px;font-weight:500}
.rc .meta b{font-weight:800}
.rc .say{margin:22px -48px -52px;background:var(--lime);display:flex;justify-content:space-between;align-items:center;padding:16px 48px 26px}
.rc .say b{font-family:Alex;font-weight:900;font-size:34px}
.rc .say span{font-weight:700;font-size:21px}
/* الختم */
.st{position:absolute;width:210px;height:210px;transform:rotate(14deg)}
.st .d{position:absolute;inset:0;border-radius:50%;background:var(--coral);box-shadow:0 0 0 9px var(--ink)}
.st .r{position:absolute;inset:14px;border-radius:50%;border:4px dashed rgba(245,240,228,.75)}
.st .v{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--paper)}
.st .v b{font-family:Alex;font-weight:900;font-size:68px;line-height:.95}
.st .v span{font-weight:800;font-size:24px}
/* السلايدات */
.ix{position:absolute;font-family:Alex;font-weight:800;font-size:22px;color:var(--ink);background:var(--lime);border-radius:999px;padding:6px 18px}
.rc.strip{padding:34px 44px 40px}
.strip .nm{font-family:Alex;font-weight:900;font-size:46px;line-height:1.3}
"""

def esc(x): return html.escape(str(x or ""))
def money(v):
    try: return f"{int(str(v).replace(',', '')):,}"
    except Exception: return esc(v)
def pct(o):
    if o.get("discount_pct"): return int(o["discount_pct"])
    try:
        a = int(str(o["old_price"]).replace(",", "")); b = int(str(o["new_price"]).replace(",", ""))
        return round((a - b) * 100 / a)
    except Exception: return None
def uri(p): return pathlib.Path(p).resolve().as_uri() if p else ""

def client_badge(o, x, y, right=True):
    side = f"right:{x}px" if right else f"left:{x}px"
    logo = f"background-image:url('{uri(o.get('logo'))}')" if o.get("logo") else ""
    hd = f"<div class='hd'>@{esc(o['handle'])}</div>" if o.get("handle") else ""
    return (f"<div class='client' style='{side};top:{y}px'><div class='lg' style=\"{logo}\"></div>"
            f"<div><div class='nm'>{esc(o.get('merchant'))}</div>{hd}</div></div>")

def our_badge(x, y):
    return f"<div class='ours' style='left:{x}px;top:{y}px'>{MARK}<span>عروض بغداد</span></div>"

def stamp(o, x, y, size=210):
    p = pct(o)
    if not p: return ""
    k = size / 210
    return (f"<div class='st' style='left:{x}px;top:{y}px;transform:rotate(14deg) scale({k});transform-origin:top left'>"
            f"<div class='d'></div><div class='r'></div><div class='v'><b>{p}%</b><span>خصم</span></div></div>")

def receipt(o, x, y, w, cta="التفاصيل بالكابشن ←", title_size=52, price_size=100):
    old = (f"<div class='pr'><span class='lbl' style='font-weight:500'>السعر قبل</span>"
           f"<span class='old'>{money(o['old_price'])}<i></i></span></div>") if o.get("old_price") else ""
    no = f"وصل رقم {int(o['receipt_no']):04d}" if o.get("receipt_no") else ""
    newp = money(o.get("new_price")); ps = price_size if len(newp) <= 6 else int(price_size * .86)
    return f"""<div class='rc' style='left:{x}px;top:{y}px;width:{w}px'>
      <div class='no'><span>{' · '.join(x for x in [esc(o.get('category')), no] if x)}</span></div>
      <div class='ti' style='font-size:{title_size}px'>{esc(o.get('title'))}</div>
      <div class='dash'></div>{old}
      <div class='pr' style='margin-top:4px'><span class='lbl'>هسه بـ</span><span class='new' style='font-size:{ps}px'>{newp}<small>د.ع</small></span></div>
      <div class='dash'></div>
      <div class='meta'><span>المكان: <b>{esc(o.get('area'))}</b></span><span>لغاية: <b>{esc(o.get('valid_until'))}</b></span></div>
      <div class='say'><b>وصلك العرض</b><span>{cta}</span></div></div>"""

def media_box(src, top, h, hole=False):
    inner = "" if hole or not src else f"<img src='{uri(src)}'>"
    bg = "background:transparent" if hole else ""
    return f"<div class='media' style='top:{top}px;height:{h}px;{bg}'>{inner}</div><div class='seam' style='top:{top+h}px'></div>"

def doc(body, W, H, ground=True):
    g = "<div class='ground'></div>" if ground else ""
    return (f"<!doctype html><html lang='ar' dir='rtl'><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body><div class='cv' style='width:{W}px;height:{H}px'>{g}{body}</div></body></html>")

# ---------- التخطيطات ----------
def post(o, media):
    """منشور 4:5 — النصف العلوي للعميل، النصف السفلي وصلنا."""
    W, H = 1080, 1350
    body = (media_box(media, 0, 720) + client_badge(o, 40, 40) + our_badge(40, 50) +
            receipt(o, 90, 670, 900, title_size=50, price_size=104) + stamp(o, 26, 590, 200))
    return doc(body, W, H), W, H

def tall(o, media, kind, hole=False):
    """ستوري أو ريلز 9:16 — الريلز: كل النص بين y=290 و y=1250، ويُترك 230px يميناً في الثلث السفلي.
    الستوري: النص بين y=230 و y=1580."""
    W, H = 1080, 1920
    if kind == "reel":
        mh, rx, rw, top, ts, ps = 740, 65, 785, 290, 42, 82
        cta = "راسلهم من الكابشن ←"
        ours = our_badge(65, top)
        client = client_badge(o, 65, top)
    else:
        mh, rx, rw, top, ts, ps = 980, 65, 950, 230, 50, 100
        cta = "راسلنا للتفاصيل ←"
        ours = our_badge(400, 1500)
        client = client_badge(o, 65, top)
    body = (media_box(media, 0, mh, hole) + client + (our_badge(65, top) if kind == "reel" else "") +
            receipt(o, rx, mh - 40, rw, cta=cta, title_size=ts, price_size=ps) +
            stamp(o, 20, mh - 175, 170) + (ours if kind != "reel" else ""))
    return doc(body, W, H, ground=True), W, H

def slide_item(o, it, i, n):
    W, H = 1080, 1350
    oo = dict(o, old_price=it.get("old_price"), new_price=it.get("new_price"))
    old = f"<span class='old'>{money(it['old_price'])}<i></i></span>" if it.get("old_price") else ""
    body = (media_box(it.get("media"), 0, 1000) + client_badge(o, 40, 40) +
            f"<div class='ix' style='left:40px;top:52px'>{i}/{n}</div>" +
            f"""<div class='rc strip' style='top:960px;left:40px;width:1000px;height:360px'>
                 <div class='nm'>{esc(it.get('name'))}</div>
                 <div class='pr' style='display:flex;justify-content:space-between;align-items:center;margin-top:14px'>{old}
                   <span class='new' style='font-family:Alex;font-weight:900;font-size:86px;display:flex;gap:10px;align-items:baseline'>{money(it.get('new_price'))}<small style='font-size:30px'>د.ع</small></span></div></div>""" +
            stamp(oo, 40, 820, 170))
    return doc(body, W, H)

def slide_end(o, n):
    W, H = 1080, 1350
    logo = f"background-image:url('{uri(o.get('logo'))}')" if o.get("logo") else ""
    no = f"وصل رقم {int(o['receipt_no']):04d}" if o.get("receipt_no") else ""
    hd = f"<div style='font-weight:700;font-size:30px;direction:ltr;color:var(--lime)'>@{esc(o['handle'])}</div>" if o.get("handle") else ""
    body = f"""
      <div style="position:absolute;top:130px;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:20px;color:var(--paper)">
        <div style="width:220px;height:220px;border-radius:50%;background:#fff center/cover no-repeat;{logo};box-shadow:0 0 0 8px var(--lime)"></div>
        <div style="font-family:Alex;font-weight:900;font-size:64px">{esc(o.get('merchant'))}</div>{hd}
      </div>
      <div class="rc" style="left:120px;top:640px;width:840px">
        <div class="no"><span>{no}</span></div>
        <div class="ti" style="font-size:46px;padding-left:0">{esc(o.get('title'))}</div>
        <div class="dash"></div>
        <div class="meta" style="font-size:28px;flex-direction:column;gap:12px">
          <span>المكان: <b>{esc(o.get('area'))}</b></span><span>العرض لغاية: <b>{esc(o.get('valid_until'))}</b></span>
          <span>للطلب: <b>راسلهم على حسابهم</b></span></div>
        <div class="say"><b>وصلك العرض</b><span>احفظ المنشور ←</span></div></div>
      {our_badge(40, 40)}<div class="ix" style="right:40px;top:52px">{n}/{n}</div>"""
    return doc(body, W, H)

# ---------- التصيير ----------
async def shoot(pages, outdir):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, (d, W, H) in pages.items():
            t = outdir / f"_{name}.html"; t.write_text(d, encoding="utf-8")
            pg = await b.new_page(viewport={"width": W, "height": H})
            await pg.goto(t.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
            await pg.screenshot(path=str(outdir / f"{name}.png")); await pg.close(); t.unlink()
        await b.close()

def is_video(p): return p and pathlib.Path(p).suffix.lower() in (".mp4", ".mov", ".m4v", ".webm")

def build_stills(o, outdir, formats):
    imgs = [m for m in o.get("media", []) if not is_video(m)]
    hero = imgs[0] if imgs else None
    pages = {}
    if "post" in formats: pages["post"] = post(o, hero)
    if "story" in formats: pages["story"] = tall(o, hero, "story")
    if "carousel" in formats and o.get("items"):
        n = len(o["items"]) + 2
        pages["slide_01"] = post(o, o["items"][0].get("media") or hero)
        for i, it in enumerate(o["items"], start=2):
            pages[f"slide_{i:02d}"] = (slide_item(o, it, i, n), 1080, 1350)
        pages[f"slide_{n:02d}"] = (slide_end(o, n), 1080, 1350)
    asyncio.run(shoot(pages, outdir))
    return sorted(str(outdir / f"{k}.png") for k in pages)

# ---------- الريلز: فيديو العميل أو صوره + إطارنا المتحرك ----------
ANIM_T = 4.2  # تكتمل الحركة هنا، ثم يثبت الإطار
SFX = dict(badge=.25, thud=.75, print0=1.0, print1=2.6, strike=2.8, pop=3.3)

ANIM_JS = """<script>
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)), seg=(t,a,b)=>cl((t-a)/(b-a));
const eo=x=>1-Math.pow(1-x,3), back=x=>{const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
function setT(t){
  const S=__SFX__;
  $$('.client,.ours').forEach((e,i)=>{const p=eo(seg(t,S.badge+i*.12,S.badge+.45+i*.12));e.style.opacity=p;e.style.transform=`translateY(${(1-p)*-40}px)`});
  const st=$('.st'); if(st){const d=seg(t,S.thud-.35,S.thud);const sc=1+(2.6-1)*(1-eo(d));
    st.style.opacity=d>0?1:0; st.style.transform=`rotate(${14-(1-eo(d))*40}deg) scale(${(st.dataset.k||1)*sc})`;}
  const rc=$('.rc'), p=eo(seg(t,S.print0,S.print1));
  rc.style.opacity=t>=S.print0?1:0; rc.style.clipPath=`inset(0 0 ${(1-p)*100}% 0)`; rc.style.transform=`translateY(${(1-p)*-50}px)`;
  const sk=$('.old i'); if(sk) sk.style.transform=`scaleX(${eo(seg(t,S.strike,S.strike+.4))})`;
  const nw=$('.new'); nw.style.transformOrigin='left center'; nw.style.transform=`scale(${t<S.pop?0.001:back(seg(t,S.pop,S.pop+.5))})`;
  const sm=$('.seam'); sm.style.transform=`scaleX(${eo(seg(t,0,.6))})`; sm.style.transformOrigin='right';
}
</script>"""

def reel_overlay_doc(o):
    d, W, H = tall(o, None, "reel", hole=True)
    mh = 740
    d = d.replace("<div class='ground'></div>", f"<div class='ground' style='top:{mh}px'></div>", 1)
    d = d.replace("transform:rotate(14deg) scale(", "transform:rotate(14deg) scale(", 1)
    import re
    m = re.search(r"class='st' style='[^']*scale\(([\d.]+)\)", d)
    if m: d = d.replace("<div class='st' ", f"<div class='st' data-k='{m.group(1)}' ", 1)
    return d.replace("</body>", ANIM_JS.replace("__SFX__", json.dumps(SFX)) + "</body>"), W, H

async def overlay_frames(o, fdir):
    d, W, H = reel_overlay_doc(o)
    t = fdir / "_overlay.html"; t.write_text(d, encoding="utf-8")
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": W, "height": H})
        await pg.goto(t.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
        for i in range(int(ANIM_T * FPS) + 1):
            await pg.evaluate(f"setT({i / FPS})")
            await pg.screenshot(path=str(fdir / f"o{i:04d}.png"), omit_background=True)
        await b.close()

def probe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return 0.0

def has_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(r.stdout.strip())

def photos_to_video(imgs, out, per=2.6):
    """صور العميل → فيديو بحركة تقريب بطيئة (1080×740)."""
    parts = []
    for i, im in enumerate(imgs):
        seg = out.parent / f"_ph{i}.mp4"
        n = int(per * FPS)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(im), "-vf",
                        f"scale=2160:1480:force_original_aspect_ratio=increase,crop=2160:1480,"
                        f"zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x740:fps={FPS}",
                        "-t", str(per), "-pix_fmt", "yuv420p", str(seg)], check=True)
        parts.append(seg)
    lst = out.parent / "_ph.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)], check=True)
    return out

SR = 44100
def _env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-t / d)
def sfx_track(path, dur, bed=True):
    rng = np.random.default_rng(7)
    out = np.zeros(int((dur + .5) * SR))
    def put(sig, at):
        i = int(at * SR); out[i:i + len(sig)] += sig[:max(0, len(out) - i)]
    n = int(.45 * SR); t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * (55 + 70 * np.exp(-t * 30)) * t) * _env(n, .001, .12) + rng.standard_normal(n) * _env(n, .0005, .012) * .5
    put(thud, SFX["thud"])
    tt = SFX["print0"]
    while tt < SFX["print1"]:
        m = int(.03 * SR); x = rng.standard_normal(m); x = x - np.convolve(x, np.ones(6) / 6, "same")
        put(x * _env(m, .0005, .006) * .35, tt); tt += .038 + rng.uniform(-.006, .006)
    m = int(.42 * SR); ts = np.arange(m) / SR
    put(np.convolve(rng.standard_normal(m), np.ones(12) / 12, "same") * np.sin(np.pi * ts / ts[-1]) ** 2 * .5, SFX["strike"] - .05)
    m = int(.16 * SR); ts = np.arange(m) / SR
    put(np.sin(2 * np.pi * (320 + 2600 * ts) * ts) * _env(m, .002, .05) * .55, SFX["pop"])
    if bed:
        b = .5
        while b < dur - .3:
            m = int(.28 * SR); ts = np.arange(m) / SR
            if not (SFX["print0"] < b < SFX["print1"]):
                put(np.sin(2 * np.pi * (48 + 90 * np.exp(-ts * 40)) * ts) * _env(m, .001, .09) * .45, b)
            h = int(.05 * SR); x = rng.standard_normal(h); put((x - np.convolve(x, np.ones(3) / 3, "same")) * _env(h, .0005, .01) * .07, b + .25)
            b += .5
    f = int(.6 * SR); out[-f:] *= np.linspace(1, 0, f)
    out = out / (np.abs(out).max() + 1e-9) * .89
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

def build_reel(o, out_mp4, max_dur=20.0):
    out_mp4 = pathlib.Path(out_mp4).resolve(); work = out_mp4.parent / "_reel_work"
    shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    vids = [m for m in o.get("media", []) if is_video(m)]
    imgs = [m for m in o.get("media", []) if not is_video(m)] + [it["media"] for it in o.get("items", []) if it.get("media")]
    if vids: src = pathlib.Path(vids[0]).resolve(); client_audio = has_audio(src)
    elif imgs: src = photos_to_video(list(dict.fromkeys(imgs))[:6], work / "photos.mp4"); client_audio = False
    else: raise SystemExit("لا توجد وسائط للعميل")
    dur = max(8.0, min(max_dur, probe_dur(src) or 8.0))
    asyncio.run(overlay_frames(o, work))
    wav = work / "sfx.wav"; sfx_track(wav, dur, bed=not client_audio)
    vf = (f"[0:v]scale=1080:740:force_original_aspect_ratio=increase,crop=1080:740,setsar=1,fps={FPS}[v];"
          f"color=c=0x15112B:s=1080x1920:r={FPS}:d={dur}[bg];[bg][v]overlay=0:0[b];"
          f"[1:v]tpad=stop_mode=clone:stop_duration={dur},fps={FPS}[o];[b][o]overlay=0:0:shortest=0,trim=duration={dur}[out]")
    if client_audio:
        af = f"[0:a]volume=0.55,apad[ca];[2:a]volume=1.0[sx];[ca][sx]amix=inputs=2:duration=longest,atrim=duration={dur},afade=t=out:st={dur-.6}:d=.6[aout]"
    else:
        af = f"[2:a]atrim=duration={dur}[aout]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(src),
                    "-framerate", str(FPS), "-i", str(work / "o%04d.png"), "-i", str(wav),
                    "-filter_complex", vf + ";" + af, "-map", "[out]", "-map", "[aout]", "-t", str(dur),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_mp4)], check=True)
    cover = out_mp4.with_suffix(".cover.jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-sseof", "-0.5", "-i", str(out_mp4), "-frames:v", "1", "-q:v", "2", str(cover)], check=True)
    shutil.rmtree(work, ignore_errors=True)
    return str(out_mp4), str(cover)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("offer"); ap.add_argument("outdir")
    ap.add_argument("--formats", default="post,story,carousel")
    a = ap.parse_args()
    o = json.loads(pathlib.Path(a.offer).read_text())
    out = pathlib.Path(a.outdir).resolve(); out.mkdir(parents=True, exist_ok=True)
    fm = a.formats.split(",")
    res = build_stills(o, out, fm)
    if "reel" in fm: res += list(build_reel(o, out / "reel.mp4"))
    print("\n".join(res))


