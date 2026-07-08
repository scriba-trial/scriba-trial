from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import threading
from supabase import create_client
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "scriba-admin-secret-2026")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
CRON_KEY = os.getenv("CRON_KEY", "scriba-trial-key-2026")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "scriba-admin-2026")


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", error=None, form={})

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    field = request.form.get("field", "").strip()
    target_client = request.form.get("target_client", "").strip()
    pain_point = request.form.get("pain_point", "").strip()
    voice_signal = request.form.get("voice_signal", "").strip()

    form_data = dict(name=name, email=email, field=field,
                     target_client=target_client, pain_point=pain_point,
                     voice_signal=voice_signal)

    if not all([name, email, field, target_client, pain_point]):
        return render_template("index.html", error="נא למלא את כל השדות החובה", form=form_data)

    existing = supabase.table("trials").select("id").eq("email", email).execute()
    if existing.data:
        return render_template("index.html",
                               error="המייל הזה כבר רשום. בדוק/י את תיבת הדואר שלך.",
                               form=form_data)

    result = supabase.table("trials").insert({
        "name": name,
        "email": email,
        "field": field,
        "target_client": target_client,
        "pain_point": pain_point,
        "voice_signal": voice_signal,
        "status": "new",
    }).execute()

    trial_id = result.data[0]["id"] if result.data else None

    if trial_id:
        def send_topics():
            try:
                from trial_flow import process_single_trial
                process_single_trial(trial_id)
            except Exception as e:
                print(f"[signup] send topics error: {e}")
        threading.Thread(target=send_topics, daemon=True).start()

    return render_template("success.html", name=name)


@app.route("/cron/send-topics", methods=["POST"])
def cron_send_topics():
    if request.headers.get("X-Cron-Key", "") != CRON_KEY:
        return jsonify({"error": "unauthorized"}), 401

    def run():
        try:
            from trial_flow import process_new_trials
            process_new_trials()
        except Exception as e:
            print(f"[cron/send-topics] error: {e}")

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


@app.route("/admin/send-topics/<trial_id>", methods=["POST"])
@admin_required
def admin_send_topics(trial_id):
    def run():
        try:
            from trial_flow import process_single_trial
            process_single_trial(trial_id)
        except Exception as e:
            print(f"[admin/send-topics] error: {e}")

    threading.Thread(target=run, daemon=True).start()
    return redirect(url_for("admin_trial", trial_id=trial_id))


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
