import imaplib
import email

def fetch_emails(username, password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(username, password)
    mail.select('inbox')

    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].split()

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, '(RFC822)')
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        print("Subject:", email_message['subject'])
        print("From:", email_message['from'])

        print("-" * 50)

fetch_emails('oindri1301@gmail.com', 'kiyo uvxe jdrg fllm')
