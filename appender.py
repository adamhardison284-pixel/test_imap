import imaplib
import time
import requests
from datetime import datetime, timezone

import json
from email.message import EmailMessage
from email.utils import format_datetime

"""
python appender_github.py
"""

SUPABASE_URL = "https://uryfrvpoyhrzfgctupqk.supabase.co"

params = {
    "table": "t_online_de_valid",
    "offer_id": "4",
    "from_email": "free-iptv@meetoffer.online",
    "from_name": "Free Premium IPTV "
}
while True:
    response = None
    email_to = None
    while True:
        try:
            response = requests.get(
                f"{SUPABASE_URL}/functions/v1/imap_append",
                params=params,
                timeout=60
            )
            break
        except:
            pass

    try:
        data = response.json()['result']
        email_to = data['email_to']
        password = data['password']
        imap = data['imap']
        port = data['port']
        from_email = data['from_email']
        from_name = data['name']
        subject = data['subject']
        msg_body = data['msg_body']
        
        # Decode \u003C, \u003E, etc.
        html = msg_body

        # Create email
        msg = EmailMessage()

        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = email_to
        msg["Subject"] = subject
        msg["Date"] = format_datetime(datetime.now(timezone.utc))

        # HTML body
        msg.set_content("Please view this email in an HTML-capable email client.")
        msg.add_alternative(html, subtype="html")

        # Connect to IMAP
        mail = imaplib.IMAP4_SSL(imap, port)
        mail.login(email_to, password)

        # Append to Inbox
        status, data = mail.append(
            "INBOX",
            None,
            imaplib.Time2Internaldate(datetime.now(timezone.utc)),
            msg.as_bytes()
        )
        
        mail.logout()
        print("success :", email_to)

    except requests.exceptions.JSONDecodeError:
        print("error :", email_to)
        print("Response is not valid JSON:")
        print(response.text)
    time.sleep(2)
    
