"""
Business logic for the trial flow.

process_new_trials():   picks up status='new' trials, suggests topics, sends email
check_replies_and_generate(): checks inbox for replies, generates + sends post
"""

import os
import imaplib
import email as email_lib
from datetime import datetime, timedelta, timezone
from email.header import decode_header
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
GMAIL = os.getenv("GMAIL_ADDRESS", "scriba.try@gmail.com")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "")


# ── helpers ───────────────────────────────────────────────────────────────────

def _decode_header_str(raw: str) -> str:
    parts = decode_header(raw or "")
    result = ""
    for part, charset in parts:
        if isinstance(part, bytes):
            result += part.decode(charset or "utf-8", errors="ignore")
        else:
            result += part
    return result


def _get_body(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode("utf-8", errors="ignore")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode("utf-8", errors="ignore")
    return ""


def _extract_reply_line(body: str) -> str:
    for line in body.strip().split("\n"):
        stripped = line.strip()
        if stripped.startswith(">") or "wrote:" in stripped or "----" in stripped:
            break
        if stripped:
            return stripped
    return ""


def _now():
    return datetime.now(timezone.utc)


def _parse_timestamp(value):
    if not value:
        return None
    timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp


def _first_topic(topics_text: str) -> str:
    for line in topics_text.split("\n"):
        line = line.strip()
        if line.startswith("1.") or line.startswith("1 "):
            return line[2:].strip().split(":")[0].strip()
    return topics_text.strip()


def _insert_post(trial_id: str, topic: str, post: dict):
    return supabase.table("posts").insert({
        "trial_id": trial_id,
        "topic": topic,
        "facebook_text": post["facebook_text"],
        "linkedin_text": post["linkedin_text"],
        "blog_text": post.get("blog_text", ""),
        "reel_script": post.get("reel_script", ""),
    }).execute().data[0]


def _send_post_and_update(trial: dict, post: dict, cycle: int):
    from email_utils import send_post_email

    send_post_email(trial, post)
    now = _now()
    update = {
        "status": f"cycle_{cycle}_sent",
        "post_sent_at": now.isoformat(),
    }
    if cycle < 3:
        update["next_action_at"] = (now + timedelta(days=2)).isoformat()
    supabase.table("trials").update(update).eq("id", trial["id"]).execute()


def start_trial(trial_id: str):
    """Generate the first post and leave it for admin review."""
    post_id = None
    try:
        from email_utils import send_admin_review_email
        from generate import generate_post_for_trial, pick_topic

        trial = supabase.table("trials").select("*").eq("id", trial_id).single().execute().data
        if not trial:
            return

        topic = pick_topic(trial)
        post = generate_post_for_trial(trial, topic)
        saved_post = _insert_post(trial_id, topic, post)
        post_id = saved_post["id"]

        supabase.table("trials").update({
            "status": "post_1_pending",
            "cycle": 1,
        }).eq("id", trial_id).execute()

        send_admin_review_email(trial, post_id)
    except Exception as e:
        if post_id:
            try:
                supabase.table("posts").delete().eq("id", post_id).execute()
            except Exception as cleanup_error:
                print(f"[flow] failed to clean up post {post_id}: {cleanup_error}")
        try:
            supabase.table("trials").update({"status": "new"}).eq("id", trial_id).execute()
        except Exception as reset_error:
            print(f"[flow] failed to reset trial {trial_id}: {reset_error}")
        print(f"[flow] start trial error for {trial_id}: {e}")


def advance_trials():
    """Advance due trials through the three-post trial cycle."""
    from email_utils import send_admin_completion_email, send_post_email, send_topics_email
    from generate import generate_post_for_trial, suggest_topics

    now = _now()
    rows = supabase.table("trials").select("*").in_("status", [
        "post_1_pending", "cycle_1_sent", "cycle_2_sent", "topics_sent", "cycle_3_sent"
    ]).execute().data or []

    for trial in rows:
        try:
            status = trial.get("status")
            if status == "post_1_pending":
                post = supabase.table("posts").select("*").eq("trial_id", trial["id"]).order("created_at").limit(1).execute().data
                if post and _parse_timestamp(post[0].get("created_at")) and now - _parse_timestamp(post[0]["created_at"]) >= timedelta(hours=12):
                    _send_post_and_update(trial, post[0], 1)
                continue

            next_action_at = _parse_timestamp(trial.get("next_action_at"))
            if status in ("cycle_1_sent", "cycle_2_sent") and next_action_at and next_action_at <= now:
                topics_text = suggest_topics(trial)
                send_topics_email(trial, topics_text, include_auto_pick=True)
                topics = {}
                for line in topics_text.split("\n"):
                    line = line.strip()
                    for number in range(1, 4):
                        if line.startswith(f"{number}.") or line.startswith(f"{number} "):
                            topics[str(number)] = line[2:].strip().split(":")[0].strip()
                            break
                cycle = int(trial.get("cycle") or 1) + 1
                supabase.table("trials").update({
                    "status": "topics_sent",
                    "cycle": cycle,
                    "topics_json": topics,
                    "topics_sent_at": now.isoformat(),
                }).eq("id", trial["id"]).execute()
                continue

            if status == "topics_sent" and _parse_timestamp(trial.get("topics_sent_at")) and now - _parse_timestamp(trial["topics_sent_at"]) >= timedelta(hours=24):
                cycle = int(trial.get("cycle") or 1)
                topic = (trial.get("topics_json") or {}).get("1")
                if not topic:
                    topic = _first_topic(suggest_topics(trial))
                post = generate_post_for_trial(trial, topic)
                _insert_post(trial["id"], topic, post)
                _send_post_and_update(trial, post, cycle)
                continue

            if status == "cycle_3_sent" and _parse_timestamp(trial.get("post_sent_at")) and now - _parse_timestamp(trial["post_sent_at"]) >= timedelta(days=2):
                posts = supabase.table("posts").select("*").eq("trial_id", trial["id"]).order("created_at").execute().data or []
                supabase.table("trials").update({"status": "trial_complete"}).eq("id", trial["id"]).execute()
                send_admin_completion_email(trial, posts)
        except Exception as e:
            print(f"[flow] advance error for {trial.get('email')}: {e}")


# ── main functions ─────────────────────────────────────────────────────────────

def process_new_trials():
    """Send topic suggestions to every trial with status='new'."""
    from generate import suggest_topics
    from email_utils import send_topics_email

    rows = supabase.table("trials").select("*").eq("status", "new").execute()
    trials = rows.data or []
    print(f"[flow] found {len(trials)} new trials")

    for trial in trials:
        try:
            topics_text = suggest_topics(trial)
            send_topics_email(trial, topics_text)

            # Parse numbered topics into a dict for later lookup
            topics_dict = {}
            for line in topics_text.split("\n"):
                line = line.strip()
                for i in range(1, 4):
                    if line.startswith(f"{i}.") or line.startswith(f"{i} "):
                        topic_name = line[2:].strip().split(":")[0].strip()
                        topics_dict[str(i)] = topic_name
                        break

            supabase.table("trials").update({
                "status": "topics_sent",
                "topics_json": topics_dict,
                "topics_sent_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", trial["id"]).execute()

            print(f"[flow] topics sent to {trial['email']}")
        except Exception as e:
            print(f"[flow] error for {trial['email']}: {e}")


def check_replies_and_generate():
    """Scan inbox for replies from trials with status='topics_sent'."""
    from generate import generate_post_for_trial
    from email_utils import send_post_email

    pending = supabase.table("trials").select("*").eq("status", "topics_sent").execute()
    if not pending.data:
        print("[flow] no pending trials")
        return

    pending_by_email = {t["email"]: t for t in pending.data}
    print(f"[flow] checking replies for {len(pending_by_email)} trials")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL, APP_PASSWORD)
    mail.select("inbox")

    since = datetime.now().strftime("%d-%b-%Y")
    _, messages = mail.search(None, f"SINCE {since}")
    email_ids = messages[0].split()
    print(f"[flow] {len(email_ids)} emails in inbox today")

    processed = set()

    for eid in reversed(email_ids):
        _, msg_data = mail.fetch(eid, "(BODY.PEEK[])")
        msg = email_lib.message_from_bytes(msg_data[0][1])

        subject = _decode_header_str(msg.get("Subject", ""))
        sender_raw = msg.get("From", "")
        sender = sender_raw.lower()

        # Extract plain email from "Name <email>" format
        if "<" in sender:
            sender = sender.split("<")[1].rstrip(">").strip()

        if sender not in pending_by_email:
            continue
        if sender in processed:
            continue

        is_reply = any(x in subject for x in ("Re:", "RE:", "re:"))
        is_topic_email = "נושא" in subject or "scriba" in subject.lower()
        if not (is_reply and is_topic_email):
            continue

        body = _get_body(msg)
        reply = _extract_reply_line(body)
        print(f"[flow] reply from {sender}: {repr(reply)}")

        if not reply or "דלג" in reply or "skip" in reply.lower():
            # Generate fresh topics and resend instead of skipping
            try:
                from generate import suggest_topics
                from email_utils import send_topics_email
                trial = pending_by_email[sender]
                new_topics_text = suggest_topics(trial)
                send_topics_email(trial, new_topics_text)
                new_topics_dict = {}
                for line in new_topics_text.split("\n"):
                    line = line.strip()
                    for i in range(1, 4):
                        if line.startswith(f"{i}.") or line.startswith(f"{i} "):
                            new_topics_dict[str(i)] = line[2:].strip().split(":")[0].strip()
                            break
                supabase.table("trials").update({
                    "topics_json": new_topics_dict,
                }).eq("email", sender).execute()
                print(f"[flow] resent fresh topics to {sender} after skip")
            except Exception as e:
                print(f"[flow] resend topics error for {sender}: {e}")
            processed.add(sender)
            continue

        trial = pending_by_email[sender]
        topics_dict = trial.get("topics_json") or {}

        import re
        topic = reply
        num_match = re.search(r"\b([1-3])\b", reply.strip())
        if num_match and topics_dict:
            topic = topics_dict.get(num_match.group(1), reply)

        try:
            post = generate_post_for_trial(trial, topic)
            send_post_email(trial, post)

            supabase.table("posts").insert({
                "trial_id": trial["id"],
                "topic": topic,
                "facebook_text": post["facebook_text"],
                "linkedin_text": post["linkedin_text"],
                "blog_text": post.get("blog_text", ""),
                "reel_script": post.get("reel_script", ""),
            }).execute()

            supabase.table("trials").update({
                "status": f"cycle_{int(trial.get('cycle') or 1)}_sent",
                "chosen_topic": topic,
                "post_sent_at": datetime.now(timezone.utc).isoformat(),
                **({"next_action_at": (_now() + timedelta(days=2)).isoformat()}
                   if int(trial.get("cycle") or 1) < 3 else {}),
            }).eq("id", trial["id"]).execute()

            print(f"[flow] post generated and sent to {sender}")
        except Exception as e:
            print(f"[flow] generation error for {sender}: {e}")

        processed.add(sender)

    mail.logout()
    print(f"[flow] done. processed: {len(processed)}")


def process_single_trial(trial_id: str):
    """Manually trigger topic suggestions for one trial (admin action)."""
    from generate import suggest_topics
    from email_utils import send_topics_email

    row = supabase.table("trials").select("*").eq("id", trial_id).single().execute()
    trial = row.data
    if not trial:
        print(f"[flow] trial {trial_id} not found")
        return

    topics_text = suggest_topics(trial)
    send_topics_email(trial, topics_text)

    topics_dict = {}
    for line in topics_text.split("\n"):
        line = line.strip()
        for i in range(1, 4):
            if line.startswith(f"{i}.") or line.startswith(f"{i} "):
                topic_name = line[2:].strip().split(":")[0].strip()
                topics_dict[str(i)] = topic_name
                break

    supabase.table("trials").update({
        "status": "topics_sent",
        "topics_json": topics_dict,
        "topics_sent_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", trial_id).execute()

    print(f"[flow] manual topics sent to {trial['email']}")
