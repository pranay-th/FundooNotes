"""
Celery async tasks for email delivery.

Both tasks use bind=True so they can call self.retry() on failure,
with up to 3 retries and a 60-second delay between attempts.
"""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from loguru import logger


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email(self, email: str, token: str) -> None:
    """
    Send an account-verification email to the given address.

    Preconditions:
        - email is a valid email address string
        - token is a non-empty string (UUID or signed value)
    Postconditions:
        - Email dispatched via SMTP containing the verification URL
        - On SMTP failure: task retried up to 3 times (60 s apart)
        - On permanent failure after all retries: task marked as FAILED

    Args:
        email: Recipient email address.
        token: Single-use verification token stored in Redis.
    """
    try:
        verification_url = f"{settings.FRONTEND_URL}/verify-email/?token={token}"
        send_mail(
            subject="Verify your fundooNotes account",
            message=(
                f"Welcome to fundooNotes!\n\n"
                f"Please verify your email address by clicking the link below:\n"
                f"{verification_url}\n\n"
                f"This link expires in 1 hour."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {email}")
    except Exception as exc:
        logger.error(
            f"Failed to send verification email to {email} "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1}): {exc}"
        )
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, email: str, token: str) -> None:
    """
    Send a password-reset email to the given address.

    Preconditions:
        - email is a valid email address string
        - token is a non-empty string stored in Redis with TTL=3600
    Postconditions:
        - Email dispatched via SMTP containing the reset URL
        - On SMTP failure: task retried up to 3 times (60 s apart)
        - On permanent failure after all retries: task marked as FAILED

    Args:
        email: Recipient email address.
        token: Single-use password-reset token stored in Redis.
    """
    try:
        reset_url = f"{settings.FRONTEND_URL}/reset-password/?token={token}"
        send_mail(
            subject="Reset your fundooNotes password",
            message=(
                f"You requested a password reset for your fundooNotes account.\n\n"
                f"Click the link below to set a new password:\n"
                f"{reset_url}\n\n"
                f"This link expires in 1 hour. If you did not request this, "
                f"you can safely ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {email}")
    except Exception as exc:
        logger.error(
            f"Failed to send password reset email to {email} "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1}): {exc}"
        )
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_login_otp_email(self, email: str, otp: str) -> None:
    """
    Send a login OTP email to the given address.

    Preconditions:
        - email is a valid email address string
        - otp is a 6-digit string stored in Redis with TTL=300
    Postconditions:
        - Email dispatched via SMTP containing the OTP
        - On SMTP failure: task retried up to 3 times (60 s apart)
        - On permanent failure after all retries: task marked as FAILED

    Args:
        email: Recipient email address.
        otp: 6-digit one-time password.
    """
    try:
        send_mail(
            subject="Your fundooNotes login OTP",
            message=(
                f"Your one-time password (OTP) for logging into fundooNotes is:\n\n"
                f"  {otp}\n\n"
                f"This OTP expires in 5 minutes. Do not share it with anyone.\n"
                f"If you did not attempt to log in, please ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"Login OTP email sent to {email}")
    except Exception as exc:
        logger.error(
            f"Failed to send login OTP email to {email} "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1}): {exc}"
        )
        raise self.retry(exc=exc)


@shared_task
def dispatch_due_reminders() -> None:
    """
    Periodic task — runs every minute via Celery Beat.
    Finds all notes whose reminder_at is due (within the last minute) and
    not yet trashed, sends a reminder email to the note owner, then clears
    the reminder_at field so it doesn't fire again.
    """
    from django.utils import timezone
    from notes.models import Note

    now = timezone.now()
    window_start = now - timezone.timedelta(minutes=1)

    due_notes = Note.objects.filter(
        reminder_at__gte=window_start,
        reminder_at__lte=now,
        is_trashed=False,
    ).select_related("created_by")

    for note in due_notes:
        user = note.created_by
        try:
            send_mail(
                subject=f"Reminder: {note.title or 'Your note'}",
                message=(
                    f"Hi {user.username},\n\n"
                    f"This is your reminder for the note:\n\n"
                    f"  \"{note.title or 'Untitled'}\"\n\n"
                    f"{note.content[:500] if note.content else ''}\n\n"
                    f"Open FundooNotes to view it in full."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            logger.info(f"Reminder sent to {user.email} for note {note.id}")
        except Exception as exc:
            logger.error(f"Failed to send reminder for note {note.id}: {exc}")

        # Clear the reminder so it doesn't fire again
        note.reminder_at = None
        note.save(update_fields=["reminder_at"])
