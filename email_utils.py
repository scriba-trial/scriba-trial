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


def _followup_html(name: str, body: str) -> str:
    return f"""
<div dir="rtl" style="font-family:'Segoe UI',Arial,sans-serif;max-width:620px;margin:auto;color:#1a1a2e;">
  <div style="background:#0f172a;padding:28px 32px 20px;border-radius:12px 12px 0 0;">
    <p style="margin:0;font-size:22px;font-weight:700;letter-spacing:2px;color:#fff;">SCRIBA</p>
    <p style="margin:4px 0 0;font-size:13px;color:#94a3b8;">תוכן שנשמע כמוך</p>
  </div>
  <div style="background:#fff;padding:28px 32px;border:1px solid #e2e8f0;border-top:none;">
    <p style="font-size:17px;font-weight:600;margin:0 0 16px;">היי {name},</p>
    {body}
  </div>
  <div style="background:#f1f5f9;padding:14px 32px;border-radius:0 0 12px 12px;border:1px solid #e2e8f0;border-top:none;">
    <p style="margin:0;font-size:12px;color:#94a3b8;text-align:center;">
      Scriba &nbsp;|&nbsp; scriba.biz &nbsp;|&nbsp; powered by AI, crafted for humans
    </p>
  </div>
</div>"""


# ── Non-responders (topics_sent) ──────────────────────────────────────────────
# Sequence: ts_f1 (+2h) → ts_f2 (next day 09:00) → ts_f3 (same day 13:00)
#           → ts_f4 (+3 days 11:00) → ts_f5 (same day 20:00)

def _ts_followup_1(trial: dict):
    # TODO: write your text (+2h after topics email)
    name = trial["name"]
    subject = "TODO: subject ts_f1"
    body = f"""<p style="font-size:15px;line-height:1.8;">TODO: body ts_f1</p>"""
    _send(trial["email"], subject, _followup_html(name, body))


def _ts_followup_2(trial: dict):
    # TODO: write your text (next day 09:00)
    name = trial["name"]
    subject = "TODO: subject ts_f2"
    body = f"""<p style="font-size:15px;line-height:1.8;">TODO: body ts_f2</p>"""
    _send(trial["email"], subject, _followup_html(name, body))


def _ts_followup_3(trial: dict):
    # TODO: write your text (same day 13:00)
    name = trial["name"]
    subject = "TODO: subject ts_f3"
    body = f"""<p style="font-size:15px;line-height:1.8;">TODO: body ts_f3</p>"""
    _send(trial["email"], subject, _followup_html(name, body))


def _ts_followup_4(trial: dict):
    # TODO: write your text (+3 days 11:00)
    name = trial["name"]
    subject = "TODO: subject ts_f4"
    body = f"""<p style="font-size:15px;line-height:1.8;">TODO: body ts_f4</p>"""
    _send(trial["email"], subject, _followup_html(name, body))


def _ts_followup_5(trial: dict):
    # TODO: write your text (same day 20:00 — final)
    name = trial["name"]
    subject = "TODO: subject ts_f5"
    body = f"""<p style="font-size:15px;line-height:1.8;">TODO: body ts_f5</p>"""
    _send(trial["email"], subject, _followup_html(name, body))


# ── Completed (got post, not purchased) ───────────────────────────────────────
# Sequence: cp_f1 (+2h) → cp_f2 (next day 08:00) → cp_f3 (day after 13:00)
#           → cp_f4 (+3 days 08:00)

def _cp_followup_1(trial: dict):
    # TODO: write your text (+2h after post email)
    name = trial["name"]
    subject = "TODO: subject cp_f1"
    body = f"""<p style="font-size:15px;line-height:1.8;">TODO: body cp_f1</p>"""
    _send(trial["email"], subject, _followup_html(name, body))


def _cp_followup_2(trial: dict):
    # TODO: write your text (next day 08:00)
    name = trial["name"]
    subject = "TODO: subject cp_f2"
    body = f"""<p style="font-size:15px;line-height:1.8;">TODO: body cp_f2</p>"""
    _send(trial["email"], subject, _followup_html(name, body))


def _cp_followup_3(trial: dict):
    # TODO: write your text (day after cp_f2, 13:00)
    name = trial["name"]
    subject = "TODO: subject cp_f3"
    body = f"""<p style="font-size:15px;line-height:1.8;">TODO: body cp_f3</p>"""
    _send(trial["email"], subject, _followup_html(name, body))


def _cp_followup_4(trial: dict):
    # TODO: write your text (+3 days from cp_f3, 08:00 — final)
    name = trial["name"]
    subject = "TODO: subject cp_f4"
    body = f"""<p style="font-size:15px;line-height:1.8;">TODO: body cp_f4</p>"""
    _send(trial["email"], subject, _followup_html(name, body))
