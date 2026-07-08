"""
Follow-up email sequences for Scriba Trial (Israel time).

topics_sent sequence — non-responders (chose no topic yet):
  ts_f1 — +2h after topics_sent_at
  ts_f2 — next day at 09:00 IL
  ts_f3 — same day as ts_f2, at 13:00 IL
  ts_f4 — 3 days after ts_f3's day, at 11:00 IL
  ts_f5 — same day as ts_f4, at 20:00 IL

completed sequence — got posts, not purchased:
  cp_f1 — +2h after post_sent_at
  cp_f2 — next day at 08:00 IL
  cp_f3 — day after cp_f2's day, at 13:00 IL
  cp_f4 — 3 days after cp_f3's day, at 08:00 IL
"""

import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
IL = ZoneInfo("Asia/Jerusalem")


# ── time helpers ──────────────────────────────────────────────────────────────

def _now_il() -> datetime:
    return datetime.now(IL)


def _to_il(ts_str: str) -> datetime:
    dt = datetime.fromisoformat(ts_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IL)


def _next_day_at(dt_il: datetime, hour: int) -> datetime:
    d = (dt_il + timedelta(days=1)).date()
    return datetime(d.year, d.month, d.day, hour, 0, 0, tzinfo=IL)


def _same_day_at(dt_il: datetime, hour: int) -> datetime:
    d = dt_il.date()
    return datetime(d.year, d.month, d.day, hour, 0, 0, tzinfo=IL)


def _days_after_at(dt_il: datetime, days: int, hour: int) -> datetime:
    d = (dt_il + timedelta(days=days)).date()
    return datetime(d.year, d.month, d.day, hour, 0, 0, tzinfo=IL)


# ── main function ─────────────────────────────────────────────────────────────

def send_followups():
    """Check all active trials and send any due follow-up emails."""
    from email_utils import send_followup_email

    now = _now_il()

    all_topics_sent = supabase.table("trials").select("*").eq("status", "topics_sent").execute().data or []
    all_completed = supabase.table("trials").select("*").eq("status", "completed").execute().data or []

    topics_sent = [t for t in all_topics_sent if not t.get("purchased")]
    completed = [t for t in all_completed if not t.get("purchased")]

    print(f"[followups] {len(topics_sent)} non-responders, {len(completed)} completed")

    for trial in topics_sent:
        _process_topics_sent(trial, now, send_followup_email)

    for trial in completed:
        _process_completed(trial, now, send_followup_email)


def _process_topics_sent(trial: dict, now: datetime, send_fn):
    ts_raw = trial.get("topics_sent_at")
    if not ts_raw:
        return

    sent = trial.get("followups_sent") or {}
    ts = _to_il(ts_raw)

    try:
        if not sent.get("ts_f1"):
            if now >= ts + timedelta(hours=2):
                send_fn(trial, "ts_f1")
                _mark_sent(trial["id"], "ts_f1", now)

        elif not sent.get("ts_f2"):
            if now >= _next_day_at(ts, 9):
                send_fn(trial, "ts_f2")
                _mark_sent(trial["id"], "ts_f2", now)

        elif not sent.get("ts_f3"):
            f2_sent = _to_il(sent["ts_f2"])
            if now >= _same_day_at(f2_sent, 13):
                send_fn(trial, "ts_f3")
                _mark_sent(trial["id"], "ts_f3", now)

        elif not sent.get("ts_f4"):
            f3_sent = _to_il(sent["ts_f3"])
            if now >= _days_after_at(f3_sent, 3, 11):
                send_fn(trial, "ts_f4")
                _mark_sent(trial["id"], "ts_f4", now)

        elif not sent.get("ts_f5"):
            f4_sent = _to_il(sent["ts_f4"])
            if now >= _same_day_at(f4_sent, 20):
                send_fn(trial, "ts_f5")
                _mark_sent(trial["id"], "ts_f5", now)

    except Exception as e:
        print(f"[followups/ts] error for {trial['email']}: {e}")


def _process_completed(trial: dict, now: datetime, send_fn):
    ps_raw = trial.get("post_sent_at")
    if not ps_raw:
        return

    sent = trial.get("followups_sent") or {}
    ps = _to_il(ps_raw)

    try:
        if not sent.get("cp_f1"):
            if now >= ps + timedelta(hours=2):
                send_fn(trial, "cp_f1")
                _mark_sent(trial["id"], "cp_f1", now)

        elif not sent.get("cp_f2"):
            if now >= _next_day_at(ps, 8):
                send_fn(trial, "cp_f2")
                _mark_sent(trial["id"], "cp_f2", now)

        elif not sent.get("cp_f3"):
            f2_sent = _to_il(sent["cp_f2"])
            if now >= _next_day_at(f2_sent, 13):
                send_fn(trial, "cp_f3")
                _mark_sent(trial["id"], "cp_f3", now)

        elif not sent.get("cp_f4"):
            f3_sent = _to_il(sent["cp_f3"])
            if now >= _days_after_at(f3_sent, 3, 8):
                send_fn(trial, "cp_f4")
                _mark_sent(trial["id"], "cp_f4", now)

    except Exception as e:
        print(f"[followups/cp] error for {trial['email']}: {e}")


def _mark_sent(trial_id: str, key: str, now: datetime):
    row = supabase.table("trials").select("followups_sent").eq("id", trial_id).single().execute().data
    current = row.get("followups_sent") or {}
    current[key] = now.isoformat()
    supabase.table("trials").update({"followups_sent": current}).eq("id", trial_id).execute()
    print(f"[followups] marked {key} for {trial_id}")
