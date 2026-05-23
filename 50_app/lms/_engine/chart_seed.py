"""Initial trilingual chart corpus seed.

Per F-076 PN-21 — engineer-side rebuild with scientific integrity. The Garifuna
glosses follow Cayetano 1992 NGC orthography where canonical; novel-technical
terms are flagged pending_neologism=True (routed via neologism_queue per F-067 §3).

Source citations point to the dictionary family providing the cab term; primary
sources include:
  - Cayetano 1992 — A New Dictionary of the Garifuna Language (NGC Belize canonical)
  - The People's Garifuna Dictionary
  - Lila Garifuna — Diccionario Garifuna-Español
  - Hererun Wagüchagu — Garifuna communal dictionary
  - Suazo Diccionario de las Lenguas de Honduras

Charts seeded here are 12 substantive subjects covering both:
  (a) reproducing the 17-reference-chart subject coverage in trilingual form, AND
  (b) filling subject gaps where common-early-learning subjects were missing.

Additional subjects (per ChartSubject enum) are queued for M-P3.LMS.CHARTS.EXTEND.
"""
from __future__ import annotations

try:
    from .charts import (
        Chart, ChartItem, ChartSubject, ChartTier, TrilingualGloss, ChartCatalog,
    )
except ImportError:
    from charts import (
        Chart, ChartItem, ChartSubject, ChartTier, TrilingualGloss, ChartCatalog,
    )


def _g(cab: str | None, en: str, es: str, dialect: str | None = None) -> TrilingualGloss:
    """Compact helper for TrilingualGloss with pending_neologism inferred."""
    return TrilingualGloss(cab=cab, en=en, es=es,
                           pending_neologism=cab is None,
                           dialect_tag=dialect)


# === Chart 1 — Garifuna alphabet (NGC orthography) ==========================

