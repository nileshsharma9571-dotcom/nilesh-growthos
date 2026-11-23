import re
import socket
import subprocess
import os

DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "guerrillamail.com", "10minutemail.com",
    "trashmail.com", "sharklasers.com", "dispostable.com", "fakeinbox.com",
    "scaleapex.in", "growthxlabs.in", "ecomvelocity.in", "omnifunnel.io",
    "skyearthrealty.com", "siyarampanipat.com"
}

MAJOR_VALID_PROVIDERS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.in", "outlook.com",
    "hotmail.com", "icloud.com", "zoho.com", "rediffmail.com"
}

def is_valid_email(email):
    if not email or not isinstance(email, str):
        return False, "Empty or invalid string"

    email = email.strip().lower()
    
    # 1. Regex Syntax Check
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(pattern, email):
        return False, "Invalid email syntax format"

    domain = email.split('@')[1]

    # 2. Check for disposable or known dead domains
    if domain in DISPOSABLE_DOMAINS:
        return False, f"Domain '{domain}' is blocked (synthetic or dead domain)"

    # 3. Major providers are instantly valid
    if domain in MAJOR_VALID_PROVIDERS:
        return True, "Valid major email provider"

    # 4. Check DNS A/AAAA Host Record
    try:
        socket.gethostbyname(domain)
    except Exception:
        return False, f"Domain '{domain}' does not exist or has no DNS records"

    # 5. Check MX record using nslookup
    try:
        cmd = ['nslookup', '-type=mx', domain]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        out = res.stdout.lower()
        if "mail exchanger" in out or "mx preference" in out:
            return True, f"Verified domain with active MX mail exchangers"
        elif "server can't find" in out or "non-existent domain" in out:
            return False, f"Domain '{domain}' has no active MX records"
    except Exception:
        pass

    # Fallback: if domain resolved via DNS
    return True, "Valid domain with active DNS host"

if __name__ == "__main__":
    test_emails = [
        "hr@techtail.in",
        "hiring@prohed.com",
        "careers@girnarsoft.com",
        "info@youdent.in",
        "hr@scaleapex.in",
        "careers@growthxlabs.in",
        "jaijinendradental@gmail.com"
    ]
    for em in test_emails:
        valid, reason = is_valid_email(em)
        print(f"{em} -> Valid: {valid} ({reason})")
