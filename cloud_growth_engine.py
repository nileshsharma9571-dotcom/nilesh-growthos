import os
import sys
import json
import datetime
import random
import time
import subprocess
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "outreach_log.json")
JOBS_FILE = os.path.join(DATA_DIR, "jobs.json")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.json")
RESUME_PATH = os.path.join(DATA_DIR, "Nilesh_Acharya_Resume.pdf")
RESUME_CLOUD_URL = "https://nileshsharma9571-dotcom.github.io/nilesh-growthos/data/Nilesh_Acharya_Resume.pdf"

from telegram_notifier import send_telegram_alert
from email_verifier import is_valid_email

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
    creds = {
        "job_email": os.environ.get("JOB_EMAIL"),
        "job_pass": os.environ.get("JOB_APP_PASS"),
        "client_email": os.environ.get("CLIENT_EMAIL"),
        "client_pass": os.environ.get("CLIENT_APP_PASS")
    }
    if (not creds["job_email"] or not creds["client_email"]) and os.path.exists(CREDENTIALS_FILE):
        local_creds = load_json(CREDENTIALS_FILE, {})
        creds["job_email"] = creds["job_email"] or local_creds.get("job_email")
        creds["job_pass"] = creds["job_pass"] or local_creds.get("job_app_password")
        creds["client_email"] = creds["client_email"] or local_creds.get("client_email")
        creds["client_pass"] = creds["client_pass"] or local_creds.get("client_app_password")

    return creds

