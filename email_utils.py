import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from typing import Union

from dotenv import load_dotenv

from clinicians import ClinicianStatus

load_dotenv()

SMTP_PORT = 465


def send_email(phlebotomist_id: int, message: str):
    email_sender = "rishabh106@gmail.com"
    email_receiver = "rsanyal@ucdavis.edu"
    subject = f"Test SUBJECT #{phlebotomist_id}"
    body = message

    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", SMTP_PORT, context=context) as smtp:
            email_password = os.getenv("EMAIL_PASSWORD")
            smtp.login(email_sender, email_password)
            smtp.send_message(em)
            print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


def send_alert(
    phlebotomist_id: int,
    alert_case: Union[ClinicianStatus.ERROR, ClinicianStatus.OUT_OF_BOUNDS],
):
    """
    Send email alert in case of a clinician going out of bounds
    """
    message = f"Phlebotomist #{phlebotomist_id} has exited the designated safety zone as of {datetime.utcnow().isoformat()} UTC."

    # print(message, alert_case)
    send_email(phlebotomist_id, message)
