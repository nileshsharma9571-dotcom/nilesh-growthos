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

from telegram_notifier import send_telegram_alert
from email_verifier import is_valid_email
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

    # 1. Update Jobs Catalog with Today's Fresh Listings
    jobs = load_json(JOBS_FILE, [])
    leads = load_json(LEADS_FILE, [])

    # Today's high-match opportunities (Nov 23, 2026)
    fresh_jobs_today = [
        {
            "id": "job-23nov-wfh-01",
            "title": "Lead Performance Marketer (Meta & Google Search Ads)",
            "company": "GrowthX Labs India",
            "location": "Remote (Work From Home - All India)",
            "job_category": "WFH",
            "type": "Full-Time (Remote WFH)",
            "experience": "1-3 Years",
            "salary": "₹40,000 - ₹55,000 / month",
            "match_score": "96%",
            "key_skills": ["Meta Ads Manager", "Google Search Ads", "Shopify CRO", "GA4", "WhatsApp Automation"],
            "hr_email": None,
            "phone": None,
            "apply_link": "https://www.linkedin.com/jobs/search/?keywords=Performance+Marketing+Specialist+Remote",
            "wa_apply_text": f"Radhe Radhe Hiring Team 🙏\n\nI am Nilesh Acharya from Kotputli/Jaipur, applying for the Lead Performance Marketer (Remote) role. I hold 9x Google Ads Certifications and Semrush SEO Certification, with hands-on experience scaling Meta Ads & conversion funnels at Leelmax Infotech (Jaipur) and NFPCY Real Estate.\n\n👉 View My Verified PDF Resume: {RESUME_CLOUD_URL}\n\nAvailable immediately with a dedicated remote setup.\nContact: +91 95713 34850 | nileshsharma3011@gmail.com",
            "batch_time": f"12:00 PM • Just Added Today ({today_str})",
            "status": "Ready to Apply (Score 96%)",
            "cover_note": f"Dear Hiring Team,\n\nI am applying for the Lead Performance Marketer (Remote) position. Having managed client ad sets and CRO landing pages at Leelmax Infotech (Jaipur) and NFPCY Real Estate (Neemrana), I focus on driving high-ROI qualified customer acquisitions.\n\nKey Highlights:\n• 9x Google Ads Certifications & Semrush SEO Certified\n• Hands-on with Meta Ads Manager, GA4 attribution, and WhatsApp lead funnels\n• Dedicated high-speed remote home office setup with immediate joining availability\n\nMy updated resume can be viewed here: {RESUME_CLOUD_URL}\n\nWarm regards,\nNilesh Acharya | +91 95713 34850 | nileshsharma3011@gmail.com"
        },
        {
            "id": "job-23nov-office-01",
            "title": "Digital Marketing Executive (Google & Meta Ads)",
            "company": "TechTail Inc.",
            "location": "Jaipur (C-Scheme, Ahinsa Circle)",
            "job_category": "Office",
            "type": "Full-Time (Office)",
            "experience": "1-3 Years",
            "salary": "₹32,000 - ₹48,000 / month",
            "match_score": "95%",
            "key_skills": ["Real Estate Meta Ads", "Google Ads", "WordPress", "Canva", "SEO"],
            "hr_email": "hr@techtail.in",
            "phone": "+91 96800 68393",
            "apply_link": "https://techtail.in",
            "wa_apply_text": f"Radhe Radhe TechTail HR Team 🙏\n\nI am Nilesh Acharya from Kotputli/Jaipur, applying for the Digital Marketing & Real Estate Ads role at TechTail Inc. (C-Scheme, Jaipur). Having handled property marketing and buyer lead funnels for NFPCY Real Estate (Neemrana) and Leelmax Infotech, I bring direct real-estate paid ads experience. 9x Google Certified.\n\n👉 View My Verified PDF Resume: {RESUME_CLOUD_URL}\n\nAvailable for immediate in-person interview in Jaipur.\nMobile: +91 95713 34850 | nileshsharma3011@gmail.com",
            "batch_time": f"11:00 AM • Just Added Today ({today_str})",
            "status": "Ready to Apply (Score 95%)",
            "cover_note": f"Dear TechTail HR Team,\n\nI am writing to apply for the Digital Marketing Executive role at TechTail Inc. (Jaipur). Having managed property lead acquisition at NFPCY Real Estate and agency accounts at Leelmax Infotech (Bhakrota, Jaipur), I bring specialized expertise in Meta Ads targeting premium home & plot buyers.\n\nHighlights:\n• 9x Google Ads Certifications & Semrush SEO Certified\n• Hands-on creative testing, landing page conversion optimization, and WhatsApp lead qualification\n• Based in Kotputli / Jaipur with immediate in-person joining availability\n\nResume link: {RESUME_CLOUD_URL}\n\nSincerely,\nNilesh Acharya | +91 95713 34850 | nileshsharma3011@gmail.com"
        },
        {
            "id": "job-23nov-office-02",
            "title": "PPC & Performance Marketing Executive",
            "company": "PROHED Digital Solutions",
            "location": "Gurugram (Sector 32, Thinkvalley)",
            "job_category": "Office",
            "type": "Full-Time (Office / Hybrid)",
            "experience": "1-3 Years",
            "salary": "₹35,000 - ₹50,000 / month",
            "match_score": "94%",
            "key_skills": ["Google Search Ads", "Meta Lead Ads", "CRO", "Analytics"],
            "hr_email": "hr@prohed.com",
            "phone": "+91 95604 48645",
            "apply_link": "https://prohed.com",
            "wa_apply_text": f"Radhe Radhe PROHED HR Team 🙏\n\nI am Nilesh Acharya, applying for the Performance Marketing role at PROHED Digital Solutions (Sector 32, Gurugram). I specialize in Meta Ads and Google Search Ads campaign scaling (ex-Leelmax Infotech, NFPCY Real Estate). 9x Google Certified.\n\n👉 View My Verified PDF Resume: {RESUME_CLOUD_URL}\n\nProximity to Gurugram with immediate joining readiness.\nMobile: +91 95713 34850 | nileshsharma3011@gmail.com",
            "batch_time": f"10:00 AM • Just Added Today ({today_str})",
            "status": "Ready to Apply (Score 94%)",
            "cover_note": f"Dear PROHED HR Team,\n\nI am excited to apply for the Performance Marketing role in Gurugram. With experience managing performance ad spend and lead generation funnels at Leelmax Infotech and NFPCY Real Estate, I focus on scalable CPA and clean conversion tracking.\n\nQualifications:\n• 9x Google Ads Certifications\n• Hands-on with Meta Ads Manager, GA4, and WordPress CRO\n• Available for immediate joining\n\nResume link: {RESUME_CLOUD_URL}\n\nWarm regards,\nNilesh Acharya | +91 95713 34850 | nileshsharma3011@gmail.com"
        }
    ]

    # Prepend fresh jobs to the existing jobs list (if not present)
    existing_job_ids = {j["id"] for j in jobs}
    new_jobs_added = []
    for fj in reversed(fresh_jobs_today):
        if fj["id"] not in existing_job_ids:
            jobs.insert(0, fj)
            new_jobs_added.append(fj)
            existing_job_ids.add(fj["id"])

    save_json(JOBS_FILE, jobs)
    print(f"[*] Updated jobs catalog. Total jobs: {len(jobs)} ({len(new_jobs_added)} new added)")

    # 2. Dispatch Telegram Alerts for Unnotified Jobs
    for j in jobs[:4]:
        jid = j["id"]
        if jid not in notified_ids:
            is_wfh = j.get("job_category") == "WFH" or "Remote" in j.get("location", "")
            icon = "🏠 [NEW WFH REMOTE JOB]" if is_wfh else "🏢 [NEW NEARBY OFFICE JOB]"
            
            wa_block = ""
            if j.get("phone"):
                wa_block = f"\n💬 WhatsApp Apply: https://wa.me/{j['phone'].replace('+', '').replace(' ', '')}\n"

            msg = (
                f"🔥 {icon} ({j.get('match_score', '90%')} Match)\n\n"
                f"📌 Role: {j.get('title')}\n"
                f"🏢 Company: {j.get('company')}\n"
                f"📍 Location: {j.get('location')}\n"
                f"💰 Salary: {j.get('salary', 'Best in Industry')}\n"
                f"🛠️ Skills: {', '.join(j.get('key_skills', []))}\n\n"
                f"👉 1-Click Direct Apply Link:\n{j.get('apply_link')}{wa_block}\n"
                f"📄 Verified Resume: {RESUME_CLOUD_URL}"
            )
            print(f"[*] Sending Telegram Job Alert -> {j.get('title')} ({j.get('company')})")
            if send_telegram_alert(msg):
                notified_ids.add(jid)
                time.sleep(1)

    # 3. Dispatch Telegram Alerts for Unnotified Leads
    for l in leads[:4]:
        lid = l["id"]
        if lid not in notified_ids:
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
                time.sleep(1)

    # Save notified log
    log_data["notified_telegram"] = list(notified_ids)
    save_json(LOG_FILE, log_data)

    # 4. Safe Drip Email Dispatch (Max 1 Job Application + 1 Client Pitch per cycle)
    profile = load_json(PROFILE_FILE, {})
    job_email = os.environ.get("JOB_EMAIL") or profile.get("credentials", {}).get("job_email")
    job_pass = os.environ.get("JOB_APP_PASS") or profile.get("credentials", {}).get("job_app_password")

    # Find a job with a verified HR email that hasn't been applied to yet
    for j in jobs:
        hr_em = j.get("hr_email")
        if hr_em and hr_em not in sent_jobs:
            valid, reason = is_valid_email(hr_em)
            if valid:
                print(f"[*] Dispatching Email Application to {hr_em} ({j.get('company')})...")
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
                    print(f"[SUCCESS] Email application delivered to {hr_em}!")
                    send_telegram_alert(f"✅ [JOB APPLICATION DISPATCHED VIA EMAIL]\n\nRole: {j.get('title')}\nCompany: {j.get('company')}\nHR Email: {hr_em}\nAttached: Nilesh_Acharya_Resume.pdf\nMatch Score: {j.get('match_score')}")
                    break # Send max 1 per cycle for safe drip pacing
                except Exception as err:
                    print(f"[ERROR] Failed to send job email to {hr_em}: {err}")

    # 5. Rebuild Dashboard HTML
    print("[*] Rebuilding Dashboard HTML...")
    rebuild_script = os.path.join(BASE_DIR, "build_clean_dashboard.py")
    if os.path.exists(rebuild_script):
        subprocess.run([sys.executable, rebuild_script], check=True)
        dash_path = os.path.join(BASE_DIR, "dashboard.html")
        idx_path = os.path.join(BASE_DIR, "index.html")
        shutil.copyfile(dash_path, idx_path)
        print("[OK] Dashboard HTML and index.html rebuilt successfully!")

    print(f"\n[DONE] Growth Engine Cycle Completed Successfully at {datetime.datetime.now().strftime('%H:%M:%S')}!\n")

if __name__ == "__main__":
    run_growth_cycle()
