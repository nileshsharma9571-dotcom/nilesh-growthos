import os
import sys
import json
import datetime
import random
import time
import subprocess
import shutil

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
from discovery_engine import discover_fresh_jobs, discover_fresh_leads
from follow_up_engine import process_day3_follow_ups

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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

def run_growth_cycle():
    now = datetime.datetime.now()
    today_str = now.strftime("%b %d, %Y")
    time_str = now.strftime("%I:%M %p")
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
    existing_job_ids = {j["id"] for j in jobs}
    existing_lead_ids = {l["id"] for l in leads}

    # 1. DYNAMIC DISCOVERY: Fresh Opportunities
    print("[1] Discovering fresh digital marketing jobs and local client leads...")
    fresh_jobs = discover_fresh_jobs(existing_job_ids, count=3)
    fresh_leads = discover_fresh_leads(existing_lead_ids, count=3)

    # Prepend new jobs to top
    if fresh_jobs:
        for fj in reversed(fresh_jobs):
            jobs.insert(0, fj)
        save_json(JOBS_FILE, jobs)
        print(f"    [+] Added {len(fresh_jobs)} fresh jobs to jobs.json (Total: {len(jobs)})")
    else:
        print(f"    [*] All current job feeds already indexed.")

    # Prepend new leads to top
    if fresh_leads:
        for fl in reversed(fresh_leads):
            leads.insert(0, fl)
        save_json(LEADS_FILE, leads)
        print(f"    [+] Added {len(fresh_leads)} fresh client leads to leads.json (Total: {len(leads)})")
    else:
        print(f"    [*] All current local business leads already indexed.")

    # 2. DISPATCH TELEGRAM ALERTS: Fresh Jobs
    print("\n[2] Dispatching Telegram notifications to @Nileshgrowth_bot...")
    jobs_notified_count = 0
    for j in jobs[:6]:
        jid = j["id"]
        if jid not in notified_ids:
            is_wfh = j.get("job_category") == "WFH" or "Remote" in j.get("location", "")
            icon = "🏠 [NEW WFH REMOTE JOB]" if is_wfh else "🏢 [NEW NEARBY OFFICE JOB]"
            
            contact_block = ""
            if j.get("is_mobile") and j.get("phone"):
                clean_num = j['phone'].replace('+', '').replace(' ', '')
                contact_block = f"\n💬 WhatsApp Apply: https://wa.me/{clean_num}\n"
            elif j.get("phone"):
                contact_block = f"\n📞 Call Office: tel:{j['phone']}\n"

            msg = (
                f"🔥 {icon} ({j.get('match_score', '90%')} Match)\n\n"
                f"📌 Role: {j.get('title')}\n"
                f"🏢 Company: {j.get('company')}\n"
                f"📍 Location: {j.get('location')}\n"
                f"💰 Salary: {j.get('salary', 'Best in Industry')}\n"
                f"🛠️ Skills: {', '.join(j.get('key_skills', []))}\n\n"
                f"👉 1-Click Direct Apply Link:\n{j.get('apply_link')}{contact_block}\n"
                f"📄 Verified One-Page Resume:\n{RESUME_CLOUD_URL}"
            )
            print(f"    [*] Telegram Alert -> Job: {j.get('title')} ({j.get('company')})")
            if send_telegram_alert(msg):
                notified_ids.add(jid)
                jobs_notified_count += 1
                time.sleep(1)

    # 3. DISPATCH TELEGRAM ALERTS: Fresh Leads
    leads_notified_count = 0
    for l in leads[:6]:
        lid = l["id"]
        if lid not in notified_ids:
            wa_block = ""
            if l.get("is_mobile") and l.get("wa_link"):
                wa_block = f"\n💬 1-Click WhatsApp Pitch:\n{l.get('wa_link')}\n"

            msg = (
                f"💼 [VERIFIED BUSINESS LEAD • GOOGLE REVIEW GAP]\n\n"
                f"🏢 Business: {l.get('business_name')}\n"
                f"📍 Location: {l.get('city')}, {l.get('state')}\n"
                f"⭐ Reviews: {l.get('reviews')}\n"
                f"⚠️ Review Gap: {l.get('audit_problem')}\n"
                f"✨ Solution: {l.get('solution_offered')}\n\n"
                f"📞 Direct Call: tel:{l.get('phone')}{wa_block}"
                f"📍 Google Maps: {l.get('maps_link', 'Available')}"
            )
            print(f"    [*] Telegram Alert -> Client Lead: {l.get('business_name')}")
            if send_telegram_alert(msg):
                notified_ids.add(lid)
                leads_notified_count += 1
                time.sleep(1)

    log_data["notified_telegram"] = list(notified_ids)
    save_json(LOG_FILE, log_data)
    print(f"    [OK] Dispatched {jobs_notified_count} job alerts and {leads_notified_count} lead alerts.")

    # 4. SAFE DRIP EMAIL OUTREACH (Max 1 Job Application + 1 Client Pitch per cycle)
    print("\n[3] Processing Safe Drip Email Outreach...")
    job_email, job_pass, client_email, client_pass = get_env_credentials()

    # Drip 1: Job Application
    job_sent_today = False
    if job_email and job_pass:
        for j in jobs:
            hr_em = j.get("hr_email")
            if hr_em and hr_em not in sent_jobs:
                valid, reason = is_valid_email(hr_em)
                if not valid:
                    continue

                print(f"    [*] Dispatching Job Application to HR: {hr_em} ({j.get('company')})...")
                try:
                    msg = MIMEMultipart()
                    msg['From'] = f"Nilesh Acharya <{job_email}>"
                    msg['To'] = hr_em
                    msg['Subject'] = f"Job Application: {j.get('title')} - Nilesh Acharya ({j.get('match_score', '90%')} Match)"
                    body = j.get("cover_note", "")
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
                    print(f"    [SUCCESS] Job application delivered to {hr_em}!")
                    send_telegram_alert(f"✅ [JOB APPLICATION DELIVERED VIA EMAIL]\n\nRole: {j.get('title')}\nCompany: {j.get('company')}\nHR Email: {hr_em}\nAttached: Nilesh_Acharya_Resume.pdf\nMatch Score: {j.get('match_score')}")
                    job_sent_today = True
                    break
                except Exception as err:
                    print(f"    [ERROR] Failed to send job email to {hr_em}: {err}")
    else:
        print("    [!] Job email credentials not configured; skipping email dispatch.")

    # Drip 2: Client Lead Pitch
    client_sent_today = False
    if client_email and client_pass:
        for l in leads:
            c_em = l.get("email")
            if c_em and c_em not in sent_clients:
                valid, reason = is_valid_email(c_em)
                if not valid:
                    continue

                print(f"    [*] Dispatching Client Pitch to: {c_em} ({l.get('business_name')})...")
                try:
                    msg = MIMEMultipart()
                    msg['From'] = f"Nilesh Acharya (Digital Marketer) <{client_email}>"
                    msg['To'] = c_em
                    msg['Subject'] = f"Radhe Radhe Sir: Digital Growth & WhatsApp Lead Funnel for {l.get('business_name')}"
                    body = l.get("outreach_pitch", "")
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
                    print(f"    [SUCCESS] Client pitch delivered to {c_em}!")
                    send_telegram_alert(f"✅ [CLIENT PITCH DELIVERED VIA EMAIL]\n\nClient: {l.get('business_name')}\nEmail: {c_em}\nCity: {l.get('city')}\nPhone: {l.get('phone')}")
                    client_sent_today = True
                    break
                except Exception as err:
                    print(f"    [ERROR] Failed to send client email to {c_em}: {err}")
    else:
        print("    [!] Client email credentials not configured; skipping email dispatch.")

    # 5. AUTOMATED DAY-3 FOLLOW-UPS
    print("\n[4] Checking Automated Day-3 Follow-ups & Incoming Replies...")
    try:
        followups_sent = process_day3_follow_ups()
        print(f"    [OK] Day-3 follow-ups processed: {followups_sent}")
    except Exception as e:
        print(f"    [!] Follow-up engine notice: {e}")

    # 6. REBUILD DASHBOARD
    print("\n[5] Rebuilding Dashboard HTML & index.html...")
    rebuild_script = os.path.join(BASE_DIR, "build_clean_dashboard.py")
    if os.path.exists(rebuild_script):
        subprocess.run([sys.executable, rebuild_script], check=True)
        print("    [OK] Live dashboard compiled successfully!")

    print(f"\n=======================================================")
    print(f"✅ CYCLE COMPLETE: Growth Engine Finished at {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"=======================================================\n")

if __name__ == "__main__":
    run_growth_cycle()
