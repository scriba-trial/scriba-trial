from flask import Flask, render_template, request, jsonify
import os
import threading
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
CRON_KEY = os.getenv("CRON_KEY", "scriba-trial-key-2026")


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

    supabase.table("trials").insert({
        "name": name,
        "email": email,
        "field": field,
        "target_client": target_client,
        "pain_point": pain_point,
        "voice_signal": voice_signal,
        "status": "new",
    }).execute()

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


if __name__ == "__main__":
    app.run(debug=True, port=5001)
