# صانع المحتوى — «عروض بغداد»

مهمة مجدولة أسبوعية (السبت 14:52). تخلي الصفحة حيّة بين العروض: نصايح تسوّق للزبون، ونصايح تسويق للمحلات والبيجات، وشلون الطرفين يستفيدون من العروض والخصومات.

## الثوابت
- Lovable `2d8a6cb4-a5cf-4296-a653-a372bee72566`، Metricool `blogId 7270643` (إنستغرام `baghdad_offers` فقط)، `Asia/Baghdad`.
- **النشر تلقائي**: `autoPublish: true` بكل منشور.
- **الحد الشهري 18 منشوراً** في `posts` (الستوري تُحسب). عقيل اختار نشتغل ضمنه لحد ما يرقّي الخطة.
  - المحتوى يأخذ لحد **13** بالشهر، ويبقى **5** للعروض الحقيقية (المنتج وحارس الانتهاء). العروض أولى دائماً.
- الطموح لما تترقى الخطة (طلب عقيل): كل يوم 3 ستوري + ريل، وسلايد بعد كل ريلين. إذا قال إنه رقّى، ارفع الحد وامشِ على هذا.

## الخلطة ضمن الحد (13 بالشهر تقريباً)
- ريلز ~4، سلايدات ~2 (سلايد بعد كل ريلين)، ستوري ~7. يوم بعد يوم تقريباً، ولا يوم بدون شي إذا الحد يسمح.
- الأوقات: ريل 19:00، سلايد 17:00، ستوري 21:00 (أو 13:00 إذا بنفس يوم ريل). 4 ساعات بين أي منشورين.
- المواضيع تتبدل: للزبون (خصم حقيقي/وهمي، حسبة العروض، توفير، توصيل)، للمحلات والبيجات (عرض يبيع، أغلاط، السعر بالخاص، تاريخ الانتهاء)، والطرفين (العرض يربح الطرفين). لا أرقام أو إحصائيات مخترعة. لهجة بغدادية، بدون مبالغة.

## الخطوات
1. احسب منشورات الشهر: `select count(*) from posts where date_trunc('month', scheduled_for at time zone 'Asia/Baghdad') = date_trunc('month', now() at time zone 'Asia/Baghdad');` والمتبقي للمحتوى = 13 − منشورات المحتوى هالشهر (`offer_id is null and kind in ('reel','carousel','story')`)، وبشرط المجموع ما يتجاوز 18 − 5 احتياط العروض اللي ما انحجزت.
2. اكتب عناصر الأسبوع الجاي في `content/<YYYY-MM>.json` (نفس الحقول الموجودة). لا تكرر موضوع سابق.
3. `python3 tips.py content/<YYYY-MM>.json media/content <ids>` ثم افحص الصور بنفسك (Read): لا نص مقطوع، ولا شي خارج مناطق الأمان.
4. `git add content media/content tips.py && git commit && git push` على main. الروابط: `https://raw.githubusercontent.com/a92eel-cpu/baghdad-offers-studio/main/media/content/<id>/<file>`.
5. الجدولة (`createScheduledPost`, providers `[{"network":"instagram"}]`):
   - ريل: `instagramData {type: REEL, showReelOnFeed: true}`، `videoThumbnailUrl` = reel.cover.jpg، الكابشن من الملف.
   - سلايد: `type: POST`، media = slide_01..NN.jpg بالترتيب، كابشن: الهوك، سطرين خلاصة، «احفظه ودزّه لـ…»، سؤال، 3–5 هاشتاغات.
   - ستوري: `type: STORY` بدون `text`.
6. سجّل كل واحد في `posts` (offer_id null، kind = reel | carousel | story، metricool_id، scheduled_for، media_urls، caption، status 'scheduled').
7. تحقق بـ `getScheduledPosts` من أخطاء آخر أسبوع (`ERROR`) وبلّغ عقيل إذا وُجدت.
8. سطر واحد لعقيل: شكد انجدول ومتى، وكم باقي من حد الشهر.
