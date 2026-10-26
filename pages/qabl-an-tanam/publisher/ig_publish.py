"""ناشر صفحة «قبل أن تنام» — إنستغرام فقط (ريلز + ستوري + منشور صورة).

مبني على ناشر «عروض بغداد» بس بثلاث فروق، تعلّمناها من حظر حساب عروض بغداد يوم 25-26 تشرين الأول:
  1. فاصل أدنى بين أي نشرتين (min_gap_minutes بـ schedule.json) + سقف يومي لكل نوع.
  2. «قاطع»: أول ما إنستغرام يرجّع حظر/كثرة إجراءات، الناشر يوقف 24 ساعة كاملة (state/pause.json)
     وما يعيد المحاولة كل 10 دقايق — المحاولات المتكررة تطوّل الحظر.
  3. يدعم الفيديو: ريلز (REELS) وستوري فيديو.

ملف الطابور queue/pending/<id>.json:
  {"id": "2026-10-28-r1", "kind": "reel" | "story" | "post",
   "not_before": "2026-10-28T22:30:00+03:00",
   "video_url": "...mp4", "cover_url": "...jpg",      # للريل / ستوري فيديو
   "image_url": "...jpg",                             # للمنشور / ستوري صورة
   "caption": "...", "share_to_feed": true}

الأسرار: IG_TOKEN, IG_USER_ID, و IG_HOST اختياري (graph.instagram.com افتراضياً).
DRY_RUN=1 يطبع اللي راح ينشره بدون ما يتصل بإنستغرام.
"""
import json, os, sys, time, pathlib, datetime, subprocess, urllib.request, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
PENDING, DONE, STATE = ROOT / "queue/pending", ROOT / "queue/done", ROOT / "state"
SCHED = json.loads((ROOT / "schedule.json").read_text())
TOKEN, USER = os.environ.get("IG_TOKEN"), os.environ.get("IG_USER_ID")
HOST = os.environ.get("IG_HOST") or "graph.instagram.com"
API = f"https://{HOST}/v21.0"
DRY = os.environ.get("DRY_RUN") == "1"
UTC = datetime.timezone.utc
BLOCK_SIGNS = ("too many actions", "2207051", "action is blocked", "request limit reached", "\"code\":4", "\"code\":17", "\"code\":32")


def now():
    return datetime.datetime.now(UTC)


def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    req = urllib.request.Request(url if method == "POST" else f"{url}?{data.decode()}",
                                 data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:500]}")


def wait_ready(cid, video=False):
    for _ in range(90 if video else 30):  # الفيديو يحتاج وقت معالجة أطول
        st = call("GET", cid, fields="status_code").get("status_code")
        if st == "FINISHED": return
        if st in ("ERROR", "EXPIRED"): raise RuntimeError(f"container {cid} {st}")
        time.sleep(5)
    raise RuntimeError(f"container {cid} timeout")


def publish(video=False, **params):
    cid = call("POST", f"{USER}/media", **params)["id"]
    wait_ready(cid, video)
    return call("POST", f"{USER}/media_publish", creation_id=cid)["id"]


# ---------- الحالة: القاطع + العدّادات ----------
def load(name, default):
    f = STATE / name
    return json.loads(f.read_text()) if f.exists() else default


def save(name, obj):
    STATE.mkdir(exist_ok=True)
    (STATE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1))


def paused():
    p = load("pause.json", {})
    until = p.get("until")
    return until and datetime.datetime.fromisoformat(until) > now()


def trip(reason):
    until = now() + datetime.timedelta(hours=24)
    save("pause.json", {"until": until.isoformat(), "reason": reason[:300]})
    print("⛔ إنستغرام قيّد النشر — وقفت 24 ساعة لحد", until.isoformat())


def log():
    return load("log.json", [])


def can_publish(kind):
    entries = [e for e in log() if datetime.datetime.fromisoformat(e["at"]) > now() - datetime.timedelta(hours=24)]
    if entries:
        last = max(datetime.datetime.fromisoformat(e["at"]) for e in entries)
        if (now() - last).total_seconds() < 60 * SCHED.get("min_gap_minutes", 20):
            return False, "gap"
    cap = SCHED.get("max_per_day", {}).get(kind, 99)
    if sum(1 for e in entries if e["kind"] == kind) >= cap:
        return False, "cap"
    return True, ""


def record(kind, item_id):
    entries = [e for e in log() if datetime.datetime.fromisoformat(e["at"]) > now() - datetime.timedelta(days=3)]
    entries.append({"at": now().isoformat(), "kind": kind, "id": item_id})
    save("log.json", entries)


