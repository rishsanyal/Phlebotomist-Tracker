import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from typing import Union

from dotenv import load_dotenv

from app_logger import logger
from clinicians import ClinicianStatus

load_dotenv()

# Default GMAIL SMPT Port
SMTP_PORT = 587


def send_email(clinician_id: int, message: str):
    """Helper function to send email alerts"""

    email_sender = "rishabh106@gmail.com"
    email_receiver = [
        "uvm7mv+dia8vb7bofnr8@sharklasers.com",
        "coding-challenges+alerts@sprinterhealth.com",
    ]

    subject = f"Clinician Update: #{clinician_id}"
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
        logger.info("successfully sent the mail")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


def send_alert(
    clinician_id: int,
    alert_case: Union[ClinicianStatus.ERROR, ClinicianStatus.OUT_OF_BOUNDS],
):
    """
    Helper function to send email alerts according the the error case
    """

    match alert_case:
        case ClinicianStatus.ERROR:
            message = f"Unable to obtain the location for Phlebotomist #{clinician_id} as of {datetime.now(datetime.timezone.utc).isoformat()} UTC."

        case ClinicianStatus.OUT_OF_BOUNDS:
            message = f"Phlebotomist #{clinician_id} has exited the their bounds as of {datetime.now(datetime.timezone.utc).isoformat()} UTC."

    send_email(clinician_id, message)
