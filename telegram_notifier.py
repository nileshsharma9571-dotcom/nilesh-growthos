import subprocess
import json
import os
import shutil
import urllib.request
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "data", "telegram_config.json")

def send_telegram_alert(message):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    cfg = json.load(f)
                    token = token or cfg.get("bot_token")
                    chat_id = chat_id or cfg.get("chat_id")
            except Exception:
                pass

    if not token or not chat_id:
        print("[TELEGRAM] Missing bot token or chat_id.")
        return False

    cmd = [
        'curl.exe', '-4', '-s',
        f'https://api.telegram.org/bot{token}/sendMessage',
        '-d', f'chat_id={chat_id}',
        '--data-urlencode', f'text={message}'
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return '"ok":true' in res.stdout
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")
        return False

def notify_new_job(job):
    is_wfh = job.get("job_category") == "WFH" or "Remote" in job.get("location", "")
    icon = "🏠 [WFH REMOTE JOB]" if is_wfh else "🏢 [NEARBY OFFICE JOB]"
    
    text = (
        f"🔥 {icon} ({job.get('match_score', '90%')} Match)\n\n"
        f"📌 Role: {job.get('title')}\n"
        f"🏢 Company: {job.get('company')}\n"
        f"📍 Location: {job.get('location')}\n"
        f"💰 Salary: {job.get('salary', 'Best in Industry')}\n"
        f"🛠️ Skills: {', '.join(job.get('key_skills', []))}\n\n"
        f"👉 1-Click Direct Apply Link:\n{job.get('apply_link')}"
    )
    return send_telegram_alert(text)

def notify_new_lead(lead):
    text = (
        f"💼 [NEW REVIEW GAP BUSINESS LEAD]\n\n"
        f"🏢 Business: {lead.get('business_name')}\n"
        f"📍 Location: {lead.get('city')}, {lead.get('state')}\n"
        f"⭐ Reviews: {lead.get('reviews')}\n"
        f"⚠️ Digital Gap: {lead.get('audit_problem')}\n"
        f"✨ Solution: {lead.get('solution_offered')}\n\n"
        f"📞 Direct Call: tel:{lead.get('phone')}\n"
        f"💬 1-Click WhatsApp Chat:\n{lead.get('wa_link')}"
    )
    return send_telegram_alert(text)

if __name__ == "__main__":
    print("Telegram notifier module ready.")
