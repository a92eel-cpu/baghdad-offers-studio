# المسوّق — «عروض بغداد»

مهمة مجدولة يومية بعد الباحث. **لا ترسل أي رسالة لأي محل.**

## القاعدة (قرار عقيل 2026-10-22)
العروض والخصومات المعلنة علناً **ما تحتاج استئذان**: الصفحات التجارية غرضها الانتشار والإعلان، واحنا ننشرها مجاناً كخدمة. انشر أي عرض يلكاه الباحث.
إذا ماكو تاريخ انتهاء معلن: يبقى العرض **أسبوعاً** من يوم نقله (`valid_until = current_date + 7`)، وبعدها يُعلن أنه انتهى (حارس الانتهاء).

## الخطوات
1. اقرأ العملاء الجدد:
   `select * from leads where status in ('new','queued') order by created_at limit 8;`
2. انقل كل واحد إلى `offers` مباشرة:
   ```sql
   with l as (select * from leads where id in (…)),
   ins as (
     insert into offers (business_name, category, area, address, contact_name, phone, social_handle, offer_title,
       old_price, new_price, discount_pct, valid_from, valid_until, conditions, preferred_format, consent,
       status, source, permission, admin_notes)
     select business_name, category, area, area, '', phone, ig_handle, left(offer_title, 60),
       old_price, new_price, discount_pct, current_date, coalesce(valid_until, current_date + 7),
       nullif(<الشروط المعروفة>, ''), 'بوست', false, 'approved', 'research', 'public',
       'lead ' || id || ' — المصدر: ' || source_url
     from l returning id, business_name, admin_notes)
   update leads set status = 'converted', offer_id = ins.id
   from ins where ins.admin_notes like 'lead ' || leads.id || '%';
   ```
   - `phone` يُحفظ فقط بصيغة `07XXXXXXXXX`، وإلا `null`.
   - لا تخترع أسعاراً: إذا العرض نسبة فقط تبقى الأسعار `null` ويكفي `discount_pct`.
   - إذا تاريخ الانتهاء المعلن فات، علّم الـ lead `expired` ولا تنقله.
3. اختم برسالة واحدة لعقيل: قائمة مرقمة بالعروض التي نُقلت (المحل، العرض، لغاية أي تاريخ وهل التاريخ معلن أو أسبوع افتراضي). إن لم يوجد جديد: سطر واحد.
