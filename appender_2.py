import imaplib
import time
import requests
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import format_datetime
from concurrent.futures import ThreadPoolExecutor

SUPABASE_URL = "https://uryfrvpoyhrzfgctupqk.supabase.co"
MAX_THREADS = 5  # Adjust this based on how many concurrent operations you want

PARAMS = {
    "table": "t_online_de_valid",
    "offer_id": "4",
    "from_email": "free-iptv@meetoffer.online",
    "from_name": "Free Premium IPTV"
}

def process_imap_append(data):
    """Handles the email compilation and IMAP appending for a single record."""
    email_to = None
    try:
        email_to = data['email_to']
        password = data['password']
        imap = data['imap']
        port = data['port']
        from_email = data['from_email']
        from_name = data['name']
        subject = data['subject']
        msg_body = data['msg_body']
        
        # Create email
        msg = EmailMessage()
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = email_to
        msg["Subject"] = subject
        msg["Date"] = format_datetime(datetime.now(timezone.utc))

        # HTML body
        msg.set_content("Please view this email in an HTML-capable email client.")
        msg.add_alternative(msg_body, subtype="html")

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
        print(f"success : {email_to}")

    except Exception as e:
        print(f"error handling {email_to or 'Unknown Email'}: {e}")

def main():
    # ThreadPoolExecutor manages worker threads efficiently
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        while True:
            response = None
            try:
                # 1. Fetch a job from the database sequentially in the main thread
                response = requests.get(
                    f"{SUPABASE_URL}/functions/v1/imap_append",
                    params=PARAMS,
                    timeout=30
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
                time.sleep(0.5)

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
