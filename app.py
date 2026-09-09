from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import threading
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from supabase import create_client
from dotenv import load_dotenv
from flask_cors import CORS
from functools import wraps

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {
    "origins": ["https://scriba.biz", "https://www.scriba.biz"]
}})
app.secret_key = os.getenv("SECRET_KEY", "scriba-admin-secret-2026")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
CRON_KEY = os.getenv("CRON_KEY", "scriba-trial-key-2026")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "scriba-admin-2026")
TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY")
TURNSTILE_SECRET = os.getenv("TURNSTILE_SECRET")
TURNSTILE_ERROR_MESSAGE = "האימות נכשל. יש לרענן את הדף ולנסות שוב."


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


def process_signup(data):
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    field = data.get("field", "").strip()
    target_client = data.get("target_client", "").strip()
    pain_point = data.get("pain_point", "").strip()
    voice_signal = data.get("voice_signal", "").strip()
    phone = data.get("phone", "").strip()

    form_data = dict(name=name, email=email, field=field,
                     target_client=target_client, pain_point=pain_point,
                     voice_signal=voice_signal, phone=phone)

    honeypot = data.get("company_website", "").strip()
    if honeypot:
        print(f"honeypot triggered {email}")
        return {"status": "honeypot", "name": name, "form": form_data}

    token = data.get("cf-turnstile-response", "").strip()
    if not TURNSTILE_SECRET or not token:
        return {"status": "error", "error": TURNSTILE_ERROR_MESSAGE, "form": form_data}

    try:
        verify_data = urllib.parse.urlencode({
            "secret": TURNSTILE_SECRET,
            "response": token,
            "remoteip": request.remote_addr or ""
        }).encode()
        req = urllib.request.Request(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data=verify_data,
            method="POST"
        )
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req, timeout=10) as resp:
            verification = json.loads(resp.read().decode())
    except Exception:
        verification = {}

    if not verification.get("success"):
        return {"status": "error", "error": TURNSTILE_ERROR_MESSAGE, "form": form_data}

    if not all([name, email, field, target_client, pain_point]):
        return {"status": "error", "error": "נא למלא את כל השדות החובה", "form": form_data}

    existing = supabase.table("trials").select("id").eq("email", email).execute()
    if existing.data:
        return {"status": "error", "error": "המייל הזה כבר רשום. בדוק/י את תיבת הדואר שלך.", "form": form_data}

    result = supabase.table("trials").insert({
        "name": name,
        "email": email,
        "field": field,
        "target_client": target_client,
        "pain_point": pain_point,
        "voice_signal": voice_signal,
        "phone": phone,
        "status": "new",
    }).execute()

    trial_id = result.data[0]["id"] if result.data else None

    if trial_id:
        def start():
            try:
                from trial_flow import start_trial
                start_trial(trial_id)
            except Exception as e:
                print(f"[signup] start trial error: {e}")
        threading.Thread(target=start, daemon=True).start()

    return {"status": "success", "name": name}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", error=None, form={}, turnstile_site_key=TURNSTILE_SITE_KEY)

    outcome = process_signup(request.form)
    if outcome["status"] == "honeypot":
        return render_template("success.html", name=outcome["name"])
    if outcome["status"] == "error":
        return render_template("index.html", error=outcome["error"], form=outcome["form"], turnstile_site_key=TURNSTILE_SITE_KEY)
    return render_template("success.html", name=outcome["name"])


@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json(silent=True) if request.is_json else request.form
    outcome = process_signup(data or {})
    if outcome["status"] == "honeypot":
        return jsonify({"ok": True})
    if outcome["status"] == "error":
        return jsonify({"ok": False, "error": outcome["error"]}), 400
    return jsonify({"ok": True})


@app.route("/cron/advance-trials", methods=["POST"])
def cron_advance_trials():
    if request.headers.get("X-Cron-Key", "") != CRON_KEY:
        return jsonify({"error": "unauthorized"}), 401

    def run():
        try:
            from trial_flow import advance_trials
            advance_trials()
        except Exception as e:
            print(f"[cron/advance-trials] error: {e}")

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/cron/check-replies", methods=["POST"])
def cron_check_replies():
    if request.headers.get("X-Cron-Key", "") != CRON_KEY:
        return jsonify({"error": "unauthorized"}), 401

    def run():
        try:
            from trial_flow import check_replies_and_generate
            check_replies_and_generate()
        except Exception as e:
            print(f"[cron/check-replies] error: {e}")

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/cron/send-followups", methods=["POST"])
def cron_send_followups():
    if request.headers.get("X-Cron-Key", "") != CRON_KEY:
        return jsonify({"error": "unauthorized"}), 401

    def run():
        try:
            from followup_flow import send_followups
            send_followups()
        except Exception as e:
            print(f"[cron/send-followups] error: {e}")

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"status": "started"})


# ── Admin ──────────────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        error = "סיסמה שגויה"
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    trials = supabase.table("trials").select("*").order("created_at", desc=True).execute().data
    return render_template("admin.html", trials=trials)


@app.route("/admin/trial/<trial_id>")
@admin_required
def admin_trial(trial_id):
    trial = supabase.table("trials").select("*").eq("id", trial_id).single().execute().data
    posts = supabase.table("posts").select("*").eq("trial_id", trial_id).order("created_at", desc=True).execute().data
    return render_template("admin_trial.html", trial=trial, posts=posts)


@app.route("/admin/post/<post_id>", methods=["GET", "POST"])
@admin_required
def admin_post(post_id):
    post = supabase.table("posts").select("*").eq("id", post_id).single().execute().data
    if not post:
        return redirect(url_for("admin_dashboard"))

    trial = supabase.table("trials").select("*").eq("id", post["trial_id"]).single().execute().data
    if request.method == "POST":
        supabase.table("posts").update({
            "facebook_text": request.form.get("facebook_text", ""),
            "linkedin_text": request.form.get("linkedin_text", ""),
            "blog_text": request.form.get("blog_text", ""),
            "reel_script": request.form.get("reel_script", ""),
        }).eq("id", post_id).execute()
        if request.form.get("action") == "send":
            from email_utils import send_post_email
            post.update({
                "facebook_text": request.form.get("facebook_text", ""),
                "linkedin_text": request.form.get("linkedin_text", ""),
                "blog_text": request.form.get("blog_text", ""),
                "reel_script": request.form.get("reel_script", ""),
            })
            send_post_email(trial, post)
            now = datetime.now(timezone.utc).isoformat()
            supabase.table("trials").update({
                "status": "cycle_1_sent",
                "post_sent_at": now,
                "next_action_at": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            }).eq("id", trial["id"]).execute()
        return redirect(url_for("admin_post", post_id=post_id))

    return render_template("admin_post.html", post=post, trial=trial)


@app.route("/admin/purchased/<trial_id>", methods=["POST"])
@admin_required
def admin_mark_purchased(trial_id):
    supabase.table("trials").update({"purchased": True}).eq("id", trial_id).execute()
    return redirect(url_for("admin_trial", trial_id=trial_id))


@app.route("/admin/delete/<trial_id>", methods=["POST"])
@admin_required
def admin_delete_trial(trial_id):
    supabase.table("trials").delete().eq("id", trial_id).execute()
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
