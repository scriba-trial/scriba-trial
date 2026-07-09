import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL = os.getenv("GMAIL_ADDRESS", "scriba.try@gmail.com")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "")


def _send(to: str, subject: str, html: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL
    msg["To"] = to
    msg["Reply-To"] = GMAIL
    msg.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL, APP_PASSWORD)
        s.sendmail(GMAIL, to, msg.as_string())


def send_topics_email(trial: dict, topics: str):
    name = trial["name"]
    to = trial["email"]
    subject = "הנה 3 נושאים לפוסט שלך — Scriba"

    html = f"""
<div dir="rtl" style="font-family:'Segoe UI',Arial,sans-serif;max-width:620px;margin:auto;color:#1a1a2e;">

  <div style="background:#0f172a;padding:28px 32px 20px;border-radius:12px 12px 0 0;">
    <p style="margin:0;font-size:22px;font-weight:700;letter-spacing:2px;color:#fff;">SCRIBA</p>
    <p style="margin:4px 0 0;font-size:13px;color:#94a3b8;">תוכן שנשמע כמוך</p>
  </div>

  <div style="background:#fff;padding:28px 32px;border:1px solid #e2e8f0;border-top:none;">
    <p style="font-size:17px;font-weight:600;margin:0 0 8px;">היי {name},</p>
    <p style="font-size:15px;line-height:1.7;margin:0 0 20px;color:#334155;">
      ניתחתי את הפרופיל שלך ומצאתי 3 נושאים שיכולים להניע שיחה אמיתית עם הקהל שלך.
    </p>

    <div style="background:#f8fafc;border-radius:8px;padding:20px 24px;margin-bottom:24px;white-space:pre-line;font-size:15px;line-height:1.9;color:#1e293b;">{topics}</div>

    <p style="font-size:15px;font-weight:600;margin:0 0 12px;">מה לעשות?</p>
    <p style="font-size:15px;line-height:1.8;margin:0 0 6px;">
      <strong>ענה/י למייל הזה</strong> עם המספר של הנושא שבחרת (לדוגמה: 2).<br>
      או כתוב/י נושא משלך ואנחנו ניצור פוסט לפיו.
    </p>
    <p style="font-size:14px;color:#64748b;margin:0;">
      לא מרוצה/ה מהנושאים? כתוב/י "דלג" ונשלח הצעות חדשות.
    </p>
  </div>

  <div style="background:#f1f5f9;padding:14px 32px;border-radius:0 0 12px 12px;border:1px solid #e2e8f0;border-top:none;">
    <p style="margin:0;font-size:12px;color:#94a3b8;text-align:center;">
      Scriba &nbsp;|&nbsp; scriba.biz &nbsp;|&nbsp; powered by AI, crafted for humans
    </p>
  </div>

</div>
"""
    _send(to, subject, html)
    print(f"[email] topics sent to {to}")


