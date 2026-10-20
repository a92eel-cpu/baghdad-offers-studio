"""محتوى النصايح لصفحة «عروض بغداد»: ريلز نصيّة، سلايدات 4:5، ستوري 9:16.

الاستخدام:  python3 tips.py content/2026-10.json media/content [id,id,...]
الملف قائمة عناصر kind = reel | carousel | story (انظر content/2026-10.json).
المخرجات: media/content/<id>/ (reel.mp4 + reel.cover.jpg | slide_01..NN.jpg | story.png)
"""
import sys, json, pathlib, asyncio, subprocess, shutil
from playwright.async_api import async_playwright
from studio import CSS, MARK, FPS
from brand_reels import ENGINE, EXTRA, HANDLE, badge, check_rows, follow, audio

TIP_CSS = """
.rowc span{font-size:48px}
.card{background:var(--paper);border-radius:36px;padding:44px 48px;font-family:Taj;font-weight:700;font-size:50px;line-height:1.5;color:var(--ink);text-wrap:pretty}
.tg{display:inline-block;font-family:Alex;font-weight:800;font-size:30px;background:var(--coral);color:var(--paper);border-radius:999px;padding:8px 28px}
.num{font-family:Alex;font-weight:900;font-size:200px;line-height:1;color:var(--lime)}
.ix2{position:absolute;right:60px;top:66px;font-family:Alex;font-weight:800;font-size:26px;color:var(--ink);background:var(--lime);border-radius:999px;padding:8px 24px}
.swipe{font-family:Alex;font-weight:800;font-size:36px;color:var(--lime)}
"""

def html_doc(body, W, H, js=""):
    return (f"<!doctype html><html lang='ar' dir='rtl'><head><meta charset='utf-8'><style>{CSS}{EXTRA}{TIP_CSS}</style></head>"
            f"<body><div class='cv' style='width:{W}px;height:{H}px'><div class='ground'></div>{body}</div>{js}</body></html>")

def ours(x, y):
    return f"<div class='ours' style='left:{x}px;top:{y}px'>{MARK}<span>عروض بغداد</span></div>"

# ---------- الريل ----------
def reel_page(it):
    dur = 14.4
    ck = it.get("ck", "✓")
    body = f"""
    <section class='sc' data-a='0' data-b='3.4'><div class='stack'>
      <div class='e kick' data-d='.1'>{it['kick']}</div>
      <div class='e big' data-d='.35' style='font-size:116px'>{it['hook']}</div></div></section>
    <section class='sc' data-a='3.4' data-b='8.4'><div class='stack'>
      <div class='e h2' data-d='.05'>{it['rows_title']}</div>
      {check_rows(it['rows'], 0, .45, .6, ck=ck).replace("class='e row'", "class='e row rowc'")}</div></section>
    <section class='sc' data-a='8.4' data-b='11.6'><div class='stack'>
      <div class='e bigmark' data-k='pop' data-r='-8' style='width:200px;height:200px'>{MARK}</div>
      <div class='e h2' data-d='.3'>{it['punch']}</div></div></section>
    {follow(11.6, dur)}"""
    js = ENGINE.replace("__DUR__", str(dur))
    return html_doc(body + badge() + "<div class='bar'></div>", 1080, 1920, js), dur, [0, 3.4, 8.4, 11.6]

