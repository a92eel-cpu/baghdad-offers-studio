"""رسومات «عروض بغداد» حسب نوع المحل — SVG مسطّح بألوان الهوية (بدون لوجوات المحلات).

kind_for(name, category) يختار الرسمة من اسم المحل وفئته، وsvg(kind) يرجّعها.
"""
L, C, P, I = "#D4FF3A", "#E8364A", "#F5F0E4", "#15112B"
S = f'stroke="{I}" stroke-width="10" stroke-linejoin="round" stroke-linecap="round"'

ART = {
"burger": f'''<path d="M70 190 Q200 60 330 190 Z" fill="#F2B04A" {S}/>
<circle cx="150" cy="140" r="6" fill="{P}"/><circle cx="200" cy="120" r="6" fill="{P}"/><circle cx="250" cy="140" r="6" fill="{P}"/>
<path d="M60 205 Q100 185 130 205 T200 205 T270 205 T340 205" fill="none" stroke="#7BC043" stroke-width="22" stroke-linecap="round"/>
<rect x="66" y="215" width="268" height="44" rx="22" fill="#7A3B22" {S}/>
<path d="M70 262 L330 262 L310 290 L90 290 Z" fill="{L}" {S}/>
<path d="M75 300 L325 300 Q325 340 290 340 L110 340 Q75 340 75 300 Z" fill="#F2B04A" {S}/>''',
"pizza": f'''<path d="M200 330 L70 90 Q200 40 330 90 Z" fill="#F7D774" {S}/>
<path d="M70 90 Q200 40 330 90 L320 115 Q200 70 80 115 Z" fill="#E09A3E" {S}/>
<circle cx="170" cy="150" r="22" fill="{C}" {S}/><circle cx="240" cy="160" r="20" fill="{C}" {S}/>
<circle cx="205" cy="230" r="18" fill="{C}" {S}/><circle cx="150" cy="200" r="7" fill="{I}"/><circle cx="235" cy="210" r="7" fill="{I}"/>''',
"fish": f'''<path d="M60 200 Q160 90 270 200 Q160 310 60 200 Z" fill="#6FC3DF" {S}/>
<path d="M265 200 L340 140 L340 260 Z" fill="#6FC3DF" {S}/>
<circle cx="115" cy="185" r="12" fill="{I}"/><path d="M160 160 Q185 200 160 240" fill="none" {S}/>
<path d="M60 330 Q200 300 340 330" fill="none" stroke="{L}" stroke-width="14" stroke-linecap="round"/>''',
"chicken": f'''<path d="M130 110 Q210 40 290 110 Q340 180 270 240 L200 250 Q120 230 120 170 Z" fill="#D9822B" {S}/>
<path d="M200 245 L150 310" {S}/><circle cx="135" cy="320" r="22" fill="{P}" {S}/><circle cx="160" cy="335" r="18" fill="{P}" {S}/>
<path d="M190 120 Q230 100 260 130" fill="none" stroke="{L}" stroke-width="12" stroke-linecap="round"/>''',
"grill": f'''<path d="M60 330 L340 70" stroke="{I}" stroke-width="12" stroke-linecap="round"/>
<rect x="95" y="230" width="70" height="70" rx="18" transform="rotate(-42 130 265)" fill="#8B4A2B" {S}/>
<rect x="165" y="165" width="70" height="70" rx="18" transform="rotate(-42 200 200)" fill="{C}" {S}/>
<rect x="235" y="100" width="70" height="70" rx="18" transform="rotate(-42 270 135)" fill="#8B4A2B" {S}/>
<path d="M90 120 Q110 90 95 60 M140 100 Q160 70 145 40" fill="none" stroke="{L}" stroke-width="10" stroke-linecap="round"/>''',
"shawarma": f'''<path d="M120 330 L170 90 Q200 70 230 90 L280 330 Z" fill="{P}" {S}/>
<path d="M150 190 L250 190 L260 240 L140 240 Z" fill="#B5652E" {S}/>
<path d="M165 120 Q200 100 235 120 L245 170 L155 170 Z" fill="#7BC043" {S}/>
<path d="M135 280 L265 280" {S}/>''',
"sweets": f'''<circle cx="200" cy="200" r="130" fill="#F2B04A" {S}/>
<path d="M85 175 Q110 95 200 85 Q300 90 318 180 Q300 230 260 215 Q230 250 200 225 Q160 250 135 220 Q95 235 85 175 Z" fill="#F48FB1" {S}/>
<circle cx="200" cy="200" r="38" fill="{I}"/>
<path d="M140 140 l12 8 M250 130 l-6 14 M280 180 l-14 4 M120 190 l14 -2 M210 120 l4 14" stroke="{L}" stroke-width="10" stroke-linecap="round"/>''',
"bakery": f'''<path d="M70 250 Q90 130 200 120 Q310 130 330 250 Q200 290 70 250 Z" fill="#E7B45C" {S}/>
<path d="M130 160 Q150 200 135 245 M200 135 Q215 190 200 260 M270 160 Q250 200 265 245" fill="none" {S}/>
<ellipse cx="200" cy="300" rx="150" ry="22" fill="{L}" {S}/>''',
"coffee": f'''<path d="M100 150 L300 150 L280 320 Q275 340 255 340 L145 340 Q125 340 120 320 Z" fill="{P}" {S}/>
<path d="M295 190 Q350 190 345 240 Q340 285 285 280" fill="none" {S}/>
<rect x="110" y="200" width="180" height="50" fill="{C}"/>
<path d="M160 120 Q140 90 165 60 M210 120 Q190 90 215 60 M260 120 Q240 90 265 60" fill="none" stroke="{L}" stroke-width="10" stroke-linecap="round"/>''',
"rice": f'''<ellipse cx="200" cy="270" rx="160" ry="55" fill="{P}" {S}/>
<path d="M70 260 Q200 110 330 260 Z" fill="#F4D58D" {S}/>
<path d="M170 170 Q240 120 280 180 Q260 220 200 215 Z" fill="#D9822B" {S}/>
<circle cx="140" cy="230" r="8" fill="{C}"/><circle cx="250" cy="240" r="8" fill="#7BC043"/><circle cx="190" cy="245" r="8" fill="#7BC043"/>''',
"salad": f'''<path d="M60 200 L340 200 Q330 330 200 330 Q70 330 60 200 Z" fill="{P}" {S}/>
<circle cx="130" cy="180" r="42" fill="#7BC043" {S}/><circle cx="200" cy="160" r="48" fill="#9BD15A" {S}/><circle cx="270" cy="180" r="42" fill="#7BC043" {S}/>
<circle cx="175" cy="195" r="20" fill="{C}" {S}/><circle cx="245" cy="198" r="18" fill="{C}" {S}/>''',
"falafel": f'''<ellipse cx="200" cy="290" rx="160" ry="45" fill="{P}" {S}/>
<circle cx="135" cy="230" r="50" fill="#9A6A2E" {S}/><circle cx="265" cy="230" r="50" fill="#9A6A2E" {S}/><circle cx="200" cy="170" r="52" fill="#B07A36" {S}/>
<path d="M120 220 l8 4 M180 160 l8 4 M250 225 l8 4" stroke="{L}" stroke-width="10" stroke-linecap="round"/>''',
"flowers": f'''<path d="M200 330 L200 200 M200 260 Q150 240 140 200 M200 250 Q250 230 262 195" fill="none" stroke="#3E8E41" stroke-width="12" stroke-linecap="round"/>
<g fill="{C}" {S}><circle cx="200" cy="130" r="34"/><circle cx="140" cy="165" r="30"/><circle cx="262" cy="160" r="30"/></g>
<g fill="{L}"><circle cx="200" cy="130" r="12"/><circle cx="140" cy="165" r="10"/><circle cx="262" cy="160" r="10"/></g>
<path d="M150 300 L250 300 L235 345 L165 345 Z" fill="{P}" {S}/>''',
"plate": f'''<circle cx="200" cy="200" r="120" fill="{P}" {S}/><circle cx="200" cy="200" r="75" fill="{L}" {S}/>
<path d="M50 90 L50 310 M30 90 L30 150 Q30 170 50 170 Q70 170 70 150 L70 90" fill="none" {S}/>
<path d="M350 90 Q320 140 340 190 L350 190 L350 310" fill="none" {S}/>''',
"clothes": f'''<path d="M140 70 L90 95 L45 160 L95 195 L120 165 L120 340 L280 340 L280 165 L305 195 L355 160 L310 95 L260 70 Q200 120 140 70 Z" fill="{C}" {S}/>
<path d="M150 230 L250 230" stroke="{L}" stroke-width="16" stroke-linecap="round"/>''',
"accessories": f'''<rect x="150" y="40" width="100" height="70" rx="20" fill="{P}" {S}/><rect x="150" y="290" width="100" height="70" rx="20" fill="{P}" {S}/>
<circle cx="200" cy="200" r="100" fill="{L}" {S}/><circle cx="200" cy="200" r="70" fill="{P}" {S}/>
<path d="M200 200 L200 150 M200 200 L235 220" {S}/>''',
"beauty": f'''<rect x="90" y="190" width="80" height="150" rx="14" fill="{I}" {S}/><path d="M100 190 L100 120 Q130 80 160 120 L160 190 Z" fill="{C}" {S}/>
<rect x="215" y="120" width="110" height="220" rx="30" fill="#F48FB1" {S}/><rect x="245" y="70" width="50" height="55" rx="10" fill="{L}" {S}/>
<path d="M240 180 L300 180" stroke="{P}" stroke-width="12" stroke-linecap="round"/>''',
"mobile": f'''<rect x="120" y="40" width="160" height="320" rx="30" fill="{I}" {S}/><rect x="138" y="80" width="124" height="230" rx="10" fill="{L}"/>
<circle cx="200" cy="335" r="10" fill="{P}"/><path d="M165 200 L195 230 L245 170" fill="none" stroke="{I}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>''',
"gym": f'''<rect x="40" y="140" width="50" height="120" rx="12" fill="{C}" {S}/><rect x="310" y="140" width="50" height="120" rx="12" fill="{C}" {S}/>
<rect x="85" y="165" width="35" height="70" rx="8" fill="{L}" {S}/><rect x="280" y="165" width="35" height="70" rx="8" fill="{L}" {S}/>
<rect x="115" y="185" width="170" height="30" rx="10" fill="{P}" {S}/>''',
"courses": f'''<path d="M40 160 L200 90 L360 160 L200 230 Z" fill="{I}" {S}/><path d="M110 195 L110 280 Q200 330 290 280 L290 195" fill="{C}" {S}/>
<path d="M330 175 L330 270" {S}/><circle cx="330" cy="285" r="16" fill="{L}" {S}/>''',
"furniture": f'''<rect x="70" y="150" width="260" height="110" rx="30" fill="{C}" {S}/><rect x="40" y="200" width="70" height="110" rx="25" fill="{C}" {S}/><rect x="290" y="200" width="70" height="110" rx="25" fill="{C}" {S}/>
<rect x="100" y="230" width="200" height="60" rx="14" fill="{L}" {S}/><path d="M80 310 L80 345 M320 310 L320 345" {S}/>''',
"market": f'''<path d="M30 80 L80 80 L120 270 L310 270 L345 130 L95 130" fill="none" {S}/>
<path d="M105 140 L335 140 L310 260 L125 260 Z" fill="{L}"/><circle cx="140" cy="320" r="24" fill="{C}" {S}/><circle cx="290" cy="320" r="24" fill="{C}" {S}/>
<path d="M170 140 L180 260 M230 140 L230 260 M285 140 L275 260" stroke="{I}" stroke-width="8"/>''',
"tag": f'''<path d="M60 200 L180 70 L340 70 L340 230 L210 360 Z" fill="{L}" {S}/><circle cx="290" cy="120" r="22" fill="{I}"/>
<path d="M170 250 L250 170" stroke="{C}" stroke-width="16" stroke-linecap="round"/>''',
}

