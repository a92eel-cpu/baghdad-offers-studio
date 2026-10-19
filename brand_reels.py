"""ريلز تعريفية لصفحة «عروض بغداد» — نص متحرك بهوية الاستوديو.

الاستخدام:  python3 brand_reels.py OUTDIR [intro,merchants,trust]
كل النص بين y=290 و y=1250، والثلث السفلي يترك 230px يميناً (مناطق أمان الريلز).
"""
import sys, json, pathlib, asyncio, subprocess, shutil, wave
import numpy as np
from playwright.async_api import async_playwright
from studio import CSS, MARK, FPS, SR, _env

HANDLE = "baghdad_offers"

ENGINE = """<script>
const cl=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)), seg=(t,a,b)=>cl((t-a)/(b-a));
const eo=x=>1-Math.pow(1-x,3), back=x=>{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
function setT(t){
  document.querySelectorAll('.sc').forEach(s=>{
    const a=+s.dataset.a, b=+s.dataset.b, last=s.hasAttribute('data-last');
    const out=last?0:eo(seg(t,b-.35,b));
    s.style.display=(t>=a&&t<b+(last?99:0))?'block':'none';
    s.style.opacity=1-out; s.style.transform=`translateY(${-out*60}px)`;
    s.querySelectorAll('.e').forEach(e=>{
      const d=a+(+e.dataset.d||0), k=e.dataset.k||'up', p=seg(t,d,d+.5);
      if(k==='pop'){e.style.opacity=p>0?1:0;e.style.transform=`scale(${p>0?back(p):.001}) rotate(${e.dataset.r||0}deg)`}
      else if(k==='wipe'){e.style.clipPath=`inset(0 0 0 ${(1-eo(p))*100}%)`}
      else{e.style.opacity=eo(p);e.style.transform=`translateY(${(1-eo(p))*70}px)`}
    });
  });
  const sm=document.querySelector('.bar'); if(sm) sm.style.transform=`scaleX(${cl(t/__DUR__)})`;
  const mk=document.querySelector('.spin'); if(mk) mk.style.transform=`rotate(${t*40}deg)`;
}
</script>"""

EXTRA = """
.sc{position:absolute;inset:0;display:none}
.stack{position:absolute;top:400px;bottom:640px;left:65px;right:65px;display:flex;flex-direction:column;justify-content:center;align-items:stretch;gap:34px}
.e{position:relative}
.kick{align-self:flex-start;font-family:Alex;font-weight:800;font-size:40px;color:var(--ink);background:var(--lime);border-radius:999px;padding:10px 34px}
.big{font-family:Alex;font-weight:900;font-size:124px;line-height:1.22;color:var(--paper);text-wrap:balance}
.big em{font-style:normal;color:var(--lime)}
.mid{font-family:Taj;font-weight:700;font-size:58px;line-height:1.45;color:var(--paper);text-wrap:balance}
.h2{font-family:Alex;font-weight:900;font-size:80px;line-height:1.3;color:var(--paper);text-wrap:balance}
.row{display:flex;align-items:center;gap:28px;background:var(--paper);border-radius:30px;padding:28px 34px}
.row .ck{flex:none;width:80px;height:80px;border-radius:50%;background:var(--ink);color:var(--lime);display:flex;align-items:center;justify-content:center;font-family:Alex;font-weight:900;font-size:44px}
.row span{font-family:Alex;font-weight:800;font-size:52px;line-height:1.3;color:var(--ink)}
.pill{align-self:flex-start;font-family:Alex;font-weight:900;font-size:66px;direction:ltr;color:var(--ink);background:var(--lime);border-radius:999px;padding:16px 50px}
.free{font-family:Alex;font-weight:900;font-size:290px;line-height:1.05;color:var(--lime)}
.bigmark{align-self:flex-start;width:340px;height:340px}
.bigmark svg{width:100%;height:100%}
.stampx{align-self:center;width:360px;height:360px;border-radius:50%;background:var(--coral);box-shadow:0 0 0 14px var(--ink),0 0 0 22px var(--coral);margin:30px 0;
  display:flex;align-items:center;justify-content:center;font-family:Alex;font-weight:900;font-size:92px;color:var(--paper);text-align:center;line-height:1.05}
.bar{position:absolute;left:0;right:0;top:0;height:12px;background:var(--lime);transform-origin:right}
.foot{position:absolute;left:65px;top:300px}
"""

