import smtplib
import imaplib
import email
from email.header import decode_header
import json
import os
import re
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from telegram_notifier import send_telegram_alert

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "outreach_log.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_credentials():
    client_email = os.environ.get("CLIENT_EMAIL")
    client_pass = os.environ.get("CLIENT_APP_PASS")
    
    if not client_email or not client_pass:
        if os.path.exists(ENV_FILE):
            try:
                with open(ENV_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("CLIENT_EMAIL="):
                            client_email = client_email or line.split("=", 1)[1]
                        elif line.startswith("CLIENT_APP_PASS="):
                            client_pass = client_pass or line.split("=", 1)[1]
            except Exception:
                pass
    return client_email, client_pass

def check_incoming_replies(user_email, app_password):
    """Checks the IMAP inbox for any email replies from contacted clients/jobs."""
    replied_senders = set()
    if not user_email or not app_password:
        return replied_senders

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user_email, app_password)
        mail.select("inbox")

        status, data = mail.search(None, "ALL")
        if status == "OK" and data[0]:
            msg_ids = data[0].split()
            for mid in msg_ids[-30:]:
                _, msg_data = mail.fetch(mid, "(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])")
                if msg_data and isinstance(msg_data[0], tuple):
                    header_text = msg_data[0][1].decode('utf-8', errors='ignore')
                    for line in header_text.split('\n'):
                        if line.lower().startswith('from:'):
                            sender_raw = line[5:].strip()
                            emails_found = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', sender_raw)
                            system_domains = {"google.com", "googlemail.com", "gmail.com", "github.com", "telegram.org"}
                            system_prefixes = ("no-reply", "noreply", "mailer-daemon", "postmaster", "notification", "security")
                            for em in emails_found:
                                em_lower = em.lower()
                                em_user = em_lower.split("@")[0]
                                em_dom = em_lower.split("@")[1] if "@" in em_lower else ""
                                if any(em_user.startswith(p) for p in system_prefixes):
                                    continue
                                if em_dom in {"accounts.google.com", "googlemail.com"}:
                                    continue
                                replied_senders.add(em_lower)
        mail.logout()
    except Exception as e:
        print(f"[IMAP NOTICE] Check for {user_email}: {e}")

    return replied_senders

def process_day3_follow_ups():
    client_email, client_pass = get_credentials()
    profile = load_json(PROFILE_FILE, {})
    log_data = load_json(LOG_FILE, {"replied_contacts": [], "followed_up": [], "history": []})
    phone = profile.get("contact", {}).get("phone", "+91 95713 34850")

    if not client_email or not client_pass:
        print("[FOLLOW-UP] Client email credentials not available; skipping automated IMAP check.")
        return 0

    # 1. Fetch live incoming replies
    replied_senders = check_incoming_replies(client_email, client_pass)
    log_data.setdefault("replied_contacts", [])
    for rep in replied_senders:
        if rep not in log_data["replied_contacts"]:
            log_data["replied_contacts"].append(rep)
            print(f"🎉 NEW CLIENT REPLY DETECTED FROM: {rep}")
            send_telegram_alert(f"🎉 [NEW CLIENT EMAIL REPLY RECEIVED!]\n\nClient Email: {rep}\nCheck your inbox: {client_email}")

    save_json(LOG_FILE, log_data)

    # 2. Check history for contacts sent >= 3 days ago without reply or follow-up
    now = datetime.datetime.now()
    log_data.setdefault("followed_up", [])
    history = log_data.get("history", [])

    followups_sent = 0
    for record in history:
        recipient = record.get("recipient")
        rec_type = record.get("type")
        timestamp_str = record.get("timestamp")

        if not recipient or rec_type != "client":
            continue

        if recipient in log_data["replied_contacts"] or recipient in log_data["followed_up"]:
            continue

        try:
            sent_time = datetime.datetime.fromisoformat(timestamp_str).replace(tzinfo=None)
            days_passed = (now - sent_time).days

            # Send Day 3 follow-up
            if days_passed >= 3:
                business = record.get("business", "Business")
                subject = f"Radhe Radhe Sir: Quick Follow-up regarding Digital Growth for {business}"
                body = (
                    f"Radhe Radhe Sir 🙏\n\n"
                    f"Mera naam Nilesh Acharya hai. Maine 3 din pehle aapko {business} ke liye website aur automated WhatsApp lead booking funnel ke regarding ek short proposal bheja tha.\n\n"
                    f"Sir, main janta hu aap busy rehte hain. Main bas ye check karna chahta tha ki kya aapne wo message dekha tha?\n\n"
                    f"Agar aap free hon, to hum is hafte 5 minute phone par connect kar sakte hain jisme main aapko ek brief demo share kar dunga ki kaise local area se verified inquiries scale kar sakte hain.\n\n"
                    f"Direct Call / WhatsApp: {phone}\n"
                    f"Radhe Radhe 🙏\n"
                    f"Nilesh Acharya | Digital Marketer\n"
                    f"Kotputli, Jaipur, Rajasthan\n"
                )
                msg = MIMEMultipart()
                msg['From'] = f"Nilesh Acharya <{client_email}>"
                msg['To'] = recipient
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                server.login(client_email, client_pass)
                server.sendmail(client_email, [recipient], msg.as_string())
                server.quit()

                log_data["followed_up"].append(recipient)
                followups_sent += 1
                print(f"[FOLLOW-UP SENT] Successfully sent Day-3 follow-up to {business} ({recipient})")
                send_telegram_alert(f"📤 [DAY-3 FOLLOW-UP DELIVERED]\n\nBusiness: {business}\nEmail: {recipient}\nSender: {client_email}")
                save_json(LOG_FILE, log_data)
        except Exception as e:
            print(f"Error checking follow-up for {recipient}: {e}")

    print(f"Follow-up check completed. Follow-ups dispatched today: {followups_sent}")
    return followups_sent

if __name__ == "__main__":
    process_day3_follow_ups()
