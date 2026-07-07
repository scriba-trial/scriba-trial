import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def build_system_prompt(trial: dict) -> str:
    name = trial["name"]
    field = trial["field"]
    target = trial["target_client"]
    pain = trial["pain_point"]
    voice = trial.get("voice_signal", "")
    voice_line = f"\nהקול שלך: {voice}" if voice else ""

    return f"""אתה כותב תוכן שיווקי עבור {name}, {field}.
הקהל: {target}.
הכאב המרכזי של הקהל: {pain}.{voice_line}

כללי עיצוב מוחלטים:
- אסור קווי הפרדה --- או קווים מפרידים מכל סוג
- אסור מקף ארוך — (em dash)
- אסור כוכביות ** לעיצוב
- אסור ## לכותרות
- נקודה צמודה לאות האחרונה, ללא רווח לפניה

=== פסקת דוגמה — אורך וקצב ===

ישבנו בהפסקת כנס. חלון עם נוף לים, קפה ביד, קרואסון שנשאר על הצלחת כי הייתי עסוק.
לקוח פוטנציאלי עמד ממולי ואמר: "רן, אתה יקר לי".
עצרתי. לא הסברתי. לא הורדתי. לא התנצלתי.
אמרתי: "אני גובה 7,700 ש"ח בחודש. לא מתנצל על זה. אבל בוא נדבר על מה אתה מקבל".

לרוב אנשים מורידים מחיר עוד לפני שמישהו שאל. מחוששים שיקרים. מכינים התנצלות על המספר לפני שאמרו אותו בכלל.
אבל לקוח לא קונה מחיר. הוא קונה את הביטחון שלך שהמחיר שווה אותו.
כשאתה מתנצל, הוא שומע: "גם אני לא בטוח שאני שווה את זה".
כשאתה לא זז, הוא שומע: "הוא יודע משהו שאני עוד לא יודע".

מה המשפט שאתם תמיד מרגישים שצריך להסביר, במקום פשוט להגיד אותו?

=== עקרונות הקול ===

1. מטאפורה נושאת את הטיעון, לא מסבירה אותו.
2. ספציפיות במקום מחווה כללית — מספר מדויק, שם, פרט קונקרטי.
3. שורה קצרה היא פאנץ' אחרי בנייה, לא המרקם כולו.
4. הנקודה צומחת מהסצנה — פותחים בסצנה, התובנה עולה מתוכה.
5. ניגוד והיפוך כמנוע: שני חצאים שסותרים זה את זה.

כללים מוחלטים:
- אין להמציא אנקדוטות אישיות.
- פיסוק מחוץ למרכאות.
- אפס מקפים ארוכים (—) בגוף הטקסט.
- שיווק צריך להרגיש חכם ולא זול."""


def generate_post_for_trial(trial: dict, topic: str) -> dict:
    system = build_system_prompt(trial)
    name = trial["name"]

    fb = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=system,
        messages=[{"role": "user", "content": f"""כתוב פוסט לפייסבוק עבור {name} על הנושא: {topic}

פייסבוק: תוכן אישי-מקצועי, בניית סמכות, 300-450 מילה.
אל תוסיף hashtags.
החזר את הפוסט בלבד, ללא כותרות או הסברים."""}]
    )

    li = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=system,
        messages=[{"role": "user", "content": f"""כתוב פוסט ללינקדאין עבור {name} על הנושא: {topic}

לינקדאין: טון מקצועי ואנושי, 200-300 מילה.
הוסף 3-4 hashtags רלוונטיים בסוף.
החזר את הפוסט בלבד, ללא כותרות או הסברים."""}]
    )

    blog = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1800,
        system=system,
        messages=[{"role": "user", "content": f"""כתוב מאמר בלוג עבור {name} על הנושא: {topic}

הבלוג מיועד לאתר האישי שלו/ה. הקוראים הם אותו קהל יעד כמו בפוסטים.
אורך: 600-900 מילה. מעמיק יותר מפוסט רשתות חברתיות.
מבנה: כותרת ראשית, פסקת פתיחה חזקה, 3-4 פסקאות עם עומק, סיום עם קריאה לפעולה.
אל תוסיף hashtags.
החזר את הטקסט בלבד, ללא הסברים."""}]
    )

    reel = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system,
        messages=[{"role": "user", "content": f"""כתוב תסריט לריל אינסטגרם עבור {name} על הנושא: {topic}

הריל מדובר — {name} מדבר/ת ישירות למצלמה.
אורך: 45-60 שניות דיבור (כ-120-150 מילה).
מבנה:
[0-5 שניות] פתיחה שמעצירה גלילה
[5-40 שניות] גוף — רעיון אחד, דוגמה אחת
[40-60 שניות] סיום עם קריאה לפעולה

החזר את התסריט בלבד."""}]
    )

    return {
        "topic": topic,
        "facebook_text": fb.content[0].text.strip(),
        "linkedin_text": li.content[0].text.strip(),
        "blog_text": blog.content[0].text.strip(),
        "reel_script": reel.content[0].text.strip(),
    }


def suggest_topics(trial: dict) -> str:
    field = trial["field"]
    target = trial["target_client"]
    pain = trial["pain_point"]

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": f"""אתה יועץ תוכן.

הלקוח: {trial["name"]}, {field}.
הקהל: {target}.
הכאב: {pain}.

הצע 3 נושאי פוסט עם חיכוך טבעי, לא גנריים.
נושא טוב גורם למישהו לעצור: "זה בדיוק אני" או "אני לא מסכים".
לכל נושא: שורה אחת — שם הנושא + משפט הסבר קצר.

החזר בפורמט:
1. [נושא]: [הסבר קצר]
2. [נושא]: [הסבר קצר]
3. [נושא]: [הסבר קצר]

ללא כוכביות **, ללא קווי הפרדה ---, ללא markdown."""}]
    )
    return resp.content[0].text.strip()