def badge():
    return (f"<div class='ours foot'><span class='spin' style='display:inline-flex;width:54px;height:54px'>{MARK}</span>"
            f"<span>عروض بغداد</span></div>")

def check_rows(items, top, d0=.5, step=.45, ck="✓"):
    out = ""
    for i, t in enumerate(items):
        mark = ck if ck else f"{'١٢٣٤٥'[i]}"
        out += (f"<div class='e row' data-d='{d0 + i*step:.2f}' >"
                f"<div class='ck'>{mark}</div><span>{t}</span></div>")
    return out

def follow(a, b):
    return f"""<section class='sc' data-a='{a}' data-b='{b}' data-last><div class='stack'>
      <div class='e bigmark' data-k='pop' data-r='-8'>{MARK}</div>
      <div class='e h2' data-d='.35'>تابعنا وخلّي<br>العرض يوصلك</div>
      <div class='e pill' data-k='pop' data-d='.9'>@{HANDLE}</div>
      <div class='e mid' data-d='1.3' style='color:var(--lime)'>وصلك العرض.</div></div></section>"""

REELS = {
  "intro": dict(dur=13.5, cuts=[0, 3.2, 6.6, 10.6], body=lambda: f"""
    <section class='sc' data-a='0' data-b='3.2'><div class='stack'>
      <div class='e kick' data-d='.1'>سؤال سريع</div>
      <div class='e big' data-d='.35'>تدوّر على <em>عرض حقيقي</em> ببغداد؟</div></div></section>
    <section class='sc' data-a='3.2' data-b='6.6'><div class='stack'>
      <div class='e bigmark' data-k='pop' data-r='-8'>{MARK}</div>
      <div class='e big' data-d='.3'>عروض <em>بغداد</em></div>
      <div class='e mid' data-d='.7'>نجمعلك عروض محلات بغداد بمكان واحد</div></div></section>
    <section class='sc' data-a='6.6' data-b='10.6'><div class='stack'>
      <div class='e h2' data-d='.05'>كل عرض ننشره بيه:</div>
      {check_rows(['اسم المحل وحسابه', 'السعر قبل وهسه', 'المنطقة', 'لغاية شوكت'], 500, .4, .55)}</div></section>
    {follow(10.6, 13.5)}"""),

  "merchants": dict(dur=14.0, cuts=[0, 3.2, 6.8, 10.9], body=lambda: f"""
    <section class='sc' data-a='0' data-b='3.2'><div class='stack'>
      <div class='e kick' data-d='.1'>لأصحاب المحلات</div>
      <div class='e big' data-d='.35'>عندك محل ببغداد <em>وعندك عرض؟</em></div></div></section>
    <section class='sc' data-a='3.2' data-b='6.8'><div class='stack'>
      <div class='e mid' data-d='.05'>ننشر عرضك على صفحتنا</div>
      <div class='e free' data-k='pop' data-d='.5'>مجاناً</div>
      <div class='e mid' data-d='1.1'>بالفترة الأولى</div></div></section>
    <section class='sc' data-a='6.8' data-b='10.9'><div class='stack'>
      <div class='e h2' data-d='.05'>بثلاث خطوات:</div>
      {check_rows(['ترسل العرض من الرابط بالبايو', 'نسوّيله تصميم', 'ننشره ونسوّيلك تاك'], 500, .4, .6, ck=None)}</div></section>
    <section class='sc' data-a='10.9' data-b='14' data-last><div class='stack'>
      <div class='e bigmark' data-k='pop' data-r='-8'>{MARK}</div>
      <div class='e h2' data-d='.35'>الرابط بالبايو</div>
      <div class='e pill' data-k='pop' data-d='.8'>@{HANDLE}</div>
      <div class='e mid' data-d='1.2' style='color:var(--lime)'>وصلك العرض.</div></div></section>"""),

  "trust": dict(dur=14.0, cuts=[0, 3.2, 7.4, 10.9], body=lambda: f"""
    <section class='sc' data-a='0' data-b='3.2'><div class='stack'>
      <div class='e kick' data-d='.1'>شلون نشتغل</div>
      <div class='e big' data-d='.35'>مو كل عرض نلگاه <em>ننشره</em></div></div></section>
    <section class='sc' data-a='3.2' data-b='7.4'><div class='stack'>
      {check_rows(['نتأكد إن العرض ساري هسه', 'ناخذ إذن المحل قبل النشر', 'نكتب السعر والتاريخ بالضبط'], 380, .2, .7)}</div></section>
    <section class='sc' data-a='7.4' data-b='10.9'><div class='stack'>
      <div class='e h2' data-d='.05'>وقبل ما يخلص العرض…</div>
      <div class='e stampx' data-k='pop' data-r='12' data-d='.6'>آخر<br>يوم</div>
      <div class='e mid' data-d='1.3'>نذكّرك بآخر يوم حتى ما يفوتك</div></div></section>
    {follow(10.9, 14.0)}"""),
}