FOOD_KEYS = [
    ("pizza", ["بيتزا", "pizza", "بعجين"]), ("burger", ["بركر", "برغر", "burger", "bites", "بايتس"]),
    ("fish", ["سمك", "اسماك", "الفقمة"]), ("shawarma", ["شاورما", "شاورمة"]),
    ("sweets", ["حلويات", "قشطوطة", "كنافة", "دونات", "donut", "كيك", "ايس", "ice", "شربت", "بقلاوة"]),
    ("coffee", ["كافيه", "cafe", "café", "قهوة", "كوفي"]), ("salad", ["دايت", "diet", "هيلثي", "healthy", "صحي"]),
    ("rice", ["مندي", "بخاري", "كبسة", "رز", "قوزي"]), ("falafel", ["فلافل", "باقلاء"]),
    ("chicken", ["جكن", "دجاج", "chicken", "تشيكن", "كرنشي", "فرايد"]),
    ("grill", ["مشويات", "كباب", "كص", "تكة", "كفتة", "لحوم", "grill", "مشاوي", "قصاب"]),
    ("bakery", ["مخبوزات", "معجنات", "فطور", "صمون", "فطائر", "تنور"]), ("flowers", ["زهور", "ورد"]),
]
CAT_KEYS = {"ملابس": "clothes", "اكسسوارات": "accessories", "إكسسوارات": "accessories", "تجميل": "beauty",
            "موبايلات": "mobile", "جيم": "gym", "دورات": "courses", "أثاث": "furniture", "اثاث": "furniture",
            "سوبرماركت": "market"}

def kind_for(name, category="مطاعم"):
    n = (name or "").lower()
    if category in CAT_KEYS: return CAT_KEYS[category]
    for k, words in FOOD_KEYS:
        if any(w.lower() in n for w in words): return k
    return "plate" if category in ("مطاعم", None, "") else "tag"

def svg(kind, size=360):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="{size}" height="{size}">'
            f'{ART.get(kind, ART["tag"])}</svg>')