def send_post_email(trial: dict, post: dict):
    name = trial["name"]
    to = trial["email"]
    subject = "הפוסט שלך מוכן — Scriba"

    fb = post["facebook_text"].replace("\n", "<br>")
    li = post["linkedin_text"].replace("\n", "<br>")
    blog = post.get("blog_text", "").replace("\n", "<br>")
    reel = post.get("reel_script", "").replace("\n", "<br>")

    html = f"""
<div dir="rtl" style="font-family:'Segoe UI',Arial,sans-serif;max-width:620px;margin:auto;color:#1a1a2e;">

  <div style="background:#0f172a;padding:28px 32px 20px;border-radius:12px 12px 0 0;">
    <p style="margin:0;font-size:22px;font-weight:700;letter-spacing:2px;color:#fff;">SCRIBA</p>
    <p style="margin:4px 0 0;font-size:13px;color:#94a3b8;">תוכן שנשמע כמוך</p>
  </div>

  <div style="background:#fff;padding:28px 32px;border:1px solid #e2e8f0;border-top:none;">
    <p style="font-size:17px;font-weight:600;margin:0 0 8px;">היי {name},</p>
    <p style="font-size:15px;line-height:1.7;margin:0 0 24px;color:#334155;">
      הפוסט שלך על <strong>{post["topic"]}</strong> מוכן. תוכל/י להשתמש בו כמו שהוא או לערוך לפי הקול שלך.
    </p>

    <div style="border-right:4px solid #1877F2;padding:16px 20px;background:#f0f7ff;border-radius:0 8px 8px 0;margin-bottom:28px;">
      <p style="margin:0 0 10px;font-size:13px;font-weight:700;color:#1877F2;letter-spacing:1px;">FACEBOOK</p>
      <p style="margin:0;font-size:15px;line-height:1.8;color:#1e293b;">{fb}</p>
    </div>

    <div style="border-right:4px solid #0077B5;padding:16px 20px;background:#f0f8ff;border-radius:0 8px 8px 0;margin-bottom:28px;">
      <p style="margin:0 0 10px;font-size:13px;font-weight:700;color:#0077B5;letter-spacing:1px;">LINKEDIN</p>
      <p style="margin:0;font-size:15px;line-height:1.8;color:#1e293b;">{li}</p>
    </div>

    <div style="border-right:4px solid #16a34a;padding:16px 20px;background:#f0fdf4;border-radius:0 8px 8px 0;margin-bottom:28px;">
      <p style="margin:0 0 10px;font-size:13px;font-weight:700;color:#16a34a;letter-spacing:1px;">BLOG</p>
      <p style="margin:0;font-size:15px;line-height:1.8;color:#1e293b;">{blog}</p>
    </div>

    <div style="border-right:4px solid #e1306c;padding:16px 20px;background:#fff0f5;border-radius:0 8px 8px 0;margin-bottom:28px;">
      <p style="margin:0 0 10px;font-size:13px;font-weight:700;color:#e1306c;letter-spacing:1px;">INSTAGRAM</p>
      <p style="margin:0;font-size:15px;line-height:1.8;color:#475569;font-style:italic;">
        בגרסה המלאה כאן תצורף תמונה מותאמת + טקסט שתעלה לאינסטגרם שלך.
      </p>
    </div>

    <div style="border-right:4px solid #7c3aed;padding:16px 20px;background:#f5f3ff;border-radius:0 8px 8px 0;margin-bottom:28px;">
      <p style="margin:0 0 10px;font-size:13px;font-weight:700;color:#7c3aed;letter-spacing:1px;">תסריט לריל</p>
      <p style="margin:0;font-size:15px;line-height:1.8;color:#1e293b;">{reel}</p>
    </div>

    <div style="background:#f8fafc;border-radius:8px;padding:18px 20px;border:1px solid #e2e8f0;">
      <p style="margin:0 0 8px;font-size:14px;font-weight:600;color:#1e293b;">רוצה עוד?</p>
      <p style="margin:0;font-size:14px;line-height:1.7;color:#475569;">
        Scriba יוצר פוסט שבועי שנשמע כמוך, מעלה מעורבות ובונה סמכות בתחום שלך.<br>
        <a href="https://scriba.biz" style="color:#0f172a;font-weight:600;">scriba.biz</a>
      </p>
    </div>
  </div>

  <div style="background:#f1f5f9;padding:14px 32px;border-radius:0 0 12px 12px;border:1px solid #e2e8f0;border-top:none;">
    <p style="margin:0;font-size:12px;color:#94a3b8;text-align:center;">
      Scriba &nbsp;|&nbsp; scriba.biz &nbsp;|&nbsp; powered by AI, crafted for humans
    </p>
  </div>

</div>
"""
    _send(to, subject, html)
    print(f"[email] post sent to {to}")


# ── Follow-up emails ──────────────────────────────────────────────────────────

def send_followup_email(trial: dict, key: str):
    """Dispatch the correct follow-up email based on sequence key."""
    dispatchers = {
        "ts_f1": _ts_followup_1,
        "ts_f2": _ts_followup_2,
        "ts_f3": _ts_followup_3,
        "ts_f4": _ts_followup_4,
        "ts_f5": _ts_followup_5,
        "cp_f1": _cp_followup_1,
        "cp_f2": _cp_followup_2,
        "cp_f3": _cp_followup_3,
        "cp_f4": _cp_followup_4,
    }
    fn = dispatchers.get(key)
    if fn:
        fn(trial)
        print(f"[email] followup {key} sent to {trial['email']}")
    else:
        print(f"[email] unknown followup key: {key}")


def _followup_html(body: str) -> str:
    return f"""
<div dir="rtl" style="font-family:'Segoe UI',Arial,sans-serif;max-width:620px;margin:auto;color:#1a1a2e;">
  <div style="background:#0f172a;padding:28px 32px 20px;border-radius:12px 12px 0 0;">
    <p style="margin:0;font-size:22px;font-weight:700;letter-spacing:2px;color:#fff;">SCRIBA</p>
    <p style="margin:4px 0 0;font-size:13px;color:#94a3b8;">תוכן שנשמע כמוך</p>
  </div>
  <div style="background:#fff;padding:28px 32px;border:1px solid #e2e8f0;border-top:none;">
    {body}
  </div>
  <div style="background:#f1f5f9;padding:14px 32px;border-radius:0 0 12px 12px;border:1px solid #e2e8f0;border-top:none;">
    <p style="margin:0;font-size:12px;color:#94a3b8;text-align:center;">
      Scriba &nbsp;|&nbsp; scriba.biz &nbsp;|&nbsp; powered by AI, crafted for humans
    </p>
  </div>
</div>"""


