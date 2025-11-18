# accounts/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_otp_email(self, email, otp):
    """Send OTP using SMTP via Celery worker."""
    try:
        subject = "Your Verification Code"
        message = f"Your OTP is {otp}. It expires in 5 minutes."
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(
            subject,
            message,
            from_email,
            [email],
            fail_silently=False,
        )
        return "OTP email sent successfully."

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