def run_growth_cycle():
    now = datetime.datetime.now()
    today_str = now.strftime("%b %d, %Y")
    time_str = now.strftime("%I:%M %p")
    print(f"\n=======================================================")
    print(f"🚀 RUNNING GROWTH ENGINE CYCLE: {today_str} • {time_str}")
    print(f"=======================================================\n")

    log_data = load_json(LOG_FILE, {"sent_clients": [], "sent_jobs": [], "notified_telegram": [], "history": []})
    notified_ids = set(log_data.get("notified_telegram", []))
    sent_jobs = set(log_data.get("sent_jobs", []))
    sent_clients = set(log_data.get("sent_clients", []))

    jobs = load_json(JOBS_FILE, [])
    leads = load_json(LEADS_FILE, [])
    profile = load_json(PROFILE_FILE, {})
    creds = get_credentials()

    job_email = creds.get("job_email")
    job_pass = creds.get("job_pass")
    client_email = creds.get("client_email")
    client_pass = creds.get("client_pass")
    phone = profile.get("contact", {}).get("phone", "+91 95713 34850")

    # 1. Dispatch Telegram Alerts for Unnotified Jobs (max 2 per cycle)
    telegram_jobs_sent = 0
    for j in jobs:
        jid = j["id"]
        if jid not in notified_ids and telegram_jobs_sent < 2:
            is_wfh = j.get("job_category") == "WFH" or "Remote" in j.get("location", "")
            icon = "🏠 [NEW WFH REMOTE JOB]" if is_wfh else "🏢 [NEW NEARBY OFFICE JOB]"
            
            wa_block = ""
            if j.get("phone"):
                wa_phone = j['phone'].replace('+', '').replace(' ', '')
                wa_block = f"\n💬 WhatsApp: https://wa.me/{wa_phone}"

            msg = (
                f"🔥 {icon} ({j.get('match_score', '90%')} Match)\n\n"
                f"📌 Role: {j.get('title')}\n"
                f"🏢 Company: {j.get('company')}\n"
                f"📍 Location: {j.get('location')}\n"
                f"💰 Salary: {j.get('salary', 'Best in Industry')}\n"
                f"🛠️ Skills: {', '.join(j.get('key_skills', []))}\n\n"
                f"👉 Direct Apply Link:\n{j.get('apply_link')}{wa_block}\n"
                f"📄 Verified Resume: {RESUME_CLOUD_URL}"
            )
            print(f"[*] Sending Telegram Job Alert -> {j.get('title')} ({j.get('company')})")
            if send_telegram_alert(msg):
                notified_ids.add(jid)
                telegram_jobs_sent += 1
                time.sleep(1)

    # 2. Dispatch Telegram Alerts for Unnotified Leads (max 2 per cycle)
    telegram_leads_sent = 0
    for l in leads:
        lid = l["id"]
        if lid not in notified_ids and telegram_leads_sent < 2:
            msg = (
                f"💼 [VERIFIED BUSINESS LEAD • GOOGLE REVIEW GAP]\n\n"
                f"🏢 Business: {l.get('business_name')}\n"
                f"📍 Location: {l.get('city')}, {l.get('state')}\n"
                f"⭐ Reviews: {l.get('reviews')}\n"
                f"⚠️ Review Gap: {l.get('audit_problem')}\n"
                f"✨ Solution: {l.get('solution_offered')}\n\n"
                f"📞 Direct Call: tel:{l.get('phone')}\n"
                f"💬 1-Click WhatsApp Pitch:\n{l.get('wa_link')}\n"
                f"📍 Google Maps: {l.get('maps_link', 'Available')}"
            )
            print(f"[*] Sending Telegram Lead Alert -> {l.get('business_name')}")
            if send_telegram_alert(msg):
                notified_ids.add(lid)
                telegram_leads_sent += 1
                time.sleep(1)

    log_data["notified_telegram"] = list(notified_ids)
    save_json(LOG_FILE, log_data)

    # 3. Safe Drip Job Application (Max 1 Job per cycle from job_email)
    if job_email and job_pass:
        for j in jobs:
            hr_em = j.get("hr_email")
            if hr_em and hr_em not in sent_jobs:
                valid, reason = is_valid_email(hr_em)
                if not valid:
                    print(f"[VERIFY SKIP] Skipping invalid job email {hr_em}: {reason}")
                    continue

                print(f"[*] Dispatching Email Application to {hr_em} ({j.get('company')})...")
                try:
                    msg = MIMEMultipart()
                    msg['From'] = f"Nilesh Acharya <{job_email}>"
                    msg['To'] = hr_em
                    msg['Subject'] = f"Job Application: {j.get('title')} - Nilesh Acharya ({j.get('match_score', '90%')} Match)"
                    body = j.get("cover_note", "")
                    if phone not in body:
                        body += f"\n\nMobile: {phone} | Kotputli, Jaipur (Immediate Joiner)"
                    msg.attach(MIMEText(body, 'plain', 'utf-8'))

                    if os.path.exists(RESUME_PATH):
                        with open(RESUME_PATH, "rb") as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', 'attachment; filename="Nilesh_Acharya_Resume.pdf"')
                            msg.attach(part)

                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(job_email, job_pass)
                    server.sendmail(job_email, [hr_em], msg.as_string())
                    server.quit()

                    sent_jobs.add(hr_em)
                    log_data.setdefault("sent_jobs", []).append(hr_em)
                    log_data.setdefault("history", []).append({
                        "timestamp": now.isoformat(),
                        "type": "job_application",
                        "recipient": hr_em,
                        "company": j.get("company"),
                        "title": j.get("title")
                    })
                    save_json(LOG_FILE, log_data)
                    print(f"[SUCCESS] Email application delivered to {hr_em}!")
                    send_telegram_alert(f"✅ [JOB APPLICATION SUBMITTED VIA EMAIL]\n\nRole: {j.get('title')}\nCompany: {j.get('company')}\nHR Email: {hr_em}\nAttached: Nilesh_Acharya_Resume.pdf\nMatch Score: {j.get('match_score')}")
                    break # Max 1 per cycle
                except Exception as err:
                    print(f"[ERROR] Failed to send job email to {hr_em}: {err}")

    # 4. Safe Drip Client Outreach (Max 1 Client per cycle from client_email)
    if client_email and client_pass:
        for l in leads:
            c_em = l.get("email")
            if c_em and c_em not in sent_clients:
                valid, reason = is_valid_email(c_em)
                if not valid:
                    print(f"[VERIFY SKIP] Skipping invalid client email {c_em}: {reason}")
                    continue

                print(f"[*] Dispatching Client Pitch to {c_em} ({l.get('business_name')})...")
                try:
                    msg = MIMEMultipart()
                    msg['From'] = f"Nilesh Acharya (Digital Marketer) <{client_email}>"
                    msg['To'] = c_em
                    msg['Subject'] = f"Radhe Radhe Sir: Digital Growth Funnel for {l.get('business_name')}"
                    body = l.get("outreach_pitch", "")
                    if phone not in body:
                        body += f"\n\nDirect Call / WhatsApp: {phone}\nNilesh Acharya | Kotputli, Jaipur"
                    msg.attach(MIMEText(body, 'plain', 'utf-8'))

                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.login(client_email, client_pass)
                    server.sendmail(client_email, [c_em], msg.as_string())
                    server.quit()

                    sent_clients.add(c_em)
                    log_data.setdefault("sent_clients", []).append(c_em)
                    log_data.setdefault("history", []).append({
                        "timestamp": now.isoformat(),
                        "type": "client",
                        "recipient": c_em,
                        "business": l.get("business_name")
                    })
                    save_json(LOG_FILE, log_data)
                    print(f"[SUCCESS] Client pitch delivered to {c_em}!")
                    send_telegram_alert(f"📧 [CLIENT EMAIL PITCH DISPATCHED]\n\nClient: {l.get('business_name')} ({l.get('city')})\nEmail: {c_em}\nSender: {client_email}\nDirect WhatsApp: {l.get('wa_link')}")
                    break # Max 1 per cycle
                except Exception as err:
                    print(f"[ERROR] Failed to send client email to {c_em}: {err}")

    # 5. Rebuild Clean Dashboard
    print("[*] Rebuilding Dashboard HTML...")
    rebuild_script = os.path.join(BASE_DIR, "build_clean_dashboard.py")
    if os.path.exists(rebuild_script):
        subprocess.run([sys.executable, rebuild_script], check=True)
        dash_path = os.path.join(BASE_DIR, "dashboard.html")
        idx_path = os.path.join(BASE_DIR, "index.html")
        if os.path.exists(dash_path):
            shutil.copyfile(dash_path, idx_path)
            print("[OK] Dashboard HTML and index.html rebuilt successfully!")

    print(f"\n[DONE] Growth Engine Cycle Completed Successfully at {datetime.datetime.now().strftime('%H:%M:%S')}!\n")

if __name__ == "__main__":
    run_growth_cycle()