# ---------- الطابور ----------
def items():
    out = []
    for f in PENDING.glob("*.json"):
        j = json.loads(f.read_text())
        out.append((datetime.datetime.fromisoformat(j["not_before"]), f, j))
    return sorted(out, key=lambda x: x[0])


def publish_one(f, j):
    kind = j.get("kind", "post")
    if DRY:
        print("DRY", kind, j["id"], j["not_before"])
        f.unlink(); record(kind, j["id"]); return True
    res = {"published_at": now().isoformat()}
    try:
        if kind == "reel":
            p = dict(media_type="REELS", video_url=j["video_url"], caption=j.get("caption", ""),
                     share_to_feed="true" if j.get("share_to_feed", True) else "false")
            if j.get("cover_url"): p["cover_url"] = j["cover_url"]
            res["media_id"] = publish(video=True, **p)
        elif kind == "story":
            if j.get("video_url"):
                res["media_id"] = publish(video=True, media_type="STORIES", video_url=j["video_url"])
            else:
                res["media_id"] = publish(media_type="STORIES", image_url=j["image_url"])
        else:
            res["media_id"] = publish(image_url=j["image_url"], caption=j.get("caption", ""))
    except Exception as e:
        msg = str(e)
        print(f.name, "ERROR", msg)
        if any(s in msg for s in BLOCK_SIGNS):
            trip(msg)  # ما نحسبها محاولة؛ العنصر يبقى بالطابور للنشر بعد رفع القيد
            return False
        j["attempts"] = j.get("attempts", 0) + 1
        j["last_error"] = msg
        if j["attempts"] < 2:
            f.write_text(json.dumps(j, ensure_ascii=False, indent=1)); return False
        res["error"] = msg
    j["result"] = res
    DONE.mkdir(exist_ok=True)
    (DONE / f.name).write_text(json.dumps(j, ensure_ascii=False, indent=1)); f.unlink()
    if "media_id" in res: record(kind, j["id"])
    print(f.name, res, flush=True)
    return "media_id" in res


def save_state():
    if os.environ.get("GIT_PUSH") != "1": return
    sh = lambda *a: subprocess.run(a, cwd=ROOT, capture_output=True, text=True)
    sh("git", "add", "-A", "queue", "state")
    if sh("git", "diff", "--cached", "--quiet").returncode == 0: return
    sh("git", "commit", "-m", "قبل أن تنام: تحديث الطابور")
    for _ in range(3):
        sh("git", "pull", "--rebase", "-q", "origin", "main")
        if sh("git", "push", "-q", "origin", "HEAD:main").returncode == 0: return
        time.sleep(3)


def whoami():
    me = call("GET", "me", fields="user_id,username,account_type,media_count")
    print("الحساب:", me.get("username"), "| النوع:", me.get("account_type"), "| المنشورات:", me.get("media_count"))
    return str(me.get("user_id") or me.get("id"))


def main():
    global USER
    if not DRY and not TOKEN:
        print("IG_TOKEN ناقص — ما نشرت شي."); return 0
    if not DRY and not USER:
        USER = whoami()
    if paused():
        print("النشر موقوف مؤقتاً:", load("pause.json", {})); return 0
    end = time.time() + 60 * float(os.environ.get("MAX_MINUTES", "25"))
    while time.time() < end and not paused():
        q = items()
        due = [(f, j) for nb, f, j in q if nb <= now()]
        if due:
            f, j = due[0]
            # عنصر فات وقته بأكثر من 3 ساعات (مثلاً بعد حظر) ما ننشره بنص النهار — نأجله لليلة الجاية بنفس الساعة
            late = now() - datetime.datetime.fromisoformat(j["not_before"])
            if late > datetime.timedelta(hours=3):
                nb = datetime.datetime.fromisoformat(j["not_before"])
                while nb < now(): nb += datetime.timedelta(days=1)
                j["not_before"] = nb.isoformat(); f.write_text(json.dumps(j, ensure_ascii=False, indent=1))
                print("أجّلت", j["id"], "إلى", j["not_before"]); save_state(); continue
            ok, why = can_publish(j.get("kind", "post"))
            if not ok:
                print("انتظار:", why, j["id"])
                if why == "gap" and end - time.time() > 120:
                    time.sleep(60); continue  # ننتظر الفاصل ضمن نفس التشغيل
                break
            publish_one(f, j); save_state()
            continue
        if not q: break
        wait = (q[0][0] - now()).total_seconds()
        if wait > end - time.time(): break
        time.sleep(max(5, wait))
    return 0


if __name__ == "__main__":
    sys.exit(main())
