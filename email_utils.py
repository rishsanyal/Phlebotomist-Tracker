import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from typing import Union

from dotenv import load_dotenv

from clinicians import ClinicianStatus

load_dotenv()

SMTP_PORT = 587


def send_email(phlebotomist_id: int, message: str):
    email_sender = "rishabh106@gmail.com"
    email_receiver = ["rishabh106@gmail.com"]
    subject = f"Test SUBJECT #{phlebotomist_id}"
    body = message

    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content(body)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(email_sender, os.getenv("EMAIL_PASSWORD"))
        server.sendmail(email_sender, email_receiver, em.as_string())
        server.close()
        print("successfully sent the mail")
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