def page(name):
    r = REELS[name]
    js = ENGINE.replace("__DUR__", str(r["dur"]))
    return (f"<!doctype html><html lang='ar' dir='rtl'><head><meta charset='utf-8'><style>{CSS}{EXTRA}</style></head>"
            f"<body><div class='cv' style='width:1080px;height:1920px'><div class='ground'></div>{r['body']()}"
            f"{badge()}<div class='bar'></div></div>{js}</body></html>")

async def frames(name, fdir):
    t = fdir / "_p.html"; t.write_text(page(name), encoding="utf-8")
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.goto(t.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
        for i in range(int(REELS[name]["dur"] * FPS)):
            await pg.evaluate(f"setT({i / FPS})")
            await pg.screenshot(path=str(fdir / f"f{i:04d}.jpg"), type="jpeg", quality=92)
        await b.close()

def audio(path, dur, cuts):
    rng = np.random.default_rng(11); out = np.zeros(int((dur + .5) * SR))
    def put(sig, at):
        i = int(at * SR); out[i:i + len(sig)] += sig[:max(0, len(out) - i)]
    b = 0.0
    while b < dur - .2:  # نبض هادئ 120bpm
        m = int(.28 * SR); ts = np.arange(m) / SR
        put(np.sin(2 * np.pi * (48 + 90 * np.exp(-ts * 40)) * ts) * _env(m, .001, .09) * .5, b)
        h = int(.05 * SR); x = rng.standard_normal(h)
        put((x - np.convolve(x, np.ones(3) / 3, "same")) * _env(h, .0005, .01) * .08, b + .25)
        b += .5
    for c in cuts:  # سويش + بوب عند كل مشهد
        m = int(.35 * SR); ts = np.arange(m) / SR
        put(np.convolve(rng.standard_normal(m), np.ones(10) / 10, "same") * np.sin(np.pi * ts / ts[-1]) ** 2 * .35, max(0, c - .1))
        m = int(.16 * SR); ts = np.arange(m) / SR
        put(np.sin(2 * np.pi * (320 + 2600 * ts) * ts) * _env(m, .002, .05) * .45, c + .35)
    f = int(.8 * SR); out[-f:] *= np.linspace(1, 0, f)
    out = out / (np.abs(out).max() + 1e-9) * .85
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())

def build(name, outdir):
    r = REELS[name]; work = outdir / f"_{name}"; shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    asyncio.run(frames(name, work)); audio(work / "a.wav", r["dur"], r["cuts"])
    mp4 = outdir / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(work / "f%04d.jpg"),
                    "-i", str(work / "a.wav"), "-t", str(r["dur"]), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
                    "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(mp4)], check=True)
    cover = outdir / f"{name}.cover.jpg"   # الغلاف = إطار العنوان بعد اكتمال الحركة
    shutil.copy(work / f"f{int(1.6 * FPS):04d}.jpg", cover)
    shutil.rmtree(work)
    return mp4, cover

if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1]).resolve(); out.mkdir(parents=True, exist_ok=True)
    names = sys.argv[2].split(",") if len(sys.argv) > 2 else list(REELS)
    for n in names: print(*build(n, out))
