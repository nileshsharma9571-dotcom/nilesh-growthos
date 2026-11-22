import re
import socket

DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "guerrillamail.com", "10minutemail.com",
    "trashmail.com", "sharklasers.com", "dispostable.com", "fakeinbox.com"
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

    # 2. Check for disposable/throwaway domains
    if domain in DISPOSABLE_DOMAINS:
        return False, "Disposable or temporary email domain"

    # 3. DNS Host Check (Domain must exist and resolve to an IP)
    try:
        socket.gethostbyname(domain)
    except Exception:
        return False, f"Domain '{domain}' does not exist or has no DNS records"

    return True, "Valid and active domain"

if __name__ == "__main__":
    test_emails = [
        "dr.sharma.apexjaipur@gmail.com",
        "fakeuser@fake123abcxyz99.com",
        "user@mailinator.com",
        "invalid-email-format"
    ]
    for em in test_emails:
        valid, reason = is_valid_email(em)
        print(f"{em} -> Valid: {valid} ({reason})")
