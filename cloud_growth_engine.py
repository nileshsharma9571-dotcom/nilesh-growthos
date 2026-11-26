import os
import sys
import json
import datetime
import time
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "outreach_log.json")
JOBS_FILE = os.path.join(DATA_DIR, "jobs.json")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
RESUME_PATH = os.path.join(DATA_DIR, "Nilesh_Acharya_Resume.pdf")
RESUME_CLOUD_URL = "https://nileshsharma9571-dotcom.github.io/nilesh-growthos/data/Nilesh_Acharya_Resume.pdf"
ENV_FILE = os.path.join(BASE_DIR, ".env")

from telegram_notifier import send_telegram_alert
from email_verifier import is_valid_email
from discovery_engine import discover_fresh_jobs, discover_fresh_leads, strip_phone_spaces
from follow_up_engine import process_day3_follow_ups

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

def now_ist():
    return datetime.datetime.now(IST)

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

def get_env_credentials():
    job_email = os.environ.get("JOB_EMAIL")
    job_pass = os.environ.get("JOB_APP_PASS")
    client_email = os.environ.get("CLIENT_EMAIL")
    client_pass = os.environ.get("CLIENT_APP_PASS")

    if not (job_email and job_pass and client_email and client_pass):
        if os.path.exists(ENV_FILE):
            try:
                with open(ENV_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("JOB_EMAIL="):
                            job_email = job_email or line.split("=", 1)[1]
                        elif line.startswith("JOB_APP_PASS="):
                            job_pass = job_pass or line.split("=", 1)[1]
                        elif line.startswith("CLIENT_EMAIL="):
                            client_email = client_email or line.split("=", 1)[1]
                        elif line.startswith("CLIENT_APP_PASS="):
                            client_pass = client_pass or line.split("=", 1)[1]
            except Exception:
                pass
    return job_email, job_pass, client_email, client_pass

def count_sent_today(history, rec_type, today_iso_prefix):
    return sum(
        1 for h in history
        if h.get("type") == rec_type and str(h.get("timestamp", "")).startswith(today_iso_prefix)
    )

def run_growth_cycle():
    now = now_ist()
    today_str = now.strftime("%b %d, %Y")
    time_str = now.strftime("%I:%M %p IST")
    today_iso = now.strftime("%Y-%m-%d")

    print(f"\n=======================================================")
    print(f"🚀 NILESH GROWTHOS PRO — RUNNING ENGINE CYCLE")
    print(f"⏰ Execution Time: {today_str} • {time_str}")
    print(f"=======================================================\n")

    log_data = load_json(LOG_FILE, {"sent_clients": [], "sent_jobs": [], "notified_telegram": [], "history": []})
    notified_ids = set(log_data.get("notified_telegram", []))
    sent_jobs = set(log_data.get("sent_jobs", []))
    sent_clients = set(log_data.get("sent_clients", []))

    jobs = load_json(JOBS_FILE, [])
    leads = load_json(LEADS_FILE, [])

    # Clean out irrelevant US-only jobs from previous runs & flatten key_skills
    jobs = [j for j in jobs if "united states" not in j.get("title", "").lower() and "content reviewer" not in j.get("title", "").lower()]
    for j in jobs:
        if isinstance(j.get("key_skills"), list):
            j["key_skills"] = [", ".join(map(str, x)) if isinstance(x, list) else str(x) for x in j["key_skills"]]

    existing_job_ids = {j["id"] for j in jobs}
    existing_lead_ids = {l["id"] for l in leads}

    # 1. DYNAMIC DISCOVERY
    print("[1] Discovering fresh digital marketing jobs & local client leads...")
    fresh_jobs = discover_fresh_jobs(existing_job_ids, count=6)
    fresh_leads = discover_fresh_leads(existing_lead_ids, count=5)

    for fj in fresh_jobs:
        fj["batch_time"] = f"{time_str} • Updated Today ({today_str})"
    for fl in fresh_leads:
        fl["batch_time"] = f"{time_str} • Updated Today ({today_str})"

    if fresh_jobs:
        for fj in reversed(fresh_jobs):
            jobs.insert(0, fj)
        save_json(JOBS_FILE, jobs)
        print(f"    [+] Added {len(fresh_jobs)} fresh jobs (Total: {len(jobs)})")
    else:
        save_json(JOBS_FILE, jobs)
        print("    [*] All current job feeds already indexed.")

    if fresh_leads:
        for fl in reversed(fresh_leads):
            leads.insert(0, fl)
        save_json(LEADS_FILE, leads)
        print(f"    [+] Added {len(fresh_leads)} fresh client leads (Total: {len(leads)})")
    else:
        print("    [*] All current business leads already indexed.")

    # 2. TELEGRAM ALERTS: Fresh Jobs
    print("\n[2] Dispatching Telegram notifications to @Nileshgrowth_bot...")
    jobs_notified_count = 0
    for j in jobs[:8]:
        jid = j["id"]
        if jid not in notified_ids:
            is_wfh = j.get("job_category") == "WFH" or "Remote" in j.get("location", "")
            icon = "🏠 [WFH REMOTE JOB]" if is_wfh else "🏢 [OFFICE JOB]"

            contact_block = ""
            if j.get("hr_email"):
                contact_block += f"\n📧 HR Email: {j.get('hr_email')}"

            msg = (
                f"🔥 {icon} ({j.get('match_score', '92%')} Match)\n\n"
                f"📌 Role: {j.get('title')}\n"
                f"🏢 Company: {j.get('company')}\n"
                f"📍 Location: {j.get('location')}\n"
                f"💰 Salary: {j.get('salary', 'Best in Industry')}\n"
                f"🛠️ Skills: {', '.join(str(s) for s in (j.get('key_skills') or []))}{contact_block}\n\n"
                f"👉 1-Click Direct Apply:\n{j.get('apply_link')}\n\n"
                f"📄 Verified Resume:\n{RESUME_CLOUD_URL}"
            )
            if send_telegram_alert(msg):
                notified_ids.add(jid)
                jobs_notified_count += 1
                time.sleep(0.8)

    # 3. TELEGRAM ALERTS: Fresh Client Leads
    leads_notified_count = 0
    for l in leads[:8]:
        lid = l["id"]
        if lid not in notified_ids:
            clean_tel = strip_phone_spaces(l.get("phone", ""))
            wa_block = ""
            if l.get("wa_verified") and l.get("wa_link"):
                wa_block = f"\n💬 1-Click WhatsApp Pitch (Verified):\n{l.get('wa_link')}\n"
            else:
                wa_block = "\nℹ️ Note: Call number directly or open Google Maps to message.\n"

            email_line = f"\n📧 Email: {l.get('email')}" if l.get("email") else ""

            msg = (
                f"💼 [BUSINESS CLIENT LEAD • REVIEW/GROWTH GAP]\n\n"
                f"🏢 Business: {l.get('business_name')}\n"
                f"📍 Area: {l.get('city')}, {l.get('state')}\n"
                f"⭐ Reviews: {l.get('reviews')}\n"
                f"⚠️ Problem: {l.get('audit_problem')}\n"
                f"✨ Solution: {l.get('solution_offered')}{email_line}\n\n"
                f"📞 Direct Call: tel:{clean_tel}{wa_block}"
                f"📍 Google Maps: {l.get('maps_link', 'Available')}"
            )
            if send_telegram_alert(msg):
                notified_ids.add(lid)
                leads_notified_count += 1
                time.sleep(0.8)

    log_data["notified_telegram"] = list(notified_ids)
    save_json(LOG_FILE, log_data)
    print(f"    [OK] Dispatched {jobs_notified_count} job alerts and {leads_notified_count} lead alerts.")

    # 4. SAFE DRIP EMAIL OUTREACH (Up to 2 Job Apps + 2 Client Pitches per cycle; daily cap 12 each)
    print("\n[3] Processing Safe Drip Email Outreach...")
    job_email, job_pass, client_email, client_pass = get_env_credentials()
    history = log_data.setdefault("history", [])

    jobs_sent_today = count_sent_today(history, "job_application", today_iso)
    clients_sent_today = count_sent_today(history, "client", today_iso)

    jobs_dispatched_now = 0
    if job_email and job_pass and jobs_sent_today < 12:
        for j in jobs:
            if jobs_dispatched_now >= 2:
                break
            hr_em = j.get("hr_email")
            if hr_em and hr_em not in sent_jobs:
                valid, _ = is_valid_email(hr_em)
                if not valid:
                    continue
                print(f"    [*] Sending Job Application -> {hr_em} ({j.get('company')})...")
                try:
                    msg = MIMEMultipart()
                    msg['From'] = f"Nilesh Acharya <{job_email}>"
                    msg['To'] = hr_em
                    msg['Subject'] = f"Job Application: {j.get('title')} - Nilesh Acharya ({j.get('match_score', '92%')} Match)"
                    msg.attach(MIMEText(j.get("cover_note", ""), 'plain', 'utf-8'))

                    if os.path.exists(RESUME_PATH):
                        with open(RESUME_PATH, "rb") as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', 'attachment; filename="Nilesh_Acharya_Resume.pdf"')
                            msg.attach(part)

                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
                    server.login(job_email, job_pass)
                    server.sendmail(job_email, [hr_em], msg.as_string())
                    server.quit()

                    sent_jobs.add(hr_em)
                    log_data.setdefault("sent_jobs", []).append(hr_em)
                    history.append({
                        "timestamp": now.isoformat(),
                        "type": "job_application",
                        "recipient": hr_em,
                        "company": j.get("company"),
                        "title": j.get("title")
                    })
                    save_json(LOG_FILE, log_data)
                    print(f"    [SUCCESS] Job application delivered to {hr_em}!")
                    send_telegram_alert(
                        f"✅ [JOB EMAIL SENT]\n\nRole: {j.get('title')}\nCompany: {j.get('company')}\nHR Email: {hr_em}\nResume: Attached PDF"
                    )
                    jobs_dispatched_now += 1
                    time.sleep(3)
                except Exception as err:
                    print(f"    [ERROR] Job email {hr_em}: {err}")

    clients_dispatched_now = 0
    if client_email and client_pass and clients_sent_today < 12:
        for l in leads:
            if clients_dispatched_now >= 2:
                break
            c_em = l.get("email")
            if c_em and c_em not in sent_clients:
                valid, _ = is_valid_email(c_em)
                if not valid:
                    continue
                print(f"    [*] Sending Client Pitch -> {c_em} ({l.get('business_name')})...")
                try:
                    msg = MIMEMultipart()
                    msg['From'] = f"Nilesh Acharya (Digital Marketer) <{client_email}>"
                    msg['To'] = c_em
                    msg['Subject'] = f"Radhe Radhe Sir: Digital Growth & WhatsApp Lead Funnel for {l.get('business_name')}"
                    msg.attach(MIMEText(l.get("outreach_pitch", ""), 'plain', 'utf-8'))

                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
                    server.login(client_email, client_pass)
                    server.sendmail(client_email, [c_em], msg.as_string())
                    server.quit()

                    sent_clients.add(c_em)
                    log_data.setdefault("sent_clients", []).append(c_em)
                    history.append({
                        "timestamp": now.isoformat(),
                        "type": "client",
                        "recipient": c_em,
                        "business": l.get("business_name")
                    })
                    save_json(LOG_FILE, log_data)
                    print(f"    [SUCCESS] Client pitch delivered to {c_em}!")
                    send_telegram_alert(
                        f"✅ [CLIENT EMAIL SENT]\n\nBusiness: {l.get('business_name')}\nEmail: {c_em}\nCity: {l.get('city')}"
                    )
                    clients_dispatched_now += 1
                    time.sleep(3)
                except Exception as err:
                    print(f"    [ERROR] Client email {c_em}: {err}")

    # 5. DAY-3 FOLLOW-UPS
    print("\n[4] Checking Automated Day-3 Follow-ups...")
    try:
        followups_sent = process_day3_follow_ups()
        print(f"    [OK] Day-3 follow-ups processed: {followups_sent}")
    except Exception as e:
        print(f"    [!] Follow-up notice: {e}")

    # 6. REBUILD DASHBOARD
    print("\n[5] Rebuilding Dashboard HTML & index.html...")
    rebuild_script = os.path.join(BASE_DIR, "build_clean_dashboard.py")
    if os.path.exists(rebuild_script):
        subprocess.run([sys.executable, rebuild_script], check=True)
        print("    [OK] Live dashboard compiled successfully!")

    print(f"\n=======================================================")
    print(f"✅ CYCLE COMPLETE ({now_ist().strftime('%I:%M %p IST')})")
    print(f"=======================================================\n")

if __name__ == "__main__":
    run_growth_cycle()
