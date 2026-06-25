# core/emailer.py
import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email                import encoders
from config import (GMAIL_USER, GMAIL_APP_PASS, APPLICANT_NAME,
                    APPLICANT_EMAIL, CV_PATH, EMAIL_SUBJECT_TEMPLATE)

def send_application(job: dict, cover_letter: str) -> bool:
    """
    Kirim email lamaran ke hiring email job tersebut.
    Return True jika berhasil.
    """
    to_email = job.get("email", "")
    if not to_email:
        print(f"[Email] Skip — no email for: {job['title']}")
        return False

    subject = EMAIL_SUBJECT_TEMPLATE.format(
        job_title=job["title"],
        applicant_name=APPLICANT_NAME
    )

    body = f"""Dear Hiring Team,

{cover_letter}

Please find my CV attached.

Best regards,
{APPLICANT_NAME}
{APPLICANT_EMAIL}
GitHub  : https://github.com/yourusername
Upwork  : https://upwork.com/freelancers/yourusername
LinkedIn: https://linkedin.com/in/yourusername
"""

    msg = MIMEMultipart()
    msg["From"]    = f"{APPLICANT_NAME} <{GMAIL_USER}>"
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach CV
    if os.path.exists(CV_PATH):
        with open(CV_PATH, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{APPLICANT_NAME.replace(" ","_")}_CV.pdf"'
            )
            msg.attach(part)
    else:
        print(f"[Email] Warning: CV file not found at {CV_PATH}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASS)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"[Email] ✓ Sent to {to_email} for: {job['title']}")
        return True
    except Exception as e:
        print(f"[Email] ✗ Failed: {e}")
        return False
