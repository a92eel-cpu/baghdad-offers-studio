"""سلايدات «خصومات اليوم» — تجميعة عروض منطقة وحدة (من جدول leads) بمنشور واحد.

الاستخدام:
  python3 roundup.py roundup.json OUTDIR
roundup.json:
  area, source (مثل «تطبيق Baly»), seen_on (نص عربي: «٢٥ تشرين الأول»),
  items: [{name, pct, title(اختياري)}]   ← مرتبة من الأعلى خصماً
المخرجات: slide_01.jpg … (1080×1350، JPG جودة 92)، أقصى 10 سلايدات.
"""
import json, sys, pathlib, asyncio
from playwright.async_api import async_playwright
from studio import CSS, esc, our_badge, doc

PER = 6
W, H = 1080, 1350

RCSS = """
.big{position:absolute;right:80px;left:80px;font-family:Alex;font-weight:900;color:var(--paper);line-height:1.15}
.lime{color:var(--lime)}
.sub{position:absolute;right:80px;left:80px;font-weight:700;font-size:34px;color:rgba(245,240,228,.8)}
.cnt{position:absolute;right:80px;display:flex;align-items:baseline;gap:14px;background:var(--lime);border-radius:28px;padding:18px 34px}
.cnt b{font-family:Alex;font-weight:900;font-size:92px;line-height:1}
.cnt span{font-weight:800;font-size:34px}
.list{position:absolute;right:60px;left:60px;top:190px;display:flex;flex-direction:column;gap:22px}
.row{background:var(--paper);border-radius:24px;height:150px;display:flex;align-items:center;justify-content:space-between;padding:0 36px 0 24px;gap:24px}
.row .n{font-family:Taj;font-weight:800;font-size:44px;line-height:1.25;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.row .p{flex:none;width:150px;height:110px;border-radius:20px;background:var(--coral);color:var(--paper);display:flex;flex-direction:column;align-items:center;justify-content:center}
.row .p b{font-family:Alex;font-weight:900;font-size:50px;line-height:1}
.row .p span{font-weight:800;font-size:22px}
.hdr{position:absolute;right:60px;top:70px;font-family:Alex;font-weight:900;font-size:40px;color:var(--paper)}
.hdr i{font-style:normal;color:var(--lime)}
.foot{position:absolute;right:60px;left:60px;bottom:52px;display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:24px;color:rgba(245,240,228,.75)}
.note{position:absolute;right:80px;left:80px;background:var(--paper);border-radius:28px;padding:44px 48px;font-size:36px;font-weight:700;line-height:1.6}
.note b{font-family:Alex;font-weight:900}
"""

def d(body): return doc(f"<style>{RCSS}</style>" + body, W, H)

def cover(r, n):
    return d(our_badge(70, 70) +
             f"<div style='position:absolute;right:80px;left:80px;top:280px;display:flex;flex-direction:column;align-items:flex-start;gap:28px'>"
             f"<div style='font-family:Alex;font-weight:900;color:var(--paper);font-size:104px;line-height:1.2'>خصومات اليوم<br>"
             f"<span class='lime'>{esc(r['area'])}</span></div>"
             f"<div style='font-weight:700;font-size:34px;color:rgba(245,240,228,.8)'>حسب {esc(r['source'])} · {esc(r['seen_on'])}</div>"
             f"<div class='cnt' style='position:static;margin-top:30px'><b>{n}</b><span>مطعم بخصم</span></div></div>"
             f"<div class='foot'><span>اسحب ←</span><span>عروض بغداد</span></div>")

def page(r, chunk, i, total):
    rows = "".join(f"<div class='row'><div class='n'>{esc(it['name'])}</div>"
                   f"<div class='p'><b>{int(it['pct'])}%</b><span>خصم</span></div></div>" for it in chunk)
    return d(f"<div class='hdr'>خصومات <i>{esc(r['area'])}</i></div><div class='list'>{rows}</div>"
             f"<div class='foot'><span>{i}/{total}</span><span>حسب {esc(r['source'])} · {esc(r['seen_on'])}</span></div>")

def end(r, total):
    return d(our_badge(70, 70) +
             f"<div class='note' style='top:300px'>الخصومات مثل ما ظهرت على <b>{esc(r['source'])}</b> يوم <b>{esc(r['seen_on'])}</b>.<br>"
             "ما معلن إلها تاريخ انتهاء، وممكن تتغير بأي وقت، فتأكد بالتطبيق قبل لا تطلب.</div>"
             "<div class='big' style='top:860px;font-size:58px'>عندك محل وتريد ننشر عرضك؟</div>"
             "<div class='big lime' style='top:950px;font-size:58px'>الرابط بالبايو</div>"
             f"<div class='foot'><span>{total}/{total}</span><span>عروض بغداد</span></div>")

async def shoot(pages, out):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, html in pages.items():
            t = out / f"_{name}.html"; t.write_text(html, encoding="utf-8")
            pg = await b.new_page(viewport={"width": W, "height": H})
            await pg.goto(t.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
            await pg.screenshot(path=str(out / f"{name}.jpg"), type="jpeg", quality=92); await pg.close(); t.unlink()
        await b.close()

if __name__ == "__main__":
    r = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2]).resolve(); out.mkdir(parents=True, exist_ok=True)
    items = r["items"][:PER * 8]  # غلاف + 8 صفحات + خاتمة = 10
    chunks = [items[k:k + PER] for k in range(0, len(items), PER)]
    total = len(chunks) + 2
    pages = {"slide_01": cover(r, len(items))}
    for j, c in enumerate(chunks, start=2): pages[f"slide_{j:02d}"] = page(r, c, j, total)
    pages[f"slide_{total:02d}"] = end(r, total)
    asyncio.run(shoot(pages, out))
    print("\n".join(sorted(str(out / f"{k}.jpg") for k in pages)))