async def reel_frames(d, dur, fdir):
    t = fdir / "_p.html"; t.write_text(d, encoding="utf-8")
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.goto(t.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
        for i in range(int(dur * FPS)):
            await pg.evaluate(f"setT({i / FPS})")
            await pg.screenshot(path=str(fdir / f"f{i:04d}.jpg"), type="jpeg", quality=92)
        await b.close()

def build_reel(it, out):
    d, dur, cuts = reel_page(it)
    work = out / "_work"; shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    asyncio.run(reel_frames(d, dur, work)); audio(work / "a.wav", dur, cuts)
    cover = out / "reel.cover.jpg"; shutil.copy(work / f"f{int(1.6 * FPS):04d}.jpg", cover)
    # الكفر مدموج بأول إطارين
    for i in range(2): shutil.copy(cover, work / f"f{i:04d}.jpg")
    mp4 = out / "reel.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(work / "f%04d.jpg"),
                    "-i", str(work / "a.wav"), "-t", str(dur), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
                    "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(mp4)], check=True)
    shutil.rmtree(work)
    return [mp4, cover]

# ---------- السلايدات والستوري ----------
def carousel_pages(it):
    n = len(it["slides"]) + 2
    pages = {}
    pages["slide_01"] = html_doc(f"""{ours(60, 60)}<div class='ix2'>اسحب ←</div>
      <div style='position:absolute;top:300px;left:70px;right:70px;display:flex;flex-direction:column;gap:40px'>
        <div class='kick'>{it['cover_kick']}</div>
        <div class='big' style='font-size:112px'>{it['cover']}</div>
        <div class='swipe'>{''.join('٠١٢٣٤٥٦٧٨٩'[int(c)] for c in str(len(it['slides'])))} نصايح بالسلايدات ←</div></div>""", 1080, 1350)
    digits = "٠١٢٣٤٥٦٧٨٩"
    for i, (h, t) in enumerate(it["slides"], start=1):
        num = "".join(digits[int(c)] for c in str(i))
        pages[f"slide_{i+1:02d}"] = html_doc(f"""{ours(60, 60)}<div class='ix2'>{i+1}/{n}</div>
          <div style='position:absolute;top:230px;left:70px;right:70px;bottom:110px;display:flex;flex-direction:column;justify-content:center;gap:34px'>
            <div class='num'>{num}</div>
            <div class='h2' style='font-size:76px'>{h}</div>
            <div class='card'>{t}</div></div>""", 1080, 1350)
    pages[f"slide_{n:02d}"] = html_doc(f"""<div class='ix2'>{n}/{n}</div>
      <div style='position:absolute;top:200px;left:70px;right:70px;display:flex;flex-direction:column;gap:38px'>
        <div class='bigmark' style='width:260px;height:260px'>{MARK}</div>
        <div class='h2'>احفظ المنشور<br>ودزّه لصديقك</div>
        <div class='pill'>@{HANDLE}</div>
        <div class='mid'>عندك محل وتريد ننشر عرضك؟<br>الرابط بالبايو.</div></div>""", 1080, 1350)
    return pages, 1080, 1350

def story_page(it):
    # النص بين y=250 و y=1580
    return html_doc(f"""
      <div style='position:absolute;top:290px;left:70px;right:70px;bottom:360px;display:flex;flex-direction:column;justify-content:center;gap:46px'>
        <div style='display:flex;gap:18px;align-items:center'><div class='kick'>{it['kick']}</div><span class='tg'>{it.get('tag','')}</span></div>
        <div class='big' style='font-size:110px'>{it['big']}</div>
        <div class='card'>{it['card']}</div></div>
      {ours(360, 1610)}""", 1080, 1920)

async def shoot(pages, W, H, out, ext):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, d in pages.items():
            t = out / f"_{name}.html"; t.write_text(d, encoding="utf-8")
            pg = await b.new_page(viewport={"width": W, "height": H})
            await pg.goto(t.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
            kw = dict(type="jpeg", quality=93) if ext == "jpg" else {}
            await pg.screenshot(path=str(out / f"{name}.{ext}"), **kw); await pg.close(); t.unlink()
        await b.close()
    return sorted(out / f"{k}.{ext}" for k in pages)

def build(it, root):
    out = root / it["id"]; out.mkdir(parents=True, exist_ok=True)
    if it["kind"] == "reel": return build_reel(it, out)
    if it["kind"] == "carousel":
        pages, W, H = carousel_pages(it); return asyncio.run(shoot(pages, W, H, out, "jpg"))
    return asyncio.run(shoot({"story": story_page(it)}, 1080, 1920, out, "png"))

if __name__ == "__main__":
    items = json.loads(pathlib.Path(sys.argv[1]).read_text())
    root = pathlib.Path(sys.argv[2]).resolve()
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    for it in items:
        if only and it["id"] not in only: continue
        print(it["id"], *build(it, root))
