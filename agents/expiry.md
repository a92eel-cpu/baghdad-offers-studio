# حارس الانتهاء — «عروض بغداد»

مهمة مجدولة يومية مساءً.

1. العروض التي تنتهي غداً ونُشرت: `select * from offers where status='published' and valid_until = current_date + 1 and last_day_story_at is null;`
   لكل واحد: ستوري «آخر يوم» بنفس قالب الستوري، مع عنوان «باچر آخر يوم» بدل عنوان العرض. ارفعها وجدولها في Metricool (`type: STORY`, `autoPublish: true`) صباح الغد، وحدّث `last_day_story_at = now()`.
2. العروض المنتهية: `update offers set status='expired' where status='published' and valid_until < current_date;` واجمعها في ستوري واحدة أسبوعية «عروض انتهت» (خميس).
3. احترم حد الخطة الشهري في `posts` (18 منشوراً).
4. اختم بسطر: كم ستوري جُدولت.