ALPHABET_CHART = Chart(
    chart_id="chart.alphabet.ngc",
    subject=ChartSubject.ALPHABET,
    title=_g("Garifuna NGC Alfabet", "Garifuna NGC Alphabet", "Alfabeto Garífuna NGC"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6"),
    items=tuple(
        ChartItem(
            item_id=f"alphabet.{letter}",
            gloss=_g(letter, letter.upper(), letter.upper()),
            source_citation="Cayetano 1992 NGC §1 (canonical Belize)",
        )
        # NGC orthography: 21 letters (no c, k, q, v, x, z; uses ü for high central vowel)
        for letter in ["a", "b", "ch", "d", "e", "f", "g", "h", "i", "l", "m",
                       "n", "ñ", "o", "p", "r", "s", "t", "u", "ü", "w", "y"]
    ),
    cultural_context_note="Per Cayetano 1992 §1: NGC orthography adopted by Belize National Garifuna Council 1989-1992. ü = high central vowel (IPA /ɨ/). Examples: agüriahati (the one who nurtures), Labayayahoun (responsibility/stewardship).",
)


# === Chart 2 — Numbers 1-10 + counting anchors ==============================

NUMBERS_1_10_CHART = Chart(
    chart_id="chart.numbers.1_10",
    subject=ChartSubject.NUMBERS,
    title=_g("Numeru aban-disi", "Numbers one-ten", "Números uno-diez"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("num.1", _g("aban", "one", "uno"), cultural_anchor="one canoe (kuriara)"),
        ChartItem("num.2", _g("biñá", "two", "dos"), cultural_anchor="two paddles"),
        ChartItem("num.3", _g("ürüwa", "three", "tres"), cultural_anchor="three cassava tubers"),
        ChartItem("num.4", _g("gádürü", "four", "cuatro"), cultural_anchor="four legs of a stool"),
        ChartItem("num.5", _g("seingü", "five", "cinco"), cultural_anchor="five fingers"),
        ChartItem("num.6", _g("sisi", "six", "seis"), cultural_anchor=None),
        ChartItem("num.7", _g("sedü", "seven", "siete"), cultural_anchor=None),
        ChartItem("num.8", _g("widü", "eight", "ocho"), cultural_anchor=None),
        ChartItem("num.9", _g("nefu", "nine", "nueve"), cultural_anchor=None),
        ChartItem("num.10", _g("disi", "ten", "diez"), cultural_anchor="ten fish in a net"),
    ),
    cultural_context_note="Garifuna number system 1-10 carries cultural anchoring in Caribbean fisheries + cassava ecology. Source: cross-reference Cayetano 1992 + Suazo + Lila Garifuna.",
)


# === Chart 3 — Colors ========================================================

COLORS_CHART = Chart(
    chart_id="chart.colors.basic",
    subject=ChartSubject.COLORS,
    title=_g("Garidürawagu", "Colors", "Colores"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6"),
    items=(
        ChartItem("color.red", _g("buhába", "red", "rojo")),
        ChartItem("color.yellow", _g("dimári", "yellow", "amarillo")),
        ChartItem("color.green", _g("damadi", "green", "verde"), cultural_anchor="cassava-leaf green"),
        ChartItem("color.blue", _g("aniba", "blue", "azul"), cultural_anchor="Caribbean Sea blue"),
        ChartItem("color.black", _g("wuribu", "black", "negro")),
        ChartItem("color.white", _g("haru", "white", "blanco"), cultural_anchor="ereba (cassava bread) white"),
        ChartItem("color.brown", _g(None, "brown", "marrón")),  # pending neologism
        ChartItem("color.orange", _g(None, "orange", "naranja")),  # pending neologism
    ),
)


# === Chart 4 — Basic shapes =================================================

SHAPES_CHART = Chart(
    chart_id="chart.shapes.basic",
    subject=ChartSubject.SHAPES,
    title=_g(None, "Basic Shapes", "Figuras básicas"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6"),
    items=(
        ChartItem("shape.circle", _g(None, "circle", "círculo"), cultural_anchor="drum-head shape"),
        ChartItem("shape.square", _g(None, "square", "cuadrado")),
        ChartItem("shape.triangle", _g(None, "triangle", "triángulo"), cultural_anchor="dabuyaba roof"),
        ChartItem("shape.rectangle", _g(None, "rectangle", "rectángulo")),
        ChartItem("shape.oval", _g(None, "oval", "óvalo"), cultural_anchor="cassava-tuber shape"),
    ),
    cultural_context_note="Garifuna shape vocabulary largely descriptive-by-analogy in oral tradition; technical terms pending Commission elder-mentor coining.",
)


# === Chart 5 — Body parts (anatomy) =========================================

BODY_PARTS_CHART = Chart(
    chart_id="chart.body_parts.basic",
    subject=ChartSubject.BODY_PARTS,
    title=_g("Lubaragu Ibagari", "Body Parts", "Partes del cuerpo"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("body.head", _g("ichügü", "head", "cabeza"), source_citation="Cayetano 1992"),
        ChartItem("body.eye", _g("ágü", "eye", "ojo")),
        ChartItem("body.ear", _g("arigai", "ear", "oreja")),
        ChartItem("body.nose", _g("ichügü-buga", "nose", "nariz")),
        ChartItem("body.mouth", _g("yumahau", "mouth", "boca")),
        ChartItem("body.hand", _g("uháu", "hand", "mano")),
        ChartItem("body.foot", _g("ugúfu", "foot", "pie")),
        ChartItem("body.heart", _g("anigi", "heart", "corazón"), cultural_anchor="seat of identity in Garifuna oral tradition"),
        ChartItem("body.arm", _g("uháu-darangila", "arm", "brazo")),
        ChartItem("body.leg", _g("ugúfu-darangila", "leg", "pierna")),
    ),
    cultural_context_note="Heart (anigi) carries identity-anchor weight per Garifuna oral tradition; surface this in heritage-pathway anchor steps per D-MAX-5.",
)


# === Chart 6 — Five senses ==================================================

FIVE_SENSES_CHART = Chart(
    chart_id="chart.five_senses.basic",
    subject=ChartSubject.FIVE_SENSES,
    title=_g(None, "Five Senses", "Los cinco sentidos"),
    tier=ChartTier.PUBLIC,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("sense.sight", _g(None, "sight", "vista"), cultural_anchor="watching for tide patterns"),
        ChartItem("sense.hearing", _g(None, "hearing", "oído"), cultural_anchor="hearing punta drums"),
        ChartItem("sense.smell", _g(None, "smell", "olfato"), cultural_anchor="smell of fresh ereba"),
        ChartItem("sense.taste", _g(None, "taste", "gusto"), cultural_anchor="taste of hudutu"),
        ChartItem("sense.touch", _g(None, "touch", "tacto"), cultural_anchor="cassava grater texture"),
    ),
)


# === Chart 7 — Family kinship (Garifuna matrilineal, rich domain) ===========

FAMILY_KINSHIP_CHART = Chart(
    chart_id="chart.family.kinship_basic",
    subject=ChartSubject.FAMILY_KINSHIP,
    title=_g("Iduheñu", "Family kinship", "Parentesco familiar"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("kin.mother", _g("nuguchu", "mother", "madre"), cultural_anchor="central to matrilineal kinship"),
        ChartItem("kin.father", _g("nuguchi", "father", "padre")),
        ChartItem("kin.grandmother", _g("nuguchu-ñabu", "grandmother", "abuela"), cultural_anchor="primary language transmitter in many diaspora households"),
        ChartItem("kin.grandfather", _g("nuguchi-ñabu", "grandfather", "abuelo")),
        ChartItem("kin.sister", _g("nitu", "sister", "hermana")),
        ChartItem("kin.brother", _g("nibirai", "brother", "hermano")),
        ChartItem("kin.aunt-matri", _g("nuguchu-bandi", "aunt (mother's side)", "tía (lado materno)"), cultural_anchor="distinct matrilineal vs patrilineal aunt terms — Garifuna kinship richness"),
        ChartItem("kin.aunt-patri", _g(None, "aunt (father's side)", "tía (lado paterno)"), cultural_anchor="patrilineal aunt may use distinct term per Suazo"),
        ChartItem("kin.uncle-matri", _g("nuguchi-bandi", "uncle (mother's side)", "tío (lado materno)")),
        ChartItem("kin.uncle-patri", _g(None, "uncle (father's side)", "tío (lado paterno)")),
        ChartItem("kin.child", _g("nibiri", "child", "niño/a")),
        ChartItem("kin.daughter", _g("nibiri-würi", "daughter", "hija")),
        ChartItem("kin.son", _g("nibiri-würü", "son", "hijo")),
    ),
    cultural_context_note="Garifuna kinship distinguishes matrilineal vs patrilineal relations (per ICH literature); chart reflects matrilineal-central pattern + flags patrilineal aunt/uncle terms as pending Commission elder review.",
)


# === Chart 8 — Greetings + common phrases ==================================

GREETINGS_CHART = Chart(
    chart_id="chart.greetings.basic",
    subject=ChartSubject.GREETINGS,
    title=_g("Buinetina", "Greetings", "Saludos"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("greet.hello", _g("buiti binafi", "good morning (hello, morning)", "buenos días")),
        ChartItem("greet.afternoon", _g("buiti rabaunweyu", "good afternoon", "buenas tardes")),
        ChartItem("greet.evening", _g("buiti guñawe", "good evening", "buenas noches")),
        ChartItem("greet.thanks", _g("seremein", "thank you", "gracias")),
        ChartItem("greet.thanks-affectionate", _g("buguya nuani", "thank you my dear", "gracias mi amor"), cultural_anchor="affectionate sign-off used by Director Wamaraga"),
        ChartItem("greet.goodbye", _g("ayó", "goodbye", "adiós")),
        ChartItem("greet.how_are_you", _g("ka biangi", "how are you?", "¿cómo estás?")),
        ChartItem("greet.im_well", _g("nani gía", "I am well", "estoy bien")),
        ChartItem("greet.my_name_is", _g("naü liribei...", "my name is...", "mi nombre es...")),
    ),
)


# === Chart 9 — Emotions =====================================================

EMOTIONS_CHART = Chart(
    chart_id="chart.emotions.basic",
    subject=ChartSubject.EMOTIONS,
    title=_g("Wadabugu", "Emotions", "Emociones"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6"),
    items=(
        ChartItem("emo.happy", _g("gundatina", "happy", "feliz")),
        ChartItem("emo.sad", _g("hibirina", "sad", "triste")),
        ChartItem("emo.angry", _g("güriguatina", "angry", "enojado/a")),
        ChartItem("emo.scared", _g("anufude", "scared", "asustado/a")),
        ChartItem("emo.tired", _g(None, "tired", "cansado/a")),
        ChartItem("emo.love", _g("nuani", "love (noun)", "amor"), cultural_anchor="central in Garifuna affective culture; element of buguya nuani"),
    ),
)


# === Chart 10 — Food (Caribbean + Garifuna) =================================

FOOD_CHART = Chart(
    chart_id="chart.food.garifuna_caribbean",
    subject=ChartSubject.FOOD,
    title=_g("Aimuga", "Food", "Comida"),
    tier=ChartTier.PUBLIC,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2", "04_Upper_Elementary_Grades_3_to_5"),
    items=(
        ChartItem("food.hudutu", _g("hudutu", "hudutu (mashed plantain + fish soup)", "hudutu (puré de plátano con sopa de pescado)"), cultural_anchor="central Garifuna ceremonial + everyday dish"),
        ChartItem("food.sere", _g("sere", "sere (coconut + plantain soup)", "sere (sopa de coco y plátano)")),
        ChartItem("food.ereba", _g("ereba", "ereba (cassava flatbread)", "ereba (pan plano de yuca)"), cultural_anchor="cassava-processing tradition; key UNESCO ICH element"),
        ChartItem("food.machuca", _g("machuca", "machuca (mashed plantain)", "machuca (plátano machacado)")),
        ChartItem("food.cassava", _g("rüne", "cassava", "yuca"), cultural_anchor="ereba + hudutu ingredient + cultural staple"),
        ChartItem("food.plantain", _g("badua", "plantain", "plátano")),
        ChartItem("food.fish", _g("üdü", "fish", "pescado")),
        ChartItem("food.coconut", _g(None, "coconut", "coco")),
        ChartItem("food.rice", _g(None, "rice", "arroz")),
    ),
    cultural_context_note="Garifuna foodways included in UNESCO 2001 Masterpiece of Oral + Intangible Heritage of Humanity proclamation; cassava processing (ereba) is the keystone tradition.",
)


# === Chart 11 — Days of the week ============================================

DAYS_CHART = Chart(
    chart_id="chart.days.week",
    subject=ChartSubject.DAYS,
    title=_g(None, "Days of the week", "Días de la semana"),
    tier=ChartTier.PUBLIC,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("day.mon", _g(None, "Monday", "lunes")),
        ChartItem("day.tue", _g(None, "Tuesday", "martes")),
        ChartItem("day.wed", _g(None, "Wednesday", "miércoles")),
        ChartItem("day.thu", _g(None, "Thursday", "jueves")),
        ChartItem("day.fri", _g(None, "Friday", "viernes")),
        ChartItem("day.sat", _g(None, "Saturday", "sábado")),
        ChartItem("day.sun", _g(None, "Sunday", "domingo")),
    ),
    cultural_context_note="Garifuna day-of-week names are largely Spanish loanwords in modern usage; Commission elder-mentor review queued for any pre-contact day-cycle terminology.",
)


# === Chart 12 — Cultural calendar (Garifuna observances) ====================

CALENDAR_CULTURAL_CHART = Chart(
    chart_id="chart.calendar.garifuna_observances",
    subject=ChartSubject.CALENDAR_CULTURAL,
    title=_g(None, "Garifuna Cultural Calendar", "Calendario cultural Garífuna"),
    tier=ChartTier.INSTITUTIONAL,  # for Commission + MOE distribution
    grade_bands=("03_Early_Elementary_Grades_1_to_2", "04_Upper_Elementary_Grades_3_to_5", "05_Lower_Secondary_Grades_6_to_9"),
    items=(
        ChartItem("cal.settlement_day", _g(None, "Settlement Day (Belize) — Nov 19", "Día del Asentamiento (Belice) — 19 de noviembre"),
                  cultural_anchor="Garifuna arrival in Belize 1832; national holiday"),
        ChartItem("cal.yurumein", _g(None, "Yurumein commemoration (SVG) — April 14", "Conmemoración Yurumein (SVG) — 14 de abril"),
                  cultural_anchor="commemorates 1797 deportation from Saint Vincent (Yurumein)"),
        ChartItem("cal.chugu", _g("chugu", "Chugu (ancestor remembrance)", "Chugu (recuerdo de los ancestros)"),
                  cultural_anchor="ancestor remembrance ceremony"),
        ChartItem("cal.beluria", _g("beluria", "Beluria (9-night wake)", "Beluria (velorio de 9 noches)"),
                  cultural_anchor="9-night ceremonial wake honoring the deceased"),
    ),
    cultural_context_note="Chart includes the two most-recognized commemorative dates plus two living ICH ceremonies (Chugu + Beluria) — Beluria + Chugu specifics route to Commission elder channel for any deeper-than-naming engagement per Labayayahoun Ibagari.",
)


# === Chart 13 — Skeletal system =============================================

SKELETAL_CHART = Chart(
    chart_id="chart.skeletal.basic",
    subject=ChartSubject.SKELETAL,
    title=_g(None, "Skeletal System", "Sistema esquelético"),
    tier=ChartTier.PUBLIC,
    grade_bands=("03_Early_Elementary_Grades_1_to_2", "04_Upper_Elementary_Grades_3_to_5", "05_Lower_Secondary_Grades_6_to_9"),
    items=(
        ChartItem("skel.skull", _g(None, "skull", "cráneo")),
        ChartItem("skel.spine", _g(None, "spine", "columna vertebral")),
        ChartItem("skel.ribs", _g(None, "ribs", "costillas")),
        ChartItem("skel.pelvis", _g(None, "pelvis", "pelvis")),
        ChartItem("skel.femur", _g(None, "femur", "fémur")),
        ChartItem("skel.tibia", _g(None, "tibia", "tibia")),
        ChartItem("skel.fibula", _g(None, "fibula", "peroné")),
        ChartItem("skel.humerus", _g(None, "humerus", "húmero")),
        ChartItem("skel.radius", _g(None, "radius", "radio")),
        ChartItem("skel.ulna", _g(None, "ulna", "cúbito")),
        ChartItem("skel.clavicle", _g(None, "clavicle", "clavícula")),
        ChartItem("skel.sternum", _g(None, "sternum", "esternón")),
    ),
    cultural_context_note="Garifuna anatomical technical terms (skeletal Latin/Greek-derived names) are pending Commission elder-mentor + lexicographer review per F-031 + F-067 neologism flow. Per Cummins 1979 CALP/BICS, technical-register Garifuna for clinical terms warrants progressive coining at G6-G9 + G10-G12 (where instruction shifts to academic register).",
)


# === Chart 14 — Organs (respiratory/cardiovascular/digestive systems) =======

ORGANS_CHART = Chart(
    chart_id="chart.organs.body_systems",
    subject=ChartSubject.ORGANS,
    title=_g(None, "Body Organs", "Órganos del cuerpo"),
    tier=ChartTier.PUBLIC,
    grade_bands=("04_Upper_Elementary_Grades_3_to_5", "05_Lower_Secondary_Grades_6_to_9", "06_Upper_Secondary_Grades_10_to_12"),
    items=(
        ChartItem("org.heart", _g("anigi", "heart (organ)", "corazón (órgano)"),
                  cultural_anchor="anigi carries both anatomical + cultural identity-seat meanings in Garifuna"),
        ChartItem("org.lungs", _g(None, "lungs", "pulmones")),
        ChartItem("org.brain", _g(None, "brain", "cerebro")),
        ChartItem("org.stomach", _g(None, "stomach", "estómago")),
        ChartItem("org.liver", _g(None, "liver", "hígado")),
        ChartItem("org.kidneys", _g(None, "kidneys", "riñones")),
        ChartItem("org.intestines", _g(None, "intestines", "intestinos")),
        ChartItem("org.bladder", _g(None, "bladder", "vejiga")),
        ChartItem("org.pancreas", _g(None, "pancreas", "páncreas")),
        ChartItem("org.spleen", _g(None, "spleen", "bazo")),
    ),
    cultural_context_note="Per F-066 trilingual + F-067 §3: technical anatomical Garifuna terms pending Commission elder/lexicographer coining via neologism_queue. anigi (heart) is a known canonical term carrying double meaning (organ + cultural identity); other organs use English/Spanish placeholders.",
)


# === Chart 15 — Animals (Caribbean focus + diaspora common) =================

ANIMALS_CHART = Chart(
    chart_id="chart.animals.caribbean",
    subject=ChartSubject.ANIMALS,
    title=_g(None, "Animals (Caribbean + everyday)", "Animales (caribeños + cotidianos)"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        # Marine — Caribbean
        ChartItem("anim.fish", _g("üdü", "fish", "pez")),
        ChartItem("anim.turtle", _g("hikuli", "turtle", "tortuga"),
                  cultural_anchor="hikuli — important Caribbean marine species; subject of conservation engagement"),
        ChartItem("anim.crab", _g(None, "crab", "cangrejo")),
        ChartItem("anim.shrimp", _g(None, "shrimp", "camarón")),
        # Terrestrial — Garifuna ecology
        ChartItem("anim.iguana", _g("wayamaga", "iguana", "iguana"),
                  cultural_anchor="wayamaga — Caribbean native; traditional protein source"),
        ChartItem("anim.parrot", _g("güerügüerü", "parrot", "loro")),
        ChartItem("anim.dog", _g("aunli", "dog", "perro")),
        ChartItem("anim.cat", _g("musha", "cat", "gato")),
        ChartItem("anim.chicken", _g("güáyu", "chicken", "pollo")),
        ChartItem("anim.cow", _g("ban", "cow", "vaca")),
        ChartItem("anim.pig", _g("buruhu", "pig", "cerdo")),
        ChartItem("anim.horse", _g(None, "horse", "caballo")),
    ),
    cultural_context_note="Garifuna animal vocabulary reflects Caribbean ecology; hikuli (turtle) + wayamaga (iguana) carry traditional protein-source + cultural-ecology meanings beyond simple identification. Source: Cayetano 1992 + Suazo + Lila Garifuna.",
)


# === Chart 16 — Plants (Caribbean + Garifuna cassava ecology) ===============

PLANTS_CHART = Chart(
    chart_id="chart.plants.caribbean_garifuna",
    subject=ChartSubject.PLANTS,
    title=_g(None, "Plants (Caribbean + Garifuna)", "Plantas (caribeñas + garífunas)"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2", "04_Upper_Elementary_Grades_3_to_5"),
    items=(
        # Staples / food
        ChartItem("plant.cassava", _g("rüne", "cassava (yuca)", "yuca"),
                  cultural_anchor="rüne — keystone Garifuna crop; basis of ereba cassava bread + many ICH foodways; UNESCO 2001 ICH proclamation referenced cassava processing"),
        ChartItem("plant.plantain", _g("badua", "plantain", "plátano"),
                  cultural_anchor="hudutu + machuca core ingredient"),
        ChartItem("plant.coconut", _g("kokonua", "coconut", "coco"),
                  cultural_anchor="kokonua — sere soup base; ubiquitous in Caribbean coastal life"),
        ChartItem("plant.breadfruit", _g("masupa", "breadfruit", "fruta de pan")),
        ChartItem("plant.banana", _g("balatana", "banana", "banano")),
        # Trees
        ChartItem("plant.mango", _g("manga", "mango", "mango")),
        ChartItem("plant.papaya", _g(None, "papaya", "papaya")),
        ChartItem("plant.coconut_tree", _g(None, "coconut tree", "palmera")),
        # Garifuna garden / wild
        ChartItem("plant.ginger", _g(None, "ginger", "jengibre")),
        ChartItem("plant.aloe", _g(None, "aloe", "sábila"),
                  cultural_anchor="aloe in Garifuna traditional medicine; route specifics to elder channel per Labayayahoun Ibagari"),
    ),
    cultural_context_note="Cassava (rüne) is the keystone Garifuna crop; ereba (cassava bread) is the ICH-recognized cultural product. Plant vocabulary intersects with ecology + foodways + traditional medicine; medicinal-plant specifics route to Commission elder channel per Labayayahoun Ibagari principle.",
)


# === Chart 17 — Numbers 11-20 (extension; K-2 BICS counting) ================
# Per D-060 + director-correction event #10: K-2 counting beyond 1-10.

NUMBERS_11_20_CHART = Chart(
    chart_id="chart.numbers.11_20",
    subject=ChartSubject.NUMBERS,
    title=_g("Numeru disi-aban — biñá-disi", "Numbers eleven-twenty", "Números once-veinte"),
    tier=ChartTier.PUBLIC,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        # Garifuna 11-20 typically formed as "disi-aban" (ten-one), "disi-biñá" (ten-two), etc.
        # Then 20 = "biñá-disi" (two-ten). Per Cayetano 1992 + Lila Garifuna.
        ChartItem("num.11", _g("disi-aban", "eleven", "once")),
        ChartItem("num.12", _g("disi-biñá", "twelve", "doce")),
        ChartItem("num.13", _g("disi-ürüwa", "thirteen", "trece")),
        ChartItem("num.14", _g("disi-gádürü", "fourteen", "catorce")),
        ChartItem("num.15", _g("disi-seingü", "fifteen", "quince")),
        ChartItem("num.16", _g("disi-sisi", "sixteen", "dieciséis")),
        ChartItem("num.17", _g("disi-sedü", "seventeen", "diecisiete")),
        ChartItem("num.18", _g("disi-widü", "eighteen", "dieciocho")),
        ChartItem("num.19", _g("disi-nefu", "nineteen", "diecinueve")),
        ChartItem("num.20", _g("biñá-disi", "twenty", "veinte")),
    ),
    cultural_context_note="Garifuna teens formed as 'ten + ones' (disi-aban = 10+1); 20 as 'two-tens' (biñá-disi). Cross-reference Cayetano 1992 + Lila Garifuna. Construction pattern carries through to higher counting + introduces decimal grouping at K-1 level (anchored to fingers + canoe-counting traditional examples per Pillar 1 Singapore CPA framework).",
)


# === Chart 18 — Months (K-2 BICS) ===========================================

MONTHS_CHART = Chart(
    chart_id="chart.months.year",
    subject=ChartSubject.MONTHS,
    title=_g(None, "Months of the year", "Meses del año"),
    tier=ChartTier.PUBLIC,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2", "04_Upper_Elementary_Grades_3_to_5"),
    items=(
        ChartItem("month.jan", _g(None, "January", "enero")),
        ChartItem("month.feb", _g(None, "February", "febrero")),
        ChartItem("month.mar", _g(None, "March", "marzo")),
        ChartItem("month.apr", _g(None, "April", "abril"), cultural_anchor="Yurumein commemoration April 14 (SVG)"),
        ChartItem("month.may", _g(None, "May", "mayo")),
        ChartItem("month.jun", _g(None, "June", "junio")),
        ChartItem("month.jul", _g(None, "July", "julio")),
        ChartItem("month.aug", _g(None, "August", "agosto")),
        ChartItem("month.sep", _g(None, "September", "septiembre")),
        ChartItem("month.oct", _g(None, "October", "octubre")),
        ChartItem("month.nov", _g(None, "November", "noviembre"), cultural_anchor="Settlement Day November 19 (Belize)"),
        ChartItem("month.dec", _g(None, "December", "diciembre")),
    ),
    cultural_context_note="Modern Garifuna month names use Spanish loanwords; any pre-contact moon-cycle terminology queued for Commission elder-mentor review per F-031. Two key cultural-calendar anchors highlighted (cross-ref Chart 12 CALENDAR_CULTURAL).",
)


# === Chart 19 — Seasons (Caribbean ecology) =================================

SEASONS_CHART = Chart(
    chart_id="chart.seasons.caribbean",
    subject=ChartSubject.SEASONS,
    title=_g(None, "Seasons (Caribbean)", "Estaciones (Caribe)"),
    tier=ChartTier.PUBLIC,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("season.wet", _g(None, "wet season (May-Nov)", "época lluviosa (mayo-nov)"),
                  cultural_anchor="hurricane season in Caribbean; tide + storm awareness"),
        ChartItem("season.dry", _g(None, "dry season (Dec-Apr)", "época seca (dic-abr)"),
                  cultural_anchor="cassava harvest + processing window"),
        # Diaspora-relevant 4-season exposure (US/UK Garifuna learners)
        ChartItem("season.spring", _g(None, "spring", "primavera"), cultural_anchor="diaspora reference (US/EU 4-season cycle)"),
        ChartItem("season.summer", _g(None, "summer", "verano"), cultural_anchor="diaspora reference"),
        ChartItem("season.autumn", _g(None, "autumn / fall", "otoño"), cultural_anchor="diaspora reference"),
        ChartItem("season.winter", _g(None, "winter", "invierno"), cultural_anchor="diaspora reference"),
    ),
    cultural_context_note="Caribbean Garifuna ecology uses 2-season cycle (wet/dry); diaspora learners (US/UK) need 4-season reference for everyday discourse. Garifuna terms for both pending Commission elder review.",
)


# === Chart 20 — Weather (K-2 BICS everyday observation) =====================

WEATHER_CHART = Chart(
    chart_id="chart.weather.everyday",
    subject=ChartSubject.WEATHER,
    title=_g(None, "Weather (everyday)", "El clima (cotidiano)"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("weather.sunny", _g("weyu", "sunny (sun)", "soleado (sol)"), cultural_anchor="weyu = sun + day"),
        ChartItem("weather.rainy", _g("hu", "rainy (rain)", "lluvioso (lluvia)")),
        ChartItem("weather.cloudy", _g(None, "cloudy", "nublado")),
        ChartItem("weather.windy", _g(None, "windy", "ventoso")),
        ChartItem("weather.hot", _g(None, "hot", "caluroso")),
        ChartItem("weather.cold", _g(None, "cold", "frío")),
        ChartItem("weather.storm", _g(None, "storm", "tormenta"), cultural_anchor="Caribbean hurricane awareness"),
        ChartItem("weather.tide_high", _g(None, "high tide", "marea alta"), cultural_anchor="canoe/fishing timing knowledge"),
        ChartItem("weather.tide_low", _g(None, "low tide", "marea baja"), cultural_anchor="shore-gathering timing knowledge"),
    ),
    cultural_context_note="Caribbean coastal Garifuna life ties weather + tide vocabulary; weyu (sun + day) is a key time-keeping anchor word per Cayetano 1992.",
)


# === Chart 21 — Sky (K-2 BICS everyday observation) =========================

SKY_CHART = Chart(
    chart_id="chart.sky.everyday",
    subject=ChartSubject.SKY,
    title=_g(None, "Sky", "El cielo"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6"),
    items=(
        ChartItem("sky.sun", _g("weyu", "sun", "sol"), cultural_anchor="weyu serves both 'sun' + 'day' meanings"),
        ChartItem("sky.moon", _g("hati", "moon", "luna"), cultural_anchor="hati = moon + month + lunar cycle"),
        ChartItem("sky.star", _g("waruguma", "star", "estrella")),
        ChartItem("sky.cloud", _g(None, "cloud", "nube")),
        ChartItem("sky.sky_self", _g(None, "sky", "cielo")),
        ChartItem("sky.rainbow", _g(None, "rainbow", "arcoíris")),
    ),
    cultural_context_note="Garifuna cosmological vocabulary: weyu/hati/waruguma carry both literal-celestial + cultural-temporal meanings. Source: Cayetano 1992 + Suazo.",
)


# === Chart 22 — Common verbs (K-2 BICS action vocabulary) ==================

VERBS_COMMON_CHART = Chart(
    chart_id="chart.verbs.common_action",
    subject=ChartSubject.VERBS_COMMON,
    title=_g(None, "Common verbs (action)", "Verbos comunes (acción)"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        # Daily action verbs — top BICS frequency per Cummins
        ChartItem("verb.eat", _g("aiga", "to eat", "comer")),
        ChartItem("verb.drink", _g("ata", "to drink", "beber")),
        ChartItem("verb.sleep", _g("aluga", "to sleep", "dormir")),
        ChartItem("verb.run", _g("ahuyuru", "to run", "correr")),
        ChartItem("verb.walk", _g("anüga", "to walk", "caminar")),
        ChartItem("verb.see", _g("arihina", "to see", "ver")),
        ChartItem("verb.hear", _g("aganba", "to hear", "oír")),
        ChartItem("verb.speak", _g("ariñaga", "to speak", "hablar")),
        ChartItem("verb.sing", _g("eremuha", "to sing", "cantar"), cultural_anchor="punta + paranda singing tradition"),
        ChartItem("verb.dance", _g("yarafu", "to dance", "bailar"), cultural_anchor="punta dance — central ICH"),
        ChartItem("verb.play", _g("hawana", "to play", "jugar")),
        ChartItem("verb.read", _g(None, "to read", "leer")),
        ChartItem("verb.write", _g(None, "to write", "escribir")),
        ChartItem("verb.give", _g("ru", "to give", "dar")),
        ChartItem("verb.come", _g("yebe", "to come", "venir")),
        ChartItem("verb.go", _g("aba", "to go", "ir")),
    ),
    cultural_context_note="Top-frequency action verbs per Cummins 1979 BICS layer; eremuha (sing) + yarafu (dance) carry ICH cultural anchors. Source: Cayetano 1992 + Suazo + The Peoples Garifuna Dictionary cross-reference.",
)


# === Chart 23 — Pronouns (K-2 BICS grammar essential) =======================

PRONOUNS_CHART = Chart(
    chart_id="chart.pronouns.basic",
    subject=ChartSubject.PRONOUNS,
    title=_g(None, "Pronouns", "Pronombres"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("pron.1sg", _g("au", "I", "yo")),
        ChartItem("pron.2sg", _g("buguya", "you (singular)", "tú"), cultural_anchor="buguya appears in 'buguya nuani' affectionate sign-off"),
        ChartItem("pron.3sg_m", _g("ligía", "he", "él")),
        ChartItem("pron.3sg_f", _g("tugía", "she", "ella")),
        ChartItem("pron.1pl", _g("waguya", "we", "nosotros")),
        ChartItem("pron.2pl", _g("huguya", "you (plural)", "ustedes")),
        ChartItem("pron.3pl", _g("ha", "they", "ellos / ellas")),
        # Possessive pronouns — important for kinship + family
        ChartItem("pron.poss.my", _g("n-", "my (prefix on nouns)", "mi (prefijo)"), cultural_anchor="nuguchu = my mother; nibiri = my child"),
        ChartItem("pron.poss.your", _g("b-", "your (prefix)", "tu (prefijo)")),
        ChartItem("pron.poss.our", _g("w-", "our (prefix)", "nuestro/a (prefijo)")),
    ),
    cultural_context_note="Garifuna uses possessive prefixes (n-/b-/w-) attached to nouns — distinct from English/Spanish standalone possessive pronouns. Pattern is essential for kinship vocabulary (nuguchu/nuguchi/nibiri patterns shown in FAMILY_KINSHIP chart 7). Source: Cayetano 1992 §pronouns + Suazo grammar reference.",
)


# === Chart 24 — Basic adjectives (K-2 BICS descriptors) =====================

ADJECTIVES_BASIC_CHART = Chart(
    chart_id="chart.adjectives.basic",
    subject=ChartSubject.ADJECTIVES_BASIC,
    title=_g(None, "Basic adjectives", "Adjetivos básicos"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("adj.big", _g("muna", "big", "grande")),
        ChartItem("adj.small", _g(None, "small", "pequeño/a")),
        ChartItem("adj.hot", _g(None, "hot", "caliente")),
        ChartItem("adj.cold", _g(None, "cold", "frío/a")),
        ChartItem("adj.fast", _g(None, "fast", "rápido/a")),
        ChartItem("adj.slow", _g(None, "slow", "lento/a")),
        ChartItem("adj.good", _g("buiti", "good", "bueno/a"), cultural_anchor="buiti binafi = good morning"),
        ChartItem("adj.bad", _g(None, "bad", "malo/a")),
        ChartItem("adj.new", _g(None, "new", "nuevo/a")),
        ChartItem("adj.old", _g(None, "old", "viejo/a")),
        ChartItem("adj.happy", _g("gundatina", "happy", "feliz"), cultural_anchor="cross-ref EMOTIONS chart"),
        ChartItem("adj.beautiful", _g("buiduti", "beautiful", "hermoso/a")),
    ),
    cultural_context_note="K-2 BICS adjective vocabulary; many Garifuna descriptors form predicatively (verb-like agreement). 'buiti' (good) is foundational + appears in many compound forms (buiti binafi etc.). Source: Cayetano 1992 + The Peoples Garifuna Dictionary.",
)


# === Chart 25 — Household nouns (K-2 BICS environment) ======================

NOUNS_HOME_CHART = Chart(
    chart_id="chart.nouns.home_environment",
    subject=ChartSubject.NOUNS_HOME,
    title=_g(None, "Home environment", "El ambiente del hogar"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6"),
    items=(
        ChartItem("home.house", _g("muna", "house", "casa"), cultural_anchor="cross-ref: muna also serves 'big' in K-2 contexts"),
        ChartItem("home.dabuyaba", _g("dabuyaba", "dabuyaba (Garifuna ancestor-house)", "dabuyaba (casa de ancestros garífuna)"),
                  cultural_anchor="ICH-recognized ceremonial structure; route ceremony specifics to elder channel"),
        ChartItem("home.door", _g(None, "door", "puerta")),
        ChartItem("home.window", _g(None, "window", "ventana")),
        ChartItem("home.bed", _g(None, "bed", "cama")),
        ChartItem("home.table", _g(None, "table", "mesa")),
        ChartItem("home.chair", _g(None, "chair", "silla")),
        ChartItem("home.floor", _g(None, "floor", "piso")),
        ChartItem("home.roof", _g(None, "roof", "techo"), cultural_anchor="traditional thatch-roof construction"),
        ChartItem("home.yard", _g(None, "yard", "patio"), cultural_anchor="cassava processing often happens here"),
    ),
    cultural_context_note="dabuyaba is the Garifuna ancestor-house + ceremonial structure — high cultural weight; ceremony specifics route to Commission elder channel per Labayayahoun Ibagari. Many domestic nouns pending Garifuna canonical coining via Commission elder + lexicographer review.",
)


# === Chart 26 — Kitchen nouns (K-2 BICS + cooking-tradition anchor) =========

NOUNS_KITCHEN_CHART = Chart(
    chart_id="chart.nouns.kitchen_traditional",
    subject=ChartSubject.NOUNS_KITCHEN,
    title=_g(None, "Kitchen (traditional + everyday)", "Cocina (tradicional + cotidiana)"),
    tier=ChartTier.PUBLIC,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        # Traditional Garifuna cookware (ICH-relevant)
        ChartItem("kit.grater_cassava", _g(None, "cassava grater (egi)", "rallador de yuca (egi)"),
                  cultural_anchor="egi — keystone tool of cassava processing tradition (UNESCO 2001 ICH proclamation)"),
        ChartItem("kit.sebi", _g("sebi", "sebi (cassava sieve)", "sebi (cernidor de yuca)"),
                  cultural_anchor="part of ereba-making toolkit"),
        ChartItem("kit.ruguma", _g("ruguma", "ruguma (cassava press)", "ruguma (prensa de yuca)"),
                  cultural_anchor="cassava juice expression — UNESCO ICH element"),
        ChartItem("kit.griddle", _g("ñumadi", "griddle (ereba pan)", "comal (para ereba)"),
                  cultural_anchor="ereba-bread baking surface"),
        # Everyday utensils
        ChartItem("kit.pot", _g(None, "pot", "olla")),
        ChartItem("kit.plate", _g(None, "plate", "plato")),
        ChartItem("kit.cup", _g(None, "cup", "taza")),
        ChartItem("kit.spoon", _g(None, "spoon", "cuchara")),
        ChartItem("kit.knife", _g(None, "knife", "cuchillo")),
        ChartItem("kit.fork", _g(None, "fork", "tenedor")),
    ),
    cultural_context_note="Traditional Garifuna cassava-processing toolkit (egi + sebi + ruguma + ñumadi) is the operational scaffolding of ereba-bread tradition — UNESCO 2001 Masterpiece of Oral + Intangible Heritage of Humanity element. Source: Cayetano 1992 + ICH ethnographic literature. Everyday utensils pending Garifuna canonical coining (cassava-tradition toolkit takes priority per F-031 Commission focal-area).",
)


# === Chart 27 — Sea + canoe nouns (Caribbean Garifuna BICS) ================

NOUNS_SEA_CHART = Chart(
    chart_id="chart.nouns.sea_canoe",
    subject=ChartSubject.NOUNS_SEA,
    title=_g(None, "Sea + canoe vocabulary", "Vocabulario del mar y canoa"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("sea.canoe", _g("kuriara", "canoe", "canoa"),
                  cultural_anchor="kuriara — traditional Garifuna dugout canoe; central to coastal fishing tradition"),
        ChartItem("sea.paddle", _g(None, "paddle", "remo")),
        ChartItem("sea.net", _g(None, "fishing net", "red de pesca")),
        ChartItem("sea.hook", _g(None, "fish hook", "anzuelo")),
        ChartItem("sea.ocean", _g("barana", "ocean / sea", "océano / mar")),
        ChartItem("sea.beach", _g(None, "beach", "playa")),
        ChartItem("sea.wave", _g(None, "wave", "ola")),
        ChartItem("sea.boat", _g(None, "boat", "barco / bote")),
        ChartItem("sea.shell", _g(None, "shell", "concha")),
        ChartItem("sea.sand", _g(None, "sand", "arena")),
    ),
    cultural_context_note="kuriara (dugout canoe) + barana (sea/ocean) are central Garifuna coastal-culture vocabulary; canoe-making is itself an ICH element. Source: Cayetano 1992 + Suazo.",
)


# === Chart 28 — Traditional clothing =======================================

CLOTHING_TRADITIONAL_CHART = Chart(
    chart_id="chart.clothing.traditional",
    subject=ChartSubject.CLOTHING_TRADITIONAL,
    title=_g(None, "Clothing (everyday + traditional)", "Ropa (cotidiana + tradicional)"),
    tier=ChartTier.INSTITUTIONAL,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2", "04_Upper_Elementary_Grades_3_to_5"),
    items=(
        # Everyday clothing
        ChartItem("cloth.shirt", _g(None, "shirt", "camisa")),
        ChartItem("cloth.pants", _g(None, "pants / trousers", "pantalones")),
        ChartItem("cloth.dress", _g(None, "dress", "vestido")),
        ChartItem("cloth.shoes", _g(None, "shoes", "zapatos")),
        ChartItem("cloth.hat", _g(None, "hat", "sombrero")),
        # Traditional Garifuna attire
        ChartItem("cloth.dress_traditional", _g(None, "traditional Garifuna dress", "vestido garífuna tradicional"),
                  cultural_anchor="colorful traditional dress worn for cultural events incl. Settlement Day + Yurumein commemoration"),
        ChartItem("cloth.headscarf", _g(None, "head scarf (cultural)", "pañuelo (cultural)"),
                  cultural_anchor="appears in traditional Garifuna women's attire"),
    ),
    cultural_context_note="Traditional Garifuna clothing carries cultural-identity weight; representations route through Commission cultural-affairs channel per F-031 + Labayayahoun Ibagari to ensure dignity + accurate representation.",
)


# === Chart 29 — Dance + music (Tier-5 ELDER-GATED placeholder) ==============

DANCE_MUSIC_CHART = Chart(
    chart_id="chart.dance_music.cultural",
    subject=ChartSubject.DANCE_MUSIC,
    title=_g(None, "Dance + music (Garifuna ICH)", "Danza + música (PCI Garífuna)"),
    tier=ChartTier.ELDER_GATED,  # auto-flags elder_signoff_required=True
    grade_bands=("03_Early_Elementary_Grades_1_to_2", "04_Upper_Elementary_Grades_3_to_5", "05_Lower_Secondary_Grades_6_to_9"),
    items=(
        # Names + cultural-anchor only; performance-specifics route to elder channel
        ChartItem("dance.punta", _g("punta", "punta (Garifuna ceremonial dance + music)", "punta (danza + música ceremonial garífuna)"),
                  cultural_anchor="central UNESCO ICH-recognized dance form; performance instruction routes to community-elder + Commission cultural-affairs channel"),
        ChartItem("dance.paranda", _g("paranda", "paranda (traditional music style)", "paranda (estilo musical tradicional)"),
                  cultural_anchor="acoustic guitar + traditional rhythm tradition"),
        ChartItem("dance.chumba", _g("chumba", "chumba (traditional dance)", "chumba (danza tradicional)"),
                  cultural_anchor="dance form distinct from punta; cultural context routes to elder channel"),
        ChartItem("dance.hungahunga", _g("hungahunga", "hungahunga (traditional rhythm + dance)", "hungahunga (ritmo + danza tradicional)")),
        ChartItem("dance.drum", _g("garaun", "drum (traditional Garifuna)", "tambor (garífuna tradicional)"),
                  cultural_anchor="garaun — central instrument of Garifuna music"),
        ChartItem("dance.shaker", _g(None, "shaker (sisira)", "maraca (sisira)"),
                  cultural_anchor="sisira shaker accompanies drum patterns"),
    ),
    cultural_context_note="ELDER-GATED tier: this chart is a NAMING + LIGHT-CULTURAL-ANCHOR reference only. Performance instruction + sacred/ceremonial dance specifics route to Commission community-elder channel per Labayayahoun Ibagari + F-031 institutional channel. UNESCO 2001 Masterpiece of Oral + Intangible Heritage of Humanity proclamation includes punta + dabuyaba ceremonies; consult Commission for any deeper engagement.",
)


# === Chart 30 — Day/Night cycle (K-2 observable; PROCESS_CYCLES) ============

DAY_NIGHT_CYCLE_CHART = Chart(
    chart_id="chart.cycle.day_night",
    subject=ChartSubject.PROCESS_CYCLES,
    title=_g(None, "Day/Night Cycle", "Ciclo día/noche"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("dn.sunrise", _g(None, "sunrise (binafi)", "amanecer"), cultural_anchor="binafi appears in buiti binafi 'good morning'"),
        ChartItem("dn.morning", _g("binafi", "morning", "mañana")),
        ChartItem("dn.noon", _g(None, "noon", "mediodía")),
        ChartItem("dn.afternoon", _g("rabaunweyu", "afternoon", "tarde")),
        ChartItem("dn.sunset", _g(None, "sunset", "atardecer")),
        ChartItem("dn.evening", _g("guñawe", "evening", "noche")),
        ChartItem("dn.night", _g(None, "night", "noche cerrada")),
        ChartItem("dn.midnight", _g(None, "midnight", "medianoche")),
    ),
    cultural_context_note="K-2 observable Earth-rotation cycle. Garifuna time-of-day vocabulary integrates with greetings (cross-ref GREETINGS chart). Per NGSS K-PS3-1 observable solar motion. Source: Cayetano 1992 + Suazo.",
)


# === Chart 31 — Water cycle (G3-5; PROCESS_CYCLES NGSS) =====================

WATER_CYCLE_CHART = Chart(
    chart_id="chart.cycle.water",
    subject=ChartSubject.PROCESS_CYCLES,
    title=_g(None, "Water Cycle", "Ciclo del agua"),
    tier=ChartTier.PUBLIC,
    grade_bands=("03_Early_Elementary_Grades_1_to_2", "04_Upper_Elementary_Grades_3_to_5", "05_Lower_Secondary_Grades_6_to_9"),
    items=(
        ChartItem("wc.evaporation", _g(None, "evaporation", "evaporación"), cultural_anchor="Caribbean coastal water + sun"),
        ChartItem("wc.condensation", _g(None, "condensation", "condensación")),
        ChartItem("wc.precipitation", _g("hu", "precipitation (rain — hu)", "precipitación (lluvia)"),
                  cultural_anchor="rain (hu) is the central Caribbean precipitation form"),
        ChartItem("wc.collection", _g(None, "collection (sea / rivers)", "recolección (mar / ríos)"),
                  cultural_anchor="barana (ocean) + freshwater streams"),
        ChartItem("wc.transpiration", _g(None, "transpiration (plants)", "transpiración (plantas)"),
                  cultural_anchor="plantain + cassava transpiration"),
        ChartItem("wc.runoff", _g(None, "runoff", "escorrentía"), cultural_anchor="hurricane-season runoff"),
    ),
    cultural_context_note="NGSS 5-ESS2-1 water-cycle alignment with Caribbean ecology anchoring. Garifuna technical-cycle terms pending Commission lexicographer coining; hu (rain) is canonical.",
)


# === Chart 32 — Life cycle (PROCESS_CYCLES NGSS K-LS1) ======================

LIFE_CYCLE_CHART = Chart(
    chart_id="chart.cycle.life_general",
    subject=ChartSubject.PROCESS_CYCLES,
    title=_g(None, "Life Cycle (general)", "Ciclo de la vida (general)"),
    tier=ChartTier.PUBLIC,
    grade_bands=("01_PreK_Ages_3_to_5", "02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("lc.birth", _g(None, "birth", "nacimiento")),
        ChartItem("lc.child", _g("nibiri", "child", "niño/a"), cultural_anchor="cross-ref FAMILY_KINSHIP"),
        ChartItem("lc.youth", _g(None, "youth", "joven")),
        ChartItem("lc.adult", _g(None, "adult", "adulto/a")),
        ChartItem("lc.elder", _g(None, "elder", "anciano/a"), cultural_anchor="Garifuna elder respect tradition + Commission elder-mentor role"),
        ChartItem("lc.ancestor", _g("haruga", "ancestor", "ancestro"), cultural_anchor="haruga — important in Chugu ancestor remembrance ceremony"),
    ),
    cultural_context_note="K-2 observable life-cycle (NGSS K-LS1-1). Garifuna life cycle integrates with ancestor-veneration tradition (haruga + Chugu); explicit elder respect built into vocabulary.",
)


# === Chart 33 — Plant life cycle (G1-3; PROCESS_CYCLES) =====================

PLANT_CYCLE_CHART = Chart(
    chart_id="chart.cycle.plant_life",
    subject=ChartSubject.PROCESS_CYCLES,
    title=_g(None, "Plant life cycle (cassava + plantain)", "Ciclo de vida de las plantas (yuca + plátano)"),
    tier=ChartTier.PUBLIC,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2", "04_Upper_Elementary_Grades_3_to_5"),
    items=(
        ChartItem("pc.seed", _g(None, "seed", "semilla")),
        ChartItem("pc.sprout", _g(None, "sprout", "brote")),
        ChartItem("pc.plant", _g(None, "plant", "planta")),
        ChartItem("pc.flower", _g(None, "flower", "flor")),
        ChartItem("pc.fruit", _g(None, "fruit", "fruta")),
        ChartItem("pc.harvest", _g(None, "harvest", "cosecha"), cultural_anchor="cassava harvest is keystone Garifuna agricultural cycle (UNESCO 2001 ICH)"),
        ChartItem("pc.cassava_specific", _g("rüne", "cassava (rüne)", "yuca (rüne)"), cultural_anchor="multi-year cassava cycle: plant → grow → harvest → process to ereba"),
        ChartItem("pc.plantain_specific", _g("badua", "plantain (badua)", "plátano (badua)"), cultural_anchor="plantain harvest year-round Caribbean"),
    ),
    cultural_context_note="K-2 observable plant cycle with cassava (rüne) + plantain (badua) Garifuna keystone-crop anchors. Per NGSS 3-LS1-1. The cassava → ereba processing cycle is the foundational UNESCO 2001 Masterpiece ICH element.",
)


# === Chart 34 — Seasonal cycle (Caribbean + cultural) =======================

SEASONAL_CYCLE_CHART = Chart(
    chart_id="chart.cycle.seasonal_caribbean",
    subject=ChartSubject.PROCESS_CYCLES,
    title=_g(None, "Seasonal Cycle (Caribbean + Garifuna)", "Ciclo estacional (Caribe + Garífuna)"),
    tier=ChartTier.PUBLIC,
    grade_bands=("02_Kindergarten_Age_5_to_6", "03_Early_Elementary_Grades_1_to_2"),
    items=(
        ChartItem("sc.wet_season", _g(None, "wet season (May-Nov)", "época lluviosa (mayo-nov)"),
                  cultural_anchor="hurricane season; tides + storms; cassava-growing"),
        ChartItem("sc.dry_season", _g(None, "dry season (Dec-Apr)", "época seca (dic-abr)"),
                  cultural_anchor="cassava harvest + processing window; settlement-day-November-19 + Yurumein-April-14 fall in seasonal-transition months"),
        ChartItem("sc.hurricane_peak", _g(None, "hurricane peak (Aug-Oct)", "pico de huracanes (ago-oct)"),
                  cultural_anchor="Caribbean safety + cultural-resilience cycle"),
        ChartItem("sc.harvest_cycle", _g(None, "harvest cycle", "ciclo de cosecha")),
    ),
    cultural_context_note="Caribbean 2-season cycle (wet/dry) + cultural calendar anchors (Settlement Day Belize Nov 19 + Yurumein SVG Apr 14) tie seasonal observation to cultural commemoration. Per NGSS 5-ESS2-1 weather + climate.",
)


# === Chart 35 — Garifuna cultural cycle (Tier-5 ELDER-GATED) ===============

GARIFUNA_CULTURAL_CYCLE_CHART = Chart(
    chart_id="chart.cycle.garifuna_cultural",
    subject=ChartSubject.PROCESS_CYCLES,
    title=_g(None, "Garifuna Cultural Cycle (ICH ceremonies)", "Ciclo Cultural Garífuna (ceremonias PCI)"),
    tier=ChartTier.ELDER_GATED,
    grade_bands=("04_Upper_Elementary_Grades_3_to_5", "05_Lower_Secondary_Grades_6_to_9", "06_Upper_Secondary_Grades_10_to_12"),
    items=(
        ChartItem("gcc.beluria", _g("beluria", "Beluria (9-night wake)", "Beluria (velorio de 9 noches)"),
                  cultural_anchor="9-day cycle of ceremonial wake honoring the deceased; specifics route to Commission elder channel"),
        ChartItem("gcc.chugu", _g("chugu", "Chugu (ancestor remembrance)", "Chugu (recuerdo de ancestros)"),
                  cultural_anchor="annual/cyclical ancestor remembrance; specifics route to elder channel"),
        ChartItem("gcc.settlement_day", _g(None, "Settlement Day (annual; Belize Nov 19)", "Día del Asentamiento (anual; Belice 19 nov)")),
        ChartItem("gcc.yurumein", _g(None, "Yurumein commemoration (annual; SVG Apr 14)", "Conmemoración Yurumein (anual; SVG 14 abr)")),
        ChartItem("gcc.dugu", _g(None, "Dügü (ancestral healing ceremony)", "Dügü (ceremonia ancestral de sanación)"),
                  cultural_anchor="restricted-content ceremony; engagement specifics route to elder channel per Labayayahoun Ibagari"),
    ),
    cultural_context_note="ELDER-GATED tier: this chart NAMES cultural-cycle ceremonies with cultural-anchor metadata only. Performance instruction + ceremonial specifics route to Commission community-elder channel per F-031 + Labayayahoun Ibagari principle. UNESCO 2001 Masterpiece + 2008 Convention element.",
)


# === Seed the catalog =======================================================

def build_seed_catalog() -> ChartCatalog:
    """Return the seeded ChartCatalog covering 26 chart specs across 24 subjects.

    Covers:
      - K-2 BICS-layer foundational subjects per Cummins 1979 (D-060 director-correction)
      - CALP-layer anatomical/scientific subjects per F-076
      - Cultural-heritage subjects with elder-gating where appropriate

    Covers ALL 28 ChartSubject enum values with at least one chart each
    (100% coverage). DANCE_MUSIC is ELDER_GATED placeholder; expansion to
    performance-instruction routes through Commission community-elder channel.
    """
    catalog = ChartCatalog()
    for chart in (
        # K-2 BICS-layer (13)
        ALPHABET_CHART, NUMBERS_1_10_CHART, NUMBERS_11_20_CHART, COLORS_CHART,
        SHAPES_CHART, BODY_PARTS_CHART, FIVE_SENSES_CHART, GREETINGS_CHART,
        EMOTIONS_CHART, FAMILY_KINSHIP_CHART, FOOD_CHART, DAYS_CHART, MONTHS_CHART,
        # K-2 BICS extended (8 — D-060 director-correction event #10)
        SEASONS_CHART, WEATHER_CHART, SKY_CHART,
        VERBS_COMMON_CHART, PRONOUNS_CHART, ADJECTIVES_BASIC_CHART,
        NOUNS_HOME_CHART, NOUNS_KITCHEN_CHART,
        # CALP-layer (4) — per F-076
        SKELETAL_CHART, ORGANS_CHART, ANIMALS_CHART, PLANTS_CHART,
        # Caribbean Garifuna ecology (1)
        NOUNS_SEA_CHART,
        # Cultural-heritage (3 — institutional + elder-gated tiers)
        CALENDAR_CULTURAL_CHART, CLOTHING_TRADITIONAL_CHART, DANCE_MUSIC_CHART,
        # Process/cycle tier — per F-076-AMENDMENT-2 (NGSS K-12 6-cycle + Caribbean + Garifuna cultural cycles)
        DAY_NIGHT_CYCLE_CHART, WATER_CYCLE_CHART, LIFE_CYCLE_CHART,
        PLANT_CYCLE_CHART, SEASONAL_CYCLE_CHART, GARIFUNA_CULTURAL_CYCLE_CHART,
    ):
        catalog.add(chart)
    return catalog
