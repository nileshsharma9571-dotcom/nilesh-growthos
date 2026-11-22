import smtplib
import json
import os
import time
import datetime
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "outreach_log.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
LEADS_FILE = os.path.join(DATA_DIR, "leads.json")
JOBS_FILE = os.path.join(DATA_DIR, "jobs.json")
RESUME_PATH = os.path.join(DATA_DIR, "Nilesh_Acharya_Resume.pdf")

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

from email_verifier import is_valid_email
from follow_up_engine import process_day3_follow_ups
from telegram_notifier import send_telegram_alert

def send_client_pitch(lead, profile, log_data):
    recipient = lead.get("email")
    if not recipient:
        return False, "No email address found"
    
    # Pre-send validation check to eliminate fake/dead emails
    valid, reason = is_valid_email(recipient)
    if not valid:
        print(f"[VERIFY SKIP] Skipping invalid email {recipient}: {reason}")
        log_data.setdefault("invalid_emails", []).append({"email": recipient, "reason": reason})
        save_json(LOG_FILE, log_data)
        return False, f"Email verification failed: {reason}"
    
    if recipient in log_data.get("sent_clients", []):
        return False, f"Already sent to {recipient}"

    client_email = os.environ.get("CLIENT_EMAIL") or profile.get("credentials", {}).get("client_email")
    client_pass = os.environ.get("CLIENT_APP_PASS") or profile.get("credentials", {}).get("client_app_password")
    phone = profile.get("contact", {}).get("phone", "+91 95713 34850")

    msg = MIMEMultipart()
    msg['From'] = f"Nilesh Acharya (Digital Marketer) <{client_email}>"
    msg['To'] = recipient
    msg['Subject'] = lead.get("email_subject", f"Radhe Radhe Sir: Digital Growth Funnel for {lead.get('business_name')}")

    body = lead.get("email_body", lead.get("outreach_pitch", ""))
    # Ensure phone number is explicitly present in the signature
    if phone not in body:
        body += f"\n\nDirect Call / WhatsApp: {phone}\nNilesh Acharya | Kotputli, Jaipur"

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(client_email, client_pass)
        server.sendmail(client_email, [recipient], msg.as_string())
        server.quit()

        log_data.setdefault("sent_clients", []).append(recipient)
        log_data.setdefault("history", []).append({
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "client",
            "recipient": recipient,
            "business": lead.get("business_name")
        })
        save_json(LOG_FILE, log_data)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] CLIENT EMAIL SENT -> {lead.get('business_name')} ({recipient})")
        send_telegram_alert(f"✅ [EMAIL PITCH DISPATCHED]\n\nClient: {lead.get('business_name')} ({lead.get('city')})\nEmail: {recipient}\nPitch: Automated Lead Funnel\n\nDirect WhatsApp: {lead.get('wa_link')}")
        return True, "Success"
    except Exception as e:
        print(f"[CLIENT ERROR] Failed {recipient}: {e}")
        return False, str(e)

def send_job_application(job, profile, log_data):
    recipient = job.get("hr_email")
    if not recipient:
        return False, "No HR email address found"
    
    # Pre-send validation check
    valid, reason = is_valid_email(recipient)
    if not valid:
        print(f"[VERIFY SKIP] Skipping invalid HR email {recipient}: {reason}")
        log_data.setdefault("invalid_emails", []).append({"email": recipient, "reason": reason})
        save_json(LOG_FILE, log_data)
        return False, f"HR email verification failed: {reason}"
    
    if recipient in log_data.get("sent_jobs", []):
        return False, f"Already applied to {recipient}"

    job_email = os.environ.get("JOB_EMAIL") or profile.get("credentials", {}).get("job_email")
    job_pass = os.environ.get("JOB_APP_PASS") or profile.get("credentials", {}).get("job_app_password")
    phone = profile.get("contact", {}).get("phone", "+91 95713 34850")

    msg = MIMEMultipart()
    msg['From'] = f"Nilesh Acharya <{job_email}>"
    msg['To'] = recipient
    msg['Subject'] = f"Job Application: {job.get('title')} - Nilesh Acharya ({job.get('match_score', '90%')} Match)"

    body = job.get("cover_note", "")
    if phone not in body:
        body += f"\n\nMobile: {phone} | Location: Kotputli, Jaipur (Immediate Joiner)"

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Attach verified PDF resume
    if os.path.exists(RESUME_PATH):
        with open(RESUME_PATH, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="Nilesh_Acharya_Resume.pdf"')
            msg.attach(part)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(job_email, job_pass)
        server.sendmail(job_email, [recipient], msg.as_string())
        server.quit()

        log_data.setdefault("sent_jobs", []).append(recipient)
        log_data.setdefault("history", []).append({
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "job",
            "recipient": recipient,
            "role": job.get("title"),
            "company": job.get("company")
        })
        save_json(LOG_FILE, log_data)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] JOB APPLICATION SENT -> {job.get('company')} ({recipient}) [Resume Attached]")
        send_telegram_alert(f"🚀 [JOB APPLICATION SUBMITTED]\n\nRole: {job.get('title')} ({job.get('match_score', '90%')} Match)\nCompany: {job.get('company')}\nLocation: {job.get('location')}\nResume: Nilesh_Acharya_Resume.pdf Attached!\nApply Link: {job.get('apply_link')}")
        return True, "Success"
    except Exception as e:
        print(f"[JOB ERROR] Failed {recipient}: {e}")
        return False, str(e)

def run_drip_scheduler():
    profile = load_json(PROFILE_FILE, {})
    log_data = load_json(LOG_FILE, {})

    print("==================================================")
    print(" GrowthOS Smart Drip Outreach Engine Active ")
    print(f" Sender 1 (Clients): {profile.get('credentials', {}).get('client_email')}")
    print(f" Sender 2 (Jobs):    {profile.get('credentials', {}).get('job_email')}")
    print(f" Contact Phone:      {profile.get('contact', {}).get('phone')}")
    print(" Working Window:     09:30 AM to 07:00 PM IST")
    print(" Drip Pacing:        1 Email every 30-45 minutes")
    print("==================================================")

    # Process next eligible client
    leads = load_json(LEADS_FILE, [])
    client_sent = False
    for lead in leads:
        if lead.get("email") and lead.get("email") not in log_data.get("sent_clients", []):
            success, msg = send_client_pitch(lead, profile, log_data)
            if success:
                client_sent = True
                break

    # Process next eligible job application
    jobs = load_json(JOBS_FILE, [])
    job_sent = False
    for job in jobs:
        if job.get("hr_email") and job.get("hr_email") not in log_data.get("sent_jobs", []):
            success, msg = send_job_application(job, profile, log_data)
            if success:
                job_sent = True
                break

    return client_sent, job_sent

if __name__ == "__main__":
    run_drip_scheduler()
