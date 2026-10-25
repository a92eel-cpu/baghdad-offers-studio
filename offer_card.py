"""بطاقة عرض واحد — منشور 4:5 + ستوري 9:16 (JPG) للناشر الخاص.

الاستخدام:
  python3 offer_card.py card.json OUTDIR
card.json:
  merchant, category (مطاعم/ملابس/…), art (اختياري: نوع الرسمة من illus.py), handle (بدون @، فقط إذا تأكدنا منه),
  pct, title, area, where (مثل «تطبيق Baly»), seen_on (نص عربي), valid_until (نص عربي، اختياري)
المخرجات: post.jpg و story.jpg
"""
import json, sys, pathlib, asyncio
from studio import doc, esc, our_badge
from illus import svg, kind_for

CCSS = """
.art{position:absolute;left:50%;transform:translateX(-50%);border-radius:50%;background:var(--ink-2);
  box-shadow:0 0 0 10px rgba(212,255,58,.18);display:flex;align-items:center;justify-content:center}
.card{position:absolute;left:60px;right:60px;background:var(--paper);border-radius:36px;padding:44px 52px}
.nm{font-family:Taj;font-weight:800;font-size:58px;line-height:1.2}
.hd{font-weight:800;font-size:34px;color:var(--coral);direction:ltr;text-align:right;margin-top:4px}
.pct{display:flex;align-items:baseline;gap:18px;margin:22px 0 4px}
.pct b{font-family:Alex;font-weight:900;font-size:150px;line-height:.95;color:var(--coral)}
.pct span{font-family:Alex;font-weight:900;font-size:56px}
.ttl{font-weight:800;font-size:38px;line-height:1.4}
.dash{border-top:4px dashed rgba(21,17,43,.25);margin:26px -6px}
.kv{display:grid;grid-template-columns:auto 1fr;gap:12px 26px;font-size:32px}
.kv span{font-weight:500;color:var(--muted)} .kv b{font-weight:800}
.tagme{position:absolute;left:60px;right:60px;text-align:center;font-family:Alex;font-weight:900;font-size:40px;color:var(--lime);direction:ltr}
.fine{position:absolute;left:60px;right:60px;text-align:center;font-weight:700;font-size:26px;color:rgba(245,240,228,.7)}
"""

def art(c, top, d):
    k = c.get("art") or kind_for(c.get("merchant"), c.get("category", "مطاعم"))
    return f"<div class='art' style='top:{top}px;width:{d}px;height:{d}px'>{svg(k, int(d*.78))}</div>"

def body(c):
    hd = f"<div class='hd'>@{esc(c['handle'])}</div>" if c.get("handle") else ""
    rows = [("المنطقة", c.get("area")), ("وين", c.get("where")), ("لغاية", c.get("valid_until")), ("ظهر يوم", c.get("seen_on"))]
    kv = "".join(f"<span>{k}</span><b>{esc(v)}</b>" for k, v in rows if v)
    return (f"<div class='nm'>{esc(c['merchant'])}</div>{hd}"
            f"<div class='pct'><b>{int(c['pct'])}%</b><span>خصم</span></div>"
            f"<div class='ttl'>{esc(c.get('title'))}</div><div class='dash'></div><div class='kv'>{kv}</div>")

def post(c):
    return doc(f"<style>{CCSS}</style>" + our_badge(60, 56) + art(c, 110, 330) +
               f"<div class='card' style='top:470px'>{body(c)}</div>"
               "<div class='fine' style='bottom:36px'>الخصم مثل ما ظهر بالمصدر، تأكد قبل لا تطلب</div>", 1080, 1350)

def story(c):
    tag = f"@{esc(c['handle'])} · " if c.get("handle") else ""
    return doc(f"<style>{CCSS}</style>" + our_badge(60, 240) + art(c, 300, 380) +
               f"<div class='card' style='top:720px'>{body(c)}</div>"
               f"<div class='tagme' style='top:1440px'>{tag}@baghdad_offers</div>"
               "<div class='fine' style='top:1520px'>الخصم مثل ما ظهر بالمصدر، تأكد قبل لا تطلب</div>", 1080, 1920)

async def shoot2(pages, out):
    # roundup.shoot يفترض 1080×1350؛ هنا نحتاج قياسين
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, (html, W, H) in pages.items():
            t = out / f"_{name}.html"; t.write_text(html, encoding="utf-8")
            pg = await b.new_page(viewport={"width": W, "height": H})
            await pg.goto(t.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
            await pg.screenshot(path=str(out / f"{name}.jpg"), type="jpeg", quality=92); await pg.close(); t.unlink()
        await b.close()

if __name__ == "__main__":
    c = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
    asyncio.run(shoot2({"post": (post(c), 1080, 1350), "story": (story(c), 1080, 1920)}, out))
    print(out / "post.jpg", out / "story.jpg", sep="\n")
