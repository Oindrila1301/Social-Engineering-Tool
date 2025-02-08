import imaplib
import email

def fetch_emails(username, password):
    # Connect to Gmail's IMAP server
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(username, password)
    mail.select('inbox')

    # Search for all emails
    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, '(RFC822)')  # Fetch the email
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)  # Parse the email

        # Extract subject and sender
        subject = email_message["subject"]
        sender = email_message["from"]

        # Extract email body (handling plain text and HTML)
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True).decode()
                    break  # Get first text/plain part
        else:
            body = email_message.get_payload(decode=True).decode()

        # Print email details
        print(f"Subject: {subject}")
        print(f"From: {sender}")
        print("Body:", body)
        print("-" * 50)

# Use your App Password
fetch_emails('oindri1301@gmail.com', 'kiyo uvxe jdrg fllm')
