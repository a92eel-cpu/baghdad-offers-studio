"""ناشر «عروض بغداد» الخاص — إنستغرام فقط، بدون Metricool.

يشتغل من GitHub Actions كل 10 دقائق (.github/workflows/publish.yml):
  1. يأخذ أقدم ملف بـ queue/pending/*.json وقته (not_before) حان.
  2. ينشر الصورة منشوراً (مع تاك المحل user_tags)، ثم نفس الصورة ستوري.
  3. ينقل الملف إلى queue/done/ مع أرقام المنشورات، أو يسجل الخطأ.

ملف الطابور:
  {"id": "...", "not_before": "2026-10-26T10:00:00+03:00",
   "image_url": "https://raw.githubusercontent.com/.../post.jpg",
   "story_url": "https://raw.githubusercontent.com/.../story.jpg",
   "caption": "...", "user_tags": [{"username": "shop", "x": 0.5, "y": 0.3}]}

الأسرار (GitHub → Settings → Secrets → Actions):
  IG_TOKEN    توكن طويل الأمد لحساب baghdad_offers
  IG_USER_ID  رقم الحساب
  IG_HOST     اختياري: graph.instagram.com (افتراضي، دخول إنستغرام) أو graph.facebook.com (دخول فيسبوك)
"""
import json, os, sys, time, pathlib, datetime, subprocess, urllib.request, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
PENDING, DONE = ROOT / "queue/pending", ROOT / "queue/done"
TOKEN, USER = os.environ.get("IG_TOKEN"), os.environ.get("IG_USER_ID")
HOST = os.environ.get("IG_HOST") or "graph.instagram.com"
API = f"https://{HOST}/v21.0"


def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    req = urllib.request.Request(url if method == "POST" else f"{url}?{data.decode()}",
                                 data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:400]}")


def wait_ready(cid):
    for _ in range(30):
        st = call("GET", cid, fields="status_code").get("status_code")
        if st == "FINISHED": return
        if st in ("ERROR", "EXPIRED"): raise RuntimeError(f"container {cid} {st}")
        time.sleep(4)
    raise RuntimeError(f"container {cid} timeout")


def publish(**params):
    cid = call("POST", f"{USER}/media", **params)["id"]
    wait_ready(cid)
    return call("POST", f"{USER}/media_publish", creation_id=cid)["id"]


def quota_left():
    try:
        d = call("GET", f"{USER}/content_publishing_limit", fields="config,quota_usage")["data"][0]
        return d["config"]["quota_total"] - d["quota_usage"]
    except Exception as e:
        print("quota check failed:", e); return 2


def due():
    now = datetime.datetime.now(datetime.timezone.utc)
    items = []
    for f in sorted(PENDING.glob("*.json")):
        j = json.loads(f.read_text())
        nb = datetime.datetime.fromisoformat(j.get("not_before", "2000-01-01T00:00:00+00:00"))
        if nb <= now: items.append((nb, f, j))
    return [x[1:] for x in sorted(items, key=lambda x: x[0])]


def next_time():
    ts = []
    for f in PENDING.glob("*.json"):
        j = json.loads(f.read_text())
        ts.append(datetime.datetime.fromisoformat(j.get("not_before", "2000-01-01T00:00:00+00:00")))
    return min(ts) if ts else None


def publish_one(f, j):
    res = {"published_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        p = dict(image_url=j["image_url"], caption=j.get("caption", ""))
        if j.get("user_tags"): p["user_tags"] = json.dumps(j["user_tags"])
        try:
            res["post_id"] = publish(**p)
        except RuntimeError as e:  # تاك غلط (حساب خاص/غير موجود) ما يوقف العرض
            if "user_tags" in p:
                res["tag_error"] = str(e); p.pop("user_tags"); res["post_id"] = publish(**p)
            else: raise
        if j.get("story_url"):
            res["story_id"] = publish(image_url=j["story_url"], media_type="STORIES")
    except Exception as e:
        res["error"] = str(e); print(f.name, "ERROR", e)
        if "post_id" not in res:
            j["attempts"] = j.get("attempts", 0) + 1
            if j["attempts"] < 2:
                j["last_error"] = str(e); f.write_text(json.dumps(j, ensure_ascii=False, indent=1)); return
    j["result"] = res
    (DONE / f.name).write_text(json.dumps(j, ensure_ascii=False, indent=1)); f.unlink()
    print(f.name, res, flush=True)


def save_state():
    """يحفظ الطابور بالمستودع بعد كل نشر، حتى ما يتكرر عرض إذا انقطع التشغيل."""
    if os.environ.get("GIT_PUSH") != "1": return
    sh = lambda *a: subprocess.run(a, cwd=ROOT, capture_output=True, text=True)
    sh("git", "add", "-A", "queue")
    if sh("git", "diff", "--cached", "--quiet").returncode == 0: return
    sh("git", "commit", "-m", "نشر: تحديث الطابور")
    for _ in range(3):
        sh("git", "pull", "--rebase", "-q", "origin", "main")
        if sh("git", "push", "-q", "origin", "HEAD:main").returncode == 0: return
        time.sleep(3)


def main():
    """يبقى شغّال لحد MAX_MINUTES: ينشر كل عرض بوقته بالضبط (كرون GitHub يتأخر أحياناً)."""
    if not (TOKEN and USER):
        print("IG_TOKEN / IG_USER_ID ناقصة — ما نشرت شي."); return 0
    DONE.mkdir(parents=True, exist_ok=True)
    end = time.time() + 60 * float(os.environ.get("MAX_MINUTES", "25"))
    while time.time() < end:
        items = due()
        if items:
            if quota_left() < 2:
                print("حد إنستغرام اليومي خلص — نكمل بالتشغيل الجاي."); break
            publish_one(*items[0]); save_state()
            if due():  # متأخرين: خلّ 10 دقائق بين كل عرضين
                time.sleep(min(600, max(0, end - time.time())))
            continue
        nt = next_time()
        if not nt: break
        wait = (nt - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
        if wait > end - time.time(): break
        time.sleep(max(5, wait))
    return 0


if __name__ == "__main__":
    sys.exit(main())