_SIG = (
    '<p style="font-size:14px;line-height:1.8;color:#475569;margin-top:24px;'
    'padding-top:16px;border-top:1px solid #f1f5f9;">'
    'בברכה,<br>'
    '<strong style="color:#1e293b;">רן &mdash; SEEDS</strong><br>'
    '<span style="color:#94a3b8;font-style:italic;font-size:12px;">'
    'גורמים לאנשים לבחור בך, גם כאשר אתה יקר יותר</span></p>'
)

_CTA_TOPICS = (
    '<p style="font-size:14px;line-height:1.8;color:#475569;margin-top:14px;">'
    'כל מה שצריך עכשיו זה להשיב למייל הראשון שקיבלת עם 3 הצעות לפוסטים. '
    'פשוט להשיב עם מספר: 1, 2 או 3.</p>'
)


def _p(text: str) -> str:
    return f'<p style="font-size:15px;line-height:1.9;color:#1e293b;margin:0 0 12px;">{text}</p>'


# ── Non-responders (topics_sent) ──────────────────────────────────────────────

def _ts_followup_1(trial: dict):
    subject = "זה לוקח 10 שניות"
    body = (
        _p("שלחתי לך קודם כמה נושאים לפוסטים. אני מכיר את זה, המייל נפתח, נקרא, ונדחק הצידה כי משהו אחר קפץ. "
           "אבל מה יכול להיות דחוף יותר מלקדם את העסק? וכן כל מה שצריך עכשיו זה להשיב למייל הקודם שקיבלת "
           "עם 3 הצעות לפוסטים. פשוט להשיב עם מספר: 1, 2 או 3. תוך זמן קצר חוזרים אליך הפוסטים כתובים, "
           "בקול שלך, מוכנים. אז איזה מהם הכי מדבר אליך?") +
        _SIG
    )
    _send(trial["email"], subject, _followup_html(body))


def _ts_followup_2(trial: dict):
    name = trial["name"]
    subject = "מה קורה ברגע שבוחרים נושא"
    body = (
        _p(f"בוקר טוב {name}. רוב האנשים בטוחים שכתיבת פוסט מקצועי לוקחת שעה. ולמי יש שעה? זה בדיוק העניין. "
           "אין צורך בשעה הזאת. ברגע שבוחרים נושא, המערכת כותבת את הפוסט בקול שלך, עם הדקויות שלך, "
           "ומחזירה אותו מוכן. בלי דף לבן. בלי להתחיל מכלום. נושא אחד, תגובה אחת, "
           "וזה כל מה שמפריד בינך לבין הפוסט הבא שלך. אז מאיזה נושא מתחילים?") +
        _CTA_TOPICS +
        _SIG
    )
    _send(trial["email"], subject, _followup_html(body))


def _ts_followup_3(trial: dict):
    subject = "לא צריך להאמין לי"
    body = (
        _p("כל מי שמוכר משהו אומר שהוא הכי טוב. אז לא אבקש ממך להאמין לי. בשביל זה בדיוק יש ניסיון. "
           "בחירת נושא אחד היא כל מה שצריך כדי לראות איך נשמע פוסט שנכתב בקול שלך, "
           "אבל מבלי שבזבזת מזמנך לשבת ולכתוב. לא משהו גנרי שיכול להתאים לכל אחד, "
           "אלא כזה שנשמע כאילו כתבת אותו בעצמך. "
           "אם זה לא ידבר אליך, אז הרווחת פוסט בחינם. "
           "אבל אם זה כן ידבר אליך, ולא עשית, הפסדת פריצת דרך עצומה. אז מה בוחרים, 1, 2 או 3?") +
        _CTA_TOPICS +
        _SIG
    )
    _send(trial["email"], subject, _followup_html(body))


def _ts_followup_4(trial: dict):
    subject = "הלקוח הבא שלך מחפש אותך עכשיו"
    body = (
        _p("ברגע הזה מישהו מחפש בדיוק את השירות שלך. הוא פותח פייסבוק, לינקדאין, גוגל. ורואה את מי שמדבר. "
           "לא את הכי טוב. את מי שנמצא. כאן זה מתחיל. פוסט אחד, ואחריו עוד אחד, "
           "וככה נבנית הנוכחות שהופכת אותך לברירה ברורה בשוק. "
           "הנושאים לפוסטים ששלחתי לך עדיין מחכים. כל מה שצריך זה להשיב עם מספר, והפוסט הראשון כבר בדרך. "
           "עוד כמה זמן נשאיר את הבמה למתחרים?") +
        _CTA_TOPICS +
        _SIG
    )
    _send(trial["email"], subject, _followup_html(body))


