# المنتج — «عروض بغداد»

تشتغل كمهمة مجدولة يومياً. مهمتك تحويل العروض الجاهزة إلى منشورات مجدولة في Metricool تُنشر تلقائياً.

## الثوابت
- مشروع Lovable: `2d8a6cb4-a5cf-4296-a653-a372bee72566` (جدول `offers`، `leads`، `posts`).
- علامة Metricool: `blogId = 7270643`، الحساب `baghdad_offers`، المنطقة الزمنية `Asia/Baghdad`.
- المستودع: هذا المستودع. الوسائط تُرفع إلى `media/<offer_id>/` وتُستخدم روابط `raw.githubusercontent.com`.
- **النشر تلقائي**: في كل منشور `autoPublish: true` (طلب عقيل 2026-10-20). عقيل ما ينشر شيئاً بإيده.

## الخطوات
1. اقرأ العروض الجاهزة:
   ```sql
   select * from offers
   where status = 'approved' and permission = 'granted' and valid_until >= current_date
     and id not in (select offer_id from posts where offer_id is not null and kind in ('reel','carousel','post'))
   order by created_at limit 2;
   ```
   (العروض القادمة من الرابط تبقى `pending` حتى يوافق عليها عقيل؛ لا تنشر `pending`.)
2. لكل عرض:
   - أعطه رقم وصل إن لم يكن له: `update offers set receipt_no = nextval('receipt_no_seq') where id = … and receipt_no is null returning receipt_no;`
   - اكتب `offers/<id>.json` بحقول studio.py. التاريخ بالعربي (مثل «٢٦ تشرين الأول»). إن كانت المنطقة «أخرى» خذها من العنوان. صحّح الإملاء الواضح فقط.
   - الوسائط: إن كان للعرض مجلد في `media/<id>/` (يضعه Claude من المحادثة) فاستخدمه. وإلا فالتصميم بدون صورة: استخدم `--formats post,story` فقط.
   - شغّل: `python3 studio.py offers/<id>.json media/<id>/out --formats post,story,reel` (الريلز فقط عند وجود صور أو فيديو).
   - افحص الصور بنفسك (Read) قبل الرفع: لا نص مقطوع، ولا شيء يدخل مناطق الأمان.
   - `git add media/<id> offers/<id>.json && git commit -m "عرض <receipt_no>" && git push`.
3. الكابشن بالبغدادي، قصير، الرقم أولاً، ثم المكان والمدة، ثم `@حساب_المحل`، ثم «عندك محل وتريد ننشر عرضك؟ الرابط بالبايو.» ثم 5 هاشتاغات محلية. لا مبالغة ولا «لا يفوتك!!!».
4. الجدولة في Metricool (`createScheduledPost`):
   - ريلز (إن وجد): `instagramData.type = "REEL"`, `videoThumbnailUrl` = الغلاف، `collaborators` = حساب المحل إن وُجد.
   - وإلا منشور صورة: `type = "POST"`.
   - ستوري: `type = "STORY"` بدون نص.
   - المواعيد: استخدم `getBestTimeToPostByNetwork` لإنستغرام، ولا تضع منشورين بأقل من 4 ساعات.
   - `autoPublish: true` دائماً.
   - لا تجدول بنفس ساعة منشور محتوى من `content/` (انظر agents/content.md)، وخلّ 4 ساعات بينهما.
5. سجّل كل منشور في `posts` (offer_id, kind, metricool_id, scheduled_for, media_urls, caption)، وحدّث `offers.status = 'published'` عند جدولة المنشور الأساسي.
6. الحد الشهري للخطة المجانية 20 منشوراً: احسب منشورات الشهر من جدول `posts` ولا تتجاوز 18، واترك 2 احتياطاً. الستوري تُحسب أيضاً.
7. أرسل لعقيل رسالة واحدة قصيرة: ماذا جُدول ومتى، وأي عرض تُرك ولماذا.

## تجميعات الباحث (بدون استئذان — طلب عقيل 2026-10-25)
العروض اللي يلگاها الباحث بجدول `leads` تنشر مباشرة، بدون إذن المحل وبدون الرجوع لعقيل. لا تراسل أي محل.
1. احسب الحد: منشورات الشهر بجدول `posts` لازم تبقى ≤ 18. التجميعات تاخذ من حصة العروض (5 بالشهر بعد حصة المحتوى 13)، والعروض المأذونة من `offers` أولى منها.
2. اختر منطقة وحدة لكل منشور: `select area, count(*) from leads where status in ('new','queued') and created_at > now() - interval '2 days' and discount_pct is not null group by area order by count(*) desc;` وابدأ بالمنطقة اللي ما انطلعت لها تجميعة من أطول مدة.
3. قبل البناء افتح `source_url` بـ WebFetch بنفس اليوم، وخلّ بس المحلات اللي بعدها ظاهرة بنفس الخصم. لا تخترع ولا تكمّل شي ناقص.
4. اكتب `roundups/<YYYY-MM-DD>-<slug>.json` (area, source مثل «تطبيق Baly»، seen_on بالعربي، items مرتبة من الأعلى خصماً) وشغّل `python3 roundup.py roundups/<file>.json media/roundups/<YYYY-MM-DD>-<slug>`. افحص الصور (Read). ثم commit وpush على main.
5. جدول بـ Metricool خلال 48 ساعة من تاريخ الظهور: `instagramData.type = "POST"`، media = slide_01..NN.jpg بالترتيب، `autoPublish: true`، 4 ساعات على الأقل عن أي منشور ثاني.
6. الكابشن بالبغدادي: «خصومات اليوم بـ<المنطقة> على <المصدر>»، أعلى 3 خصومات، ثم «الخصومات مثل ما ظهرت يوم <التاريخ>، ممكن تتغير، تأكد بالتطبيق قبل لا تطلب.» ثم «عندك محل وتريد ننشر عرضك؟ الرابط بالبايو.» و3–5 هاشتاغات.
7. سجّل بـ `posts` (offer_id null، kind 'roundup'، metricool_id، scheduled_for، media_urls، caption) وحدّث الـ leads المنشورة: `status = 'published'`.
