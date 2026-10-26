"""يحوّل محتوى ليلة وحدة إلى عناصر بالطابور حسب schedule.json.

  python3 publisher/enqueue.py 2026-10-28

يقرأ content/<date>/night.json:
  {"reels":   [{"id": "r1", "video": "media/2026-10-28/r1.mp4", "cover": "media/2026-10-28/r1.jpg", "caption": "..."}],
   "stories": [{"type": "opening", "image": "media/2026-10-28/s-opening.jpg"}, ...]}

ريلز المرحلة الحالية تاخذ أوقات reels_phase<N> بالترتيب، والستوريات تاخذ وقت نوعها.
الأوقات بعد منتصف الليل (00:30) تنحسب على اليوم التالي — لأن «الليلة» وحدة.
روابط الوسائط: الصور من raw.githubusercontent، والفيديو من jsDelivr مثبّت على رقم الكومت
(raw يرجّع octet-stream وإنستغرام يحتاج نوع فيديو صحيح).
"""
import json, sys, pathlib, datetime, subprocess, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHED = json.loads((ROOT / "schedule.json").read_text())
REPO = os.environ.get("REPO", "a92eel-cpu/baghdad-offers-studio")
PREFIX = os.environ.get("PREFIX", "pages/qabl-an-tanam/")
BRANCH = os.environ.get("BRANCH", "main")


def sha():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip() or BRANCH
    except Exception:
        return BRANCH


def img(path):  return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{PREFIX}{path}"
def vid(path):  return f"https://cdn.jsdelivr.net/gh/{REPO}@{sha()}/{PREFIX}{path}"


def at(date, hhmm):
    h, m = map(int, hhmm.split(":"))
    d = datetime.date.fromisoformat(date)
    if h < 12: d += datetime.timedelta(days=1)  # بعد منتصف الليل = نفس الليلة
    return f"{d.isoformat()}T{h:02d}:{m:02d}:00{SCHED['tz']}"


def main(date):
    night = json.loads((ROOT / f"content/{date}/night.json").read_text())
    slots = SCHED[f"reels_phase{SCHED.get('phase', 1)}"]
    out = []
    for r, t in zip(night.get("reels", []), slots):
        out.append({"id": f"{date}-{r['id']}", "kind": "reel", "not_before": at(date, t),
                    "video_url": vid(r["video"]), "cover_url": img(r["cover"]) if r.get("cover") else None,
                    "caption": r.get("caption", ""), "share_to_feed": True})
    times = {s["type"]: s["time"] for s in SCHED["stories"]}
    for s in night.get("stories", []):
        e = {"id": f"{date}-s-{s['type']}", "kind": "story", "not_before": at(date, s.get("time") or times[s["type"]])}
        if s.get("video"): e["video_url"] = vid(s["video"])
        else: e["image_url"] = img(s["image"])
        out.append(e)
    for e in out:
        e = {k: v for k, v in e.items() if v is not None}
        (ROOT / f"queue/pending/{e['id']}.json").write_text(json.dumps(e, ensure_ascii=False, indent=1))
        print(e["kind"], e["id"], e["not_before"])


if __name__ == "__main__":
    main(sys.argv[1])