def _ts_followup_5(trial: dict):
    subject = "אסגור את זה?"
    body = (
        _p('לא אציף אותך בעוד מיילים. שלחתי לך נושאים, הצעתי לך לראות איך נראה תוכן בקול שלך, וזה עדיין פתוח. '
           'אם גם עכשיו זה לא הזמן לקדם את העסק, הכל בסדר. אפשר פשוט להשיב "לא עכשיו" ואעצור. '
           'אבל אם יש בך אפילו סקרנות קטנה לראות את הפוסט הראשון, כל מה שצריך זה מספר אחד בתגובה. '
           'מה מרגיש לך נכון כרגע?') +
        _CTA_TOPICS +
        _SIG
    )
    _send(trial["email"], subject, _followup_html(body))


# ── Completed (got post, not purchased) ───────────────────────────────────────

def _cp_followup_1(trial: dict):
    subject = "אז זה נשמע כמוך?"
    body = (
        _p("קיבלת את הפוסטים. עכשיו השאלה האמיתית, כשקראת אותם, זה נשמע כמוך? "
           "זאת בדיוק המטרה. לא תוכן גנרי, אלא משהו שאפשר לעמוד מאחוריו ולשלוח בדיוק כמו שהוא. "
           "וחשוב שאדגיש משהו אחד. מה שקיבלת עכשיו זו רק טעימה. החלק האמיתי לא נגמר בזה שהפוסט מוכן. "
           "נגיע לזה מחר. בינתיים אשמח לשמוע, איך הרגיש לך לקרוא תוכן שנשמע כמוך ונוצר בלי מאמץ מצדך?") +
        _SIG
    )
    _send(trial["email"], subject, _followup_html(body))


def _cp_followup_2(trial: dict):
    subject = "החלק שעדיין לא ראית"
    body = (
        _p("אתמול קיבלת פוסטים מוכנים. יפה. אבל עדיין נשאר עליך לעשות איתם משהו. "
           "זה בדיוק ההבדל בין הטעימה למוצר. במוצר המלא לא נוגעים בכלום. "
           "הפוסט נכתב, מעוצב, ועולה לפייסבוק, לינקדאין, אינסטגרם והבלוג. אוטומטית. בקול שלך. "
           "כל מה שנשאר זה מבט אחד לפני הפרסום ואישור. פחות מ-3 דקות. "
           "הנוכחות שלך ממשיכה להיבנות באמצע פגישה, בחופשה, או ביום הכי עמוס שלך. "
           "כמה שווה לך להוריד את כל זה מהראש?") +
        _SIG
    )
    _send(trial["email"], subject, _followup_html(body))


def _cp_followup_3(trial: dict):
    subject = "זה אף פעם לא היה ChatGPT"
    body = (
        _p("אולי עולה לך המחשבה, יש לי ChatGPT, אכתוב לבד. אז שווה להיזכר מתי בפעם האחרונה באמת עשית את זה. "
           "זה מעולם לא היה עניין של כלי. הכלי קיים מזמן. מה שחסר זה שמישהו יבנה מזה שגרה שממשיכה לרוץ גם בלעדיך. "
           "בשבוע העמוס, בין לקוח לפגישה, שם בדיוק נופל התוכן. לא כי חסרים רעיונות, אלא כי אין מי שיוציא אותם לפועל. "
           "זה מה ש-SCRIBA עושה. לא עוד כלי חלוד בארגז, אלא כל העומס הזה יורד מהשולחן שלך. "
           "כמה עוד שבועות של שקט נפסיד לפני שמתחילים?") +
        _SIG
    )
    _send(trial["email"], subject, _followup_html(body))


def _cp_followup_4(trial: dict):
    subject = "שיחה קצרה, בלי התחייבות"
    body = (
        _p('אז ראית איך זה עובד. קיבלת פוסטים בקול שלך, וכבר ברור לך ההבדל בין לכתוב לבד לבין שזה פשוט קורה. '
           'נשאר רק להתאים את זה בדיוק אליך. הנושאים שלך, הלקוחות שלך, הקצב שלך. '
           'זה בדיוק מה שנעשה בשיחה קצרה. עשרים דקות. ואז יוצאים לדרך. '
           '3 פעמים בשבוע התוכן שלך עולה לפייסבוק, לינקדאין, אינסטגרם והבלוג האישי שלך. '
           '3 פעמים בשבוע מגיע אליך גם תסריט מוכן לריל/שורט. '
           'אם זה מרגיש נכון, אפשר להשיב למייל הזה, או לכתוב לי ישירות בווטסאפ. מה יותר נוח לך? '
           '<a href="https://wa.me/972507686280" style="color:#25D366;font-weight:600;text-decoration:none;">'
           'https://wa.me/972507686280</a>') +
        _SIG
    )
    _send(trial["email"], subject, _followup_html(body))
